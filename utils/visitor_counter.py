from datetime import date
from utils.db import get_db

def track_visit(ip):
    db = get_db()
    db.execute(
        "INSERT INTO visits (ip_address, visit_date) VALUES (?, ?)",
        (ip, date.today())
    )
    db.commit()
