# ModernCart

A complete, production-quality e-commerce store built with **Django**, **vanilla JavaScript**, and **pure CSS** — modern, minimal, premium, light-themed, and fully responsive.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Django](https://img.shields.io/badge/Django-5.0-092E20) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Home page** — hero section, featured products, categories, latest arrivals, newsletter, footer
- **Products page** — search, category filter, price range filter, sorting (newest / price / rating), pagination
- **Product detail page** — large image, rating, features, quantity selector, related products, breadcrumbs
- **Shopping cart** — persistent (DB-backed) cart for guests and logged-in users, AJAX quantity updates, empty-cart state
- **Checkout** — shipping details form, Cash on Delivery / Card (dummy) payment, protected behind login
- **Order success page** — order number, summary, confirmation
- **Authentication** — registration, login, logout, password validation, guest vs authenticated navbar
- **User dashboard** — profile summary, full order history with statuses
- **Admin panel** — manage products, categories, orders, and users; upload product images
- **15 sample products** auto-generated across 5 categories via a management command (or fixture)
- Fully responsive (desktop, laptop, tablet, mobile), custom 404 page, flash messages, CSRF protection

## 🛠 Tech Stack

**Frontend:** HTML5, CSS3 (pure, with CSS variables — no Bootstrap/Tailwind), Vanilla JavaScript, Google Fonts (Inter + Plus Jakarta Sans), Font Awesome icons

**Backend:** Django 5.0, SQLite, Django ORM, Django Authentication

## 📁 Project Structure

```
moderncart/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                  # created after migrate
├── moderncart/                 # project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── store/                      # main e-commerce app
│   ├── models.py                (Category, Product, Cart, CartItem, Order, OrderItem)
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── cart.py                  (session/user-aware cart helper)
│   ├── context_processors.py
│   ├── migrations/
│   ├── fixtures/products.json   (15 sample products)
│   └── management/commands/load_sample_products.py
├── accounts/                   # authentication & dashboard app
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── includes/ (navbar, footer, product_card)
│   ├── store/ (home, products, product_detail, cart, checkout, order_success)
│   ├── accounts/ (login, register, dashboard)
│   └── 404.html
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
└── media/
    └── products/                (15 generated product images)
```

## 🚀 Getting Started

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Load sample data (choose ONE method)

**Option A — management command (recommended, generates fresh placeholder images):**
```bash
python manage.py load_sample_products
```

**Option B — fixture (uses the pre-generated images already in `media/products/`):**
```bash
python manage.py loaddata products.json
```

### 5. Create an admin (superuser) account

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the store and **http://127.0.0.1:8000/admin/** for the Django admin panel.

## 🔑 Key URLs

| Page              | URL                       |
|-------------------|---------------------------|
| Home              | `/`                       |
| Products          | `/products/`              |
| Product detail    | `/product/<slug>/`        |
| Cart              | `/cart/`                  |
| Checkout          | `/checkout/` (login required) |
| Register          | `/accounts/register/`     |
| Login             | `/accounts/login/`        |
| Dashboard         | `/accounts/dashboard/` (login required) |
| Admin             | `/admin/`                 |

## 🖼 About the Sample Product Images

Since the store ships without any external/paid image assets, the 15 sample products use clean, on-brand **generated placeholder images** (Pillow), each showing the product's initials on a colored card that matches its category. To use your own photography, simply replace the images from the **Django Admin → Products → edit → Image** field — everything (thumbnails, detail page, cart, checkout, orders) updates automatically.

## 🗄 Database Models

- **Category** — `name`, `slug`, `icon`, `description`
- **Product** — `name`, `slug`, `category` (FK), `description`, `price`, `old_price`, `image`, `stock`, `rating`, `is_featured`, `is_active`
- **Cart** — one per user (or guest session), holds `CartItem`s
- **CartItem** — `cart` (FK), `product` (FK), `quantity`
- **Order** — `user` (FK), shipping fields, `payment_method`, `status`, `total_amount`, `order_number`
- **OrderItem** — `order` (FK), `product` (FK, snapshot), `price`, `quantity`

## 🔒 Security Notes

- CSRF protection on every POST form (cart, checkout, auth)
- `@login_required` on checkout, order success, and dashboard views
- Django's built-in password hashing & validators
- No hardcoded credentials — create your own superuser locally
- `SECRET_KEY` in `settings.py` is a development placeholder — replace it with an environment variable before deploying to production, and set `DEBUG = False` with a real `ALLOWED_HOSTS` list

## 📦 Deploying

Before going to production:
1. Set `DEBUG = False` in `moderncart/settings.py`
2. Move `SECRET_KEY` to an environment variable
3. Set `ALLOWED_HOSTS` to your real domain(s)
4. Run `python manage.py collectstatic`
5. Switch to a production database (PostgreSQL recommended) and a proper media storage backend (e.g. S3) for uploaded product images

## 📝 License

This project is provided as-is for learning and portfolio purposes.
