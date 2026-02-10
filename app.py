from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory, session
)
from datetime import date, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import json

from config import Config
from utils.db import get_db
from utils.visitor_counter import track_visit
from utils.auth import login_required
from flask import Response

app = Flask(__name__, template_folder='templetes')
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

UPLOAD_FOLDER = "static/images/projects"
RESUME_FOLDER = "static/resume"
BLOGS_FOLDER = "static/images/blogs"
PROJECTS_FOLDER = UPLOAD_FOLDER

# ensure upload folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(BLOGS_FOLDER, exist_ok=True)

# Ensure blogs table exists (avoid OperationalError when DB hasn't been initialized)
try:
    db_conn = get_db()
    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            excerpt TEXT,
            content TEXT NOT NULL,
            image TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db_conn.commit()
    db_conn.close()
except Exception:
    # If get_db isn't available yet or DB cannot be opened, skip; init_db.py will create it.
    pass

# Ensure feedback table exists
try:
    db_conn = get_db()
    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            rating INTEGER NOT NULL,
            message TEXT,
            notify INTEGER DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db_conn.commit()
    db_conn.close()
except Exception:
    pass


# --------------------
# VISITOR TRACKING
# --------------------
@app.before_request
def track():
    if request.endpoint in ["home", "about", "portfolio", "resume", "contact", "experience", "blog", "terms", "privacy"]:
        track_visit(request.remote_addr)


# --------------------
# USER ROUTES
# --------------------
@app.route("/")
def home():
    return render_template("user/index.html")


@app.route("/about")
def about():
    return render_template("user/about.html")


@app.route("/portfolio")
def portfolio():
    db = get_db()
    projects = db.execute("SELECT * FROM projects").fetchall()
    return render_template("user/portfolio.html", projects=projects)


@app.route("/resume")
def resume():
    return render_template("user/resume.html")


@app.route("/download-resume")
def download_resume():
    return send_from_directory(RESUME_FOLDER, "resume.pdf", as_attachment=True)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO messages (name, email, phone, message) VALUES (?, ?, ?, ?)",
            (
                request.form["name"],
                request.form["email"],
                request.form["phone"],
                request.form["message"],
            ),
        )
        db.commit()
        return redirect(url_for("contact"))

    return render_template("user/contact.html")


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        db = get_db()
        name = request.form.get('name')
        email = request.form.get('email')
        rating = int(request.form.get('rating', 5))
        message = request.form.get('message') or ''
        notify = 1 if request.form.get('notify') == '1' else 0
        db.execute(
            'INSERT INTO feedback (name, email, rating, message, notify) VALUES (?, ?, ?, ?, ?)',
            (name, email, rating, message, notify),
        )
        db.commit()
        return redirect(url_for('feedback'))

    return render_template('user/feedback.html')


@app.route("/terms")
def terms():
    return render_template("user/terms.html")


@app.route("/privacy")
def privacy():
    return render_template("user/privacy.html")


@app.route("/experience")
def experience():
    return render_template("user/experience.html")


@app.route("/blog")
def blog():
    db = get_db()
    posts = db.execute("SELECT * FROM blogs ORDER BY created_at DESC").fetchall()
    return render_template("user/blog.html", posts=posts)


@app.route("/follow-journey")
def follow_journey():
    return render_template("user/follow-journey.html")


# --------------------
# ADMIN AUTH
# --------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        db = get_db()
        admin = db.execute(
            "SELECT * FROM admin WHERE username = ?",
            (request.form["username"],),
        ).fetchone()

        if admin and check_password_hash(admin["password"], request.form["password"]):
            session["admin_id"] = admin["id"]
            return redirect(url_for("admin_dashboard"))

    return render_template("admin/login.html")


# --------------------
# ADMIN BLOG MANAGEMENT
# --------------------
@app.route("/admin/blogs", methods=["GET", "POST"])
@login_required
def admin_blogs():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title")
        excerpt = request.form.get("excerpt")
        content = request.form.get("content")
        link = request.form.get("link") or ''
        image = request.files.get("image")
        filename = ''
        if image and image.filename:
            filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
            image_path = os.path.join(BLOGS_FOLDER, filename)
            image.save(image_path)

        db.execute(
            "INSERT INTO blogs (title, excerpt, content, image, link) VALUES (?, ?, ?, ?, ?)",
            (title, excerpt, content, filename, link),
        )
        db.commit()

    posts = db.execute("SELECT * FROM blogs ORDER BY created_at DESC").fetchall()
    return render_template("admin/blogs.html", posts=posts)


@app.route("/admin/blog/delete/<int:id>", methods=["POST"])
@login_required
def admin_delete_blog(id):
    db = get_db()
    if request.method == "POST":
        row = db.execute("SELECT image FROM blogs WHERE id = ?", (id,)).fetchone()
        if row and row[0]:
            try:
                img_path = os.path.join(BLOGS_FOLDER, row[0])
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass

        db.execute("DELETE FROM blogs WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for("admin_blogs"))


@app.route("/blog/<int:id>")
def blog_post(id):
    db = get_db()
    post = db.execute("SELECT * FROM blogs WHERE id = ?", (id,)).fetchone()
    if not post:
        return redirect(url_for("blog"))
    return render_template("user/blog_post.html", post=post)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# --------------------
# ADMIN DASHBOARD
# --------------------
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    db = get_db()

    messages = db.execute(
        "SELECT * FROM messages ORDER BY created_at DESC"
    ).fetchall()

    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        "total": db.execute("SELECT COUNT(*) FROM visits").fetchone()[0],
        "today": db.execute(
            "SELECT COUNT(*) FROM visits WHERE visit_date = ?",
            (today,),
        ).fetchone()[0],
        "week": db.execute(
            "SELECT COUNT(*) FROM visits WHERE visit_date >= ?",
            (week_ago,),
        ).fetchone()[0],
        "month": db.execute(
            "SELECT COUNT(*) FROM visits WHERE visit_date >= ?",
            (month_ago,),
        ).fetchone()[0],
    }

    return render_template(
        "admin/dashboard.html",
        messages=messages,
        stats=stats,
    )


