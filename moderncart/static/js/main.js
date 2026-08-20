/* =========================================================
   ModernCart — Global JavaScript
   Handles: navbar toggle, quantity steppers, AJAX cart
   updates, flash message auto-dismiss, form validation,
   smooth scrolling and small UI animations.
   ========================================================= */

document.addEventListener('DOMContentLoaded', function () {
    initNavbarToggle();
    initQuantitySteppers();
    initCartQuantityAjax();
    initAutoDismissMessages();
    initSmoothScroll();
    initCheckoutValidation();
    initRegisterValidation();
    initScrollReveal();
});

/* ---------------- Utility: read CSRF token from cookie ---------------- */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const CSRF_TOKEN = getCookie('csrftoken');

/* ---------------- Responsive hamburger navbar ---------------- */
function initNavbarToggle() {
    const toggle = document.getElementById('navbarToggle');
    const links = document.getElementById('navbarLinks');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
        links.classList.toggle('open');
        const icon = toggle.querySelector('i');
        if (links.classList.contains('open')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-xmark');
        } else {
            icon.classList.remove('fa-xmark');
            icon.classList.add('fa-bars');
        }
    });

    // Close menu when a link is clicked (mobile)
    links.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            links.classList.remove('open');
        });
    });
}

/* ---------------- Quantity +/- steppers (product detail & cart) ---------------- */
function initQuantitySteppers() {
    document.querySelectorAll('.quantity-selector').forEach(function (selector) {
        const minusBtn = selector.querySelector('.qty-minus');
        const plusBtn = selector.querySelector('.qty-plus');
        const input = selector.querySelector('.qty-input');
        if (!input) return;

        const max = parseInt(input.getAttribute('max')) || 999;

        minusBtn && minusBtn.addEventListener('click', function () {
            let value = parseInt(input.value) || 1;
            if (value > 1) {
                input.value = value - 1;
                input.dispatchEvent(new Event('change'));
            }
        });

        plusBtn && plusBtn.addEventListener('click', function () {
            let value = parseInt(input.value) || 1;
            if (value < max) {
                input.value = value + 1;
                input.dispatchEvent(new Event('change'));
            }
        });
    });
}

/* ---------------- AJAX cart quantity updates on the cart page ---------------- */
function initCartQuantityAjax() {
    document.querySelectorAll('.cart-qty-input').forEach(function (input) {
        input.addEventListener('change', function () {
            const form = input.closest('.qty-form');
            const cartItem = input.closest('.cart-item');
            const productId = cartItem.dataset.productId;
            const price = parseFloat(cartItem.querySelector('.cart-item-price').dataset.price);
            const quantity = parseInt(input.value) || 1;

            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'quantity=' + quantity,
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    const subtotal = (price * quantity).toFixed(2);
                    cartItem.querySelector('.cart-item-subtotal').textContent = '₹' + subtotal;
                    updateCartTotals();
                    updateNavbarBadge(data.cart_count);
                }
            })
            .catch(function () {
                // Fail silently in the UI; the form still works without JS via page reload.
            });
        });
    });
}

function updateCartTotals() {
    let subtotal = 0;
    document.querySelectorAll('.cart-item').forEach(function (item) {
        const price = parseFloat(item.querySelector('.cart-item-price').dataset.price);
        const qty = parseInt(item.querySelector('.cart-qty-input').value) || 1;
        subtotal += price * qty;
    });
    const subtotalEl = document.getElementById('cartSubtotal');
    const totalEl = document.getElementById('cartTotal');
    if (subtotalEl) subtotalEl.textContent = '₹' + subtotal.toFixed(2);
    if (totalEl) totalEl.textContent = '₹' + subtotal.toFixed(2);
}

function updateNavbarBadge(count) {
    document.querySelectorAll('.cart-badge').forEach(function (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    });
}

/* ---------------- Auto-dismiss flash messages ---------------- */
function initAutoDismissMessages() {
    document.querySelectorAll('.flash-message').forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(function () { msg.remove(); }, 400);
        }, 5000);
    });
}

/* ---------------- Smooth scrolling for in-page anchor links ---------------- */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId.length > 1) {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
}

/* ---------------- Checkout form client-side validation ---------------- */
function initCheckoutValidation() {
    const form = document.querySelector('.checkout-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        let valid = true;
        const requiredFields = form.querySelectorAll('input[required], input[name="full_name"], input[name="email"], input[name="phone"], input[name="address"], input[name="city"], input[name="state"], input[name="zip_code"]');

        requiredFields.forEach(function (field) {
            clearFieldError(field);
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required.');
                valid = false;
            }
        });

        const emailField = form.querySelector('input[name="email"]');
        if (emailField && emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
            showFieldError(emailField, 'Please enter a valid email address.');
            valid = false;
        }

        if (!valid) {
            e.preventDefault();
        } else {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner"></span> Placing Order...';
                submitBtn.disabled = true;
            }
        }
    });
}

function showFieldError(field, message) {
    field.style.borderColor = '#EF4444';
    let error = field.parentElement.querySelector('.js-field-error');
    if (!error) {
        error = document.createElement('span');
        error.className = 'field-error js-field-error';
        field.parentElement.appendChild(error);
    }
    error.textContent = message;
}

function clearFieldError(field) {
    field.style.borderColor = '';
    const error = field.parentElement.querySelector('.js-field-error');
    if (error) error.remove();
}

/* ---------------- Register form password match validation ---------------- */
function initRegisterValidation() {
    const form = document.querySelector('.auth-form');
    const pass1 = document.querySelector('#id_password1');
    const pass2 = document.querySelector('#id_password2');
    if (!form || !pass1 || !pass2) return;

    form.addEventListener('submit', function (e) {
        clearFieldError(pass2);
        if (pass1.value !== pass2.value) {
            showFieldError(pass2, 'Passwords do not match.');
            e.preventDefault();
        }
    });
}

/* ---------------- Simple scroll-reveal animation for cards ---------------- */
function initScrollReveal() {
    const targets = document.querySelectorAll('.product-card, .category-card');
    if (!('IntersectionObserver' in window) || targets.length === 0) return;

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.5s ease both';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    targets.forEach(function (el) { observer.observe(el); });
}

/* ---------------- Sticky navbar shadow on scroll ---------------- */
window.addEventListener('scroll', function () {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;
    if (window.scrollY > 10) {
        navbar.style.boxShadow = '0 4px 16px rgba(17,24,39,0.06)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});
