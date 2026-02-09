// Admin Panel JavaScript - Interactivity & Animations

document.addEventListener('DOMContentLoaded', function() {
    // Set active menu item based on current page
    setActiveMenuItem();

    // Add animations to visible elements
    animateOnScroll();

    // Handle form submissions
    setupFormHandlers();

    // Setup mobile sidebar toggle
    setupMobileMenu();

    // Add real-time stat animations
    setupStatAnimations();
});

// Set active menu item
function setActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.sidebar-menu a');

    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        
        // Check if current path matches the menu item href
        if (href && currentPath.includes(href.replace(/^\//, ''))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Animate elements on scroll
function animateOnScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.5s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    // Observe stat cards, tables, and forms
    document.querySelectorAll('.stat-card, .table-container, .form-container').forEach(el => {
        observer.observe(el);
    });
}

// Setup form handlers
function setupFormHandlers() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (submitBtn) {
                // Add loading state
                submitBtn.tempText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span>Processing...</span>';

                // Reset after submission
                setTimeout(() => {
                    submitBtn.innerHTML = submitBtn.tempText;
                    submitBtn.disabled = false;
                }, 1000);
            }
        });

        // Real-time input validation feedback
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });

            input.addEventListener('focus', function() {
                this.classList.remove('input-error');
            });
        });
    });
}

// Validate input fields
function validateInput(input) {
    let isValid = true;

    if (input.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = emailRegex.test(input.value);
    } else if (input.type === 'url') {
        try {
            new URL(input.value);
        } catch (e) {
            isValid = false;
        }
    } else if (input.required) {
        isValid = input.value.trim().length > 0;
    }

    if (!isValid) {
        input.classList.add('input-error');
    } else {
        input.classList.remove('input-error');
    }

    return isValid;
}

// Setup mobile menu toggle
function setupMobileMenu() {
    const windowWidth = window.innerWidth;

    if (windowWidth <= 768) {
        // Create toggle button if it doesn't exist
        const topbar = document.querySelector('.admin-topbar');
        const sidebar = document.querySelector('.admin-sidebar-nav');

        if (topbar && sidebar && !document.querySelector('.menu-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'menu-toggle';
            toggleBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
            toggleBtn.setAttribute('aria-label', 'Toggle menu');
            topbar.insertAdjacentElement('afterbegin', toggleBtn);

            toggleBtn.addEventListener('click', function() {
                sidebar.classList.toggle('mobile-open');
                this.classList.toggle('active');
            });

            // Close menu when clicking a menu item
            sidebar.querySelectorAll('.menu-item a').forEach(link => {
                link.addEventListener('click', function() {
                    sidebar.classList.remove('mobile-open');
                    toggleBtn.classList.remove('active');
                });
            });

            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                    sidebar.classList.remove('mobile-open');
                    toggleBtn.classList.remove('active');
                }
            });
        }
    }
}

// Animate stat values with counter effect
function setupStatAnimations() {
    const statValues = document.querySelectorAll('.stat-value');

    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        
        if (!isNaN(finalValue)) {
            const startValue = 0;
            const increment = Math.ceil(finalValue / 30); // Animate over ~30 steps
            let currentValue = startValue;

            const counter = setInterval(() => {
                currentValue += increment;
                
                if (currentValue >= finalValue) {
                    stat.textContent = finalValue;
                    clearInterval(counter);
                } else {
                    stat.textContent = currentValue;
                }
            }, 30);

            // Only animate on initial load or when stat refreshes
            stat.addEventListener('animationstart', function() {
                // Reset animation
                clearInterval(counter);
                currentValue = startValue;
                
                const newCounter = setInterval(() => {
                    currentValue += increment;
                    
                    if (currentValue >= finalValue) {
                        stat.textContent = finalValue;
                        clearInterval(newCounter);
                    } else {
                        stat.textContent = currentValue;
                    }
                }, 30);
            });
        }
    });
}

// Delete confirmation dialog
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Toast notification (optional)
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fa-solid fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // Animation
    setTimeout(() => notification.classList.add('show'), 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Real-time dropdown menu handler
document.addEventListener('click', function(e) {
    // Close dropdowns when clicking outside
    if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

// Add input-error styles to admin.css via JavaScript if not present
window.addEventListener('load', function() {
    const style = document.createElement('style');
    style.textContent = `
        .input-error {
            border-color: #ef4444 !important;
            background: rgba(239, 68, 68, 0.1) !important;
        }

        .menu-toggle {
            display: none;
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 24px;
            cursor: pointer;
            padding: 10px;
            transition: var(--transition);
        }

        @media (max-width: 768px) {
            .menu-toggle {
                display: flex;
                align-items: center;
            }

            .admin-sidebar-nav {
                position: fixed;
                left: -260px;
                top: 70px;
                height: calc(100vh - 70px);
                z-index: 98;
                transition: left 0.3s ease;
            }

            .admin-sidebar-nav.mobile-open {
                left: 0;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            }
        }

        .notification {
            position: fixed;
            bottom: -100px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transition: bottom 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            max-width: 300px;
        }

        .notification.show {
            bottom: 20px;
        }

        .notification-error {
            background: var(--danger-color);
        }

        .notification-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
    `;
    document.head.appendChild(style);
});

// Export functions for use in other scripts
window.AdminPanel = {
    confirmDelete,
    showNotification
};