@app.route("/admin/messages")
@login_required
def admin_messages():
    db = get_db()
    messages = db.execute("SELECT * FROM messages ORDER BY created_at DESC").fetchall()
    return render_template("admin/massages.html", messages=messages)


@app.route('/admin/notifications')
@login_required
def admin_notifications():
    db = get_db()
    rows = db.execute('SELECT * FROM feedback ORDER BY created_at DESC').fetchall()
    # Convert sqlite Row objects to dict-like for template
    feedbacks = [dict(row) for row in rows]
    return render_template('admin/notifications.html', feedbacks=feedbacks)


@app.route('/admin/notification/mark/<int:id>', methods=['POST'])
@login_required
def admin_notification_mark(id):
    db = get_db()
    row = db.execute('SELECT is_read FROM feedback WHERE id = ?', (id,)).fetchone()
    if row is None:
        return redirect(url_for('admin_notifications'))
    new_state = 0 if row['is_read'] else 1
    db.execute('UPDATE feedback SET is_read = ? WHERE id = ?', (new_state, id))
    db.commit()
    return redirect(url_for('admin_notifications'))


@app.route('/admin/notification/delete/<int:id>', methods=['POST'])
@login_required
def admin_notification_delete(id):
    db = get_db()
    db.execute('DELETE FROM feedback WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin_notifications'))


@app.route("/admin/message/delete/<int:id>", methods=["POST"])
@login_required
def admin_delete_message(id):
    db = get_db()
    # Only allow deletion via POST to prevent accidental deletes from GET
    if request.method == "POST":
        db.execute("DELETE FROM messages WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for("admin_messages"))


@app.route("/admin/analytics")
@login_required
def admin_analytics():
    db = get_db()
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    stats = {
        "total": db.execute("SELECT COUNT(*) FROM visits").fetchone()[0],
        "today": db.execute("SELECT COUNT(*) FROM visits WHERE visit_date = ?", (today,)).fetchone()[0],
        "week": db.execute("SELECT COUNT(*) FROM visits WHERE visit_date >= ?", (week_ago,)).fetchone()[0],
        "month": db.execute("SELECT COUNT(*) FROM visits WHERE visit_date >= ?", (month_ago,)).fetchone()[0],
    }
    return render_template("admin/analytics.html", stats=stats)


@app.route('/admin/stream-stats')
@login_required
def stream_stats():
    def event_stream():
        import time
        while True:
            db = get_db()
            today = date.today()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            stats = {
                'total': db.execute('SELECT COUNT(*) FROM visits').fetchone()[0],
                'today': db.execute('SELECT COUNT(*) FROM visits WHERE visit_date = ?', (today,)).fetchone()[0],
                'week': db.execute('SELECT COUNT(*) FROM visits WHERE visit_date >= ?', (week_ago,)).fetchone()[0],
                'month': db.execute('SELECT COUNT(*) FROM visits WHERE visit_date >= ?', (month_ago,)).fetchone()[0],
            }
            yield f"data: {json.dumps(stats)}\n\n"
            time.sleep(2)
    return Response(event_stream(), mimetype='text/event-stream')


# --------------------
# ADMIN PROJECT CRUD
# --------------------
@app.route("/admin/projects", methods=["GET", "POST"])
@login_required
def admin_projects():
    db = get_db()

    if request.method == "POST":
        image = request.files.get("image")
        filename = None
        if image:
            filename = secure_filename(image.filename)
            # prefix with uuid to avoid collisions
            filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

        db.execute(
            "INSERT INTO projects (title, description, image, link) VALUES (?, ?, ?, ?)",
            (
                request.form["title"],
                request.form["description"],
                filename or '',
                request.form["link"],
            ),
        )
        db.commit()

    projects = db.execute("SELECT * FROM projects").fetchall()
    return render_template("admin/projects.html", projects=projects)


@app.route("/admin/project/delete/<int:id>", methods=["POST"])
@login_required
def delete_project(id):
    db = get_db()
    if request.method == "POST":
        # Optionally remove the image file associated with the project
        row = db.execute("SELECT image FROM projects WHERE id = ?", (id,)).fetchone()
        if row and row[0]:
            try:
                img_path = os.path.join(PROJECTS_FOLDER, row[0])
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass

        db.execute("DELETE FROM projects WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for("admin_projects"))


# --------------------
# RESUME UPLOAD
# --------------------
@app.route("/admin/resume", methods=["GET", "POST"])
@login_required
def admin_resume():
    if request.method == "POST":
        resume = request.files["resume"]
        resume.save(os.path.join(RESUME_FOLDER, "resume.pdf"))
        return redirect(url_for("admin_resume"))

    return render_template("admin/resume_upload.html")


# --------------------
# RUN
# --------------------
if __name__ == "__main__":
    app.run(debug=True)
