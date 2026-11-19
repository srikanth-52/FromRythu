<<<<<<< HEAD
# FromRythu (RYTHU_DIRECT)
### Farmer-to-Customer Direct Selling Marketplace

**FromRythu** is a full-stack web application built with **Python Django, MySQL (with PyMySQL & SQLite fallback), HTML5, CSS3, JavaScript, and Bootstrap 5**.

The platform eliminates middlemen, traders, and mandi commissions by connecting agricultural farmers (**Rythus**) directly with consumer households. Farmers get 100% fair trade autonomy over their crop prices, harvest inventory, and direct customer payments (UPI & Cash on Delivery), while consumers receive authentic, unadulterated, single-origin produce at lower prices.

---

## 🌟 The Three Portals

### 1. Farmer Portal (`/farmer/dashboard/`)
- **Dashboard Overview**: Real-time sales metrics, active produce, pending orders, revenue tracking, and low-stock alerts.
- **Add Fresh Harvest**: Register new produce with seed variety, harvest date, direct price, unit (kg, quintal, 25kg bag), organic tags, and field photos.
- **Manage Produce**: View, edit, hide/show, or modify listed farm produce.
- **Stock In / Stock Out**: Manage physical inventory with an inward/outward ledger, batch numbers, and audit trail.
- **Direct Price Control**: Modify selling prices on-the-fly with reasons for seasonal abundance or festival discounts, backed by a price history log.
- **Orders Received**: View buyer details, delivery addresses, update dispatch status (`Accepted` ➔ `Harvested & Packed` ➔ `Dispatched` ➔ `Delivered`).
- **Direct Customer Chat**: Message buyers directly regarding produce questions and bulk orders.
- **Sales Reports**: Crop-by-crop monetization analytics and gross revenue summaries with zero commission deducted.

### 2. Customer Portal (`/customer/dashboard/`)
- **Produce Catalog & Filtering**: Search and filter by crop category (Paddy, Pulses, Millets, Vegetables, Spices, Cotton), organic badge, price range, and harvest date.
- **Direct Traceability**: View exact farmer profile, farm name, district, farming technique, and harvest date on every product page.
- **Shopping Cart**: Real-time stock reservation, quantity adjustments, and auto-calculated delivery fees.
- **Checkout**: Seamless delivery address forms with choice of Cash on Delivery (COD) or Direct Farmer UPI / QR transfer.
- **Live Order Tracking**: Visual 5-step milestone tracking from farm harvest to doorstep delivery.
- **Chat with Farmers**: Ask growers questions directly from product pages or the messaging hub.
- **Verified Reviews**: Post reviews and star ratings on purchased harvests.

### 3. Admin Portal (`/admin-panel/dashboard/`)
- **System Metrics**: Total farmers, verified accounts, active customers, live produce count, and Platform GMV.
- **Farmer KYC & Approvals**: Review farmer credentials, farm land size (acres), and grant verified Rythu badges with one click.
- **Customer Oversight**: View registered households, order frequencies, and spending trends.
- **Produce & Price Audits**: Monitor marketplace-wide price updates and crop listings.
- **Inventory Logs**: Real-time unified stock ledger tracking all farm inward and outward movements.
- **Orders Supervision**: Track payment methods, delivery dispatches, and fulfillment rates.
- **Revenue & Crop Reports**: Category breakdown, top 10 best-selling produce items, and top-performing farmers.

---

## 📁 Complete Project Structure

```text
RYTHU_DIRECT/ (directsellfromfarmer)
│
├── manage.py                   # Django management entry point
├── requirements.txt            # Project dependencies
├── .env                        # Environment variables (DB, Secret Key, Debug)
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation
│
├── config/                     # Core Project Settings & Routing
│   ├── __init__.py             # PyMySQL initialization
│   ├── settings.py             # App definitions, DB config, Auth models
│   ├── urls.py                 # Central URL router
│   ├── views.py                # Home page & global redirects
│   ├── asgi.py                 # ASGI configuration
│   └── wsgi.py                 # WSGI configuration
│
├── accounts/                   # User Roles & Authentication
│   ├── models.py               # Custom User model (farmer, customer, admin)
│   ├── views.py                # Separate logins, registrations, and profile
│   ├── forms.py                # Registration and login forms
│   ├── permissions.py          # @farmer_required, @customer_required, @admin_required
│   ├── urls.py                 # /accounts/farmer-login/, customer-login/, etc.
│   ├── admin.py                # Custom UserAdmin
│   ├── tests.py                # Comprehensive test cases
│   └── management/
│       └── commands/
│           └── seed_data.py    # Database demo seeder command
│
├── farmers/                    # Farmer Profiles & Operations
│   ├── models.py               # FarmerProfile (farm size, crops, UPI, KYC)
│   ├── views.py                # Dashboard, add/manage produce, stock, price, orders, sales
│   ├── forms.py                # FarmerProfileForm, ProductForm, StockForm
│   ├── urls.py                 # /farmer/dashboard/, /farmer/stock/, etc.
│   └── admin.py                # FarmerProfileAdmin with approval actions
│
├── customers/                  # Customer Profiles & Views
│   ├── models.py               # CustomerProfile (delivery address, preferences)
│   ├── views.py                # Dashboard, order history, tracking, messages
│   ├── urls.py                 # /customer/dashboard/, /customer/my-orders/
│   └── admin.py                # CustomerProfileAdmin
│
├── products/                   # Catalog, Categories & Price History
│   ├── models.py               # Category, Product, PriceHistory, Review
│   ├── views.py                # Product catalog with filters & product details
│   ├── urls.py                 # /products/, /products/<slug>/
│   └── admin.py                # ProductAdmin, CategoryAdmin
│
├── inventory/                  # Stock Movement & Ledger
│   ├── models.py               # StockRecord (Stock In / Stock Out, batch, quantity)
│   ├── views.py                # Stock history API
│   ├── urls.py                 # /inventory/api/...
│   └── admin.py                # StockRecordAdmin
│
├── orders/                     # Shopping Cart, Orders & Order Items
│   ├── models.py               # Cart, CartItem, Order, OrderItem
│   ├── views.py                # Cart actions, checkout, order success, tracking
│   ├── forms.py                # CheckoutForm (shipping address, payment method)
│   ├── context_processors.py   # Global cart counter context processor
│   ├── urls.py                 # /orders/cart/, /orders/checkout/, etc.
│   └── admin.py                # OrderAdmin, OrderItemInline
│
├── messaging/                  # Real-Time Farmer-Customer Inquiries
│   ├── models.py               # Message model (sender, receiver, produce, content)
│   ├── views.py                # Send message dispatcher
│   ├── urls.py                 # /messaging/send/
│   └── admin.py                # MessageAdmin
│
├── payments/                   # Payment Records
│   ├── models.py               # Payment model (COD, UPI, Card, NetBanking)
│   ├── views.py                # Payment detail view
│   ├── urls.py                 # /payments/order/<order_number>/
│   └── admin.py                # PaymentAdmin
│
├── dashboard/                  # Central Role Dispatcher & Admin Panel
│   ├── views.py                # Admin dashboard, farmers, customers, inventory, reports
│   └── urls.py                 # /admin-panel/dashboard/, /admin-panel/farmers/, etc.
│
├── templates/                  # Frontend HTML Templates (Bootstrap 5)
│   ├── base.html               # Main navbar, footer, alerts, responsive shell
│   ├── home.html               # Landing page with hero, categories, featured produce
│   │
│   ├── accounts/
│   │   ├── farmer_login.html   # Farmer login portal
│   │   ├── customer_login.html # Customer login portal
│   │   ├── admin_login.html    # Administrator login portal
│   │   ├── unified_login.html  # Unified login
│   │   ├── register.html       # Role selection landing
│   │   ├── register_farmer.html# Farmer registration form
│   │   ├── register_customer.html# Customer sign up form
│   │   └── profile.html        # Profile settings & edit form
│   │
│   ├── farmer/
│   │   ├── sidebar.html        # Farmer portal sidebar partial
│   │   ├── dashboard.html      # Farmer metrics & quick orders
│   │   ├── add_product.html    # Add / edit produce form
│   │   ├── manage_products.html# Active harvest catalog
│   │   ├── stock.html          # Stock In / Stock Out ledger
│   │   ├── price.html          # Direct price control & history
│   │   ├── orders.html         # Customer orders received & status update
│   │   ├── messages.html       # Chat with buyers
│   │   └── sales_report.html   # Crop monetization reports
│   │
│   ├── customer/
│   │   ├── sidebar.html        # Customer dashboard sidebar partial
│   │   ├── dashboard.html      # Household orders & recommendations
│   │   ├── products.html       # Catalog with search, filters & sort
│   │   ├── product_details.html# Produce info, harvest date, farmer bio & reviews
│   │   ├── cart.html           # Cart table with quantity updates
│   │   ├── checkout.html       # Shipping address & payment choice
│   │   ├── my_orders.html      # Order history list
│   │   ├── order_detail.html   # Visual 5-step milestone tracking & invoice
│   │   ├── order_success.html  # Order confirmation celebration
│   │   └── messages.html       # Chat with farmers
│   │
│   └── admin_panel/
│       ├── sidebar.html        # Admin portal sidebar partial
│       ├── dashboard.html      # System stats & GMV metrics
│       ├── farmers.html        # Farmer KYC verification & approval
│       ├── customers.html      # Customer directory & spending
│       ├── products.html       # Catalog governance
│       ├── inventory.html      # Real-time stock audit ledger
│       ├── orders.html         # Platform orders supervision
│       ├── prices.html         # Price changes ledger
│       ├── messages.html       # Communication monitoring
│       └── reports.html        # Category sales & top farmers analytics
│
├── static/                     # Static Assets
│   ├── css/
│   │   ├── style.css           # Earthy agricultural design system
│   │   ├── dashboard.css       # Sidebar, metric cards, chat layout
│   │   └── responsive.css      # Mobile breakpoints
│   │
│   ├── js/
│   │   ├── main.js             # Bootstrap tooltips & auto-dismiss alerts
│   │   ├── cart.js             # Cart quantity adjustment
│   │   ├── stock.js            # Stock audit history modal fetcher
│   │   └── validation.js       # Bootstrap form validation
│   │
│   └── images/
│
├── media/                      # Uploaded files and crop photos
│   └── products/
│
└── database/
    └── schema.sql              # Complete MySQL DDL schema
```

---

## 🚀 Quick Start Guide (VS Code)

### 1. Open Project in VS Code
Open VS Code in this directory:
```bash
cd c:\Users\srikanth\Downloads\directsellfromfarmer
```

### 2. Activate Virtual Environment (or create one)
```bash
# If creating a fresh virtual environment:
python -m venv venv

# Activate in Windows PowerShell:
venv\Scripts\Activate.ps1
# or Command Prompt:
venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup (MySQL or SQLite)
The project is configured to work out-of-the-box with **SQLite** for instant zero-config development, and supports **MySQL** seamlessly via environment variables.

- **To run with SQLite (Default / Ready to Go)**:
  `.env` is already configured with `DB_ENGINE=sqlite3`.

- **To run with MySQL**:
  Update your `.env` file with your MySQL credentials:
  ```ini
  DB_ENGINE=mysql
  DB_NAME=rythu_direct_db
  DB_USER=root
  DB_PASSWORD=your_mysql_password
  DB_HOST=127.0.0.1
  DB_PORT=3306
  ```
  *(Make sure to run `CREATE DATABASE rythu_direct_db;` in MySQL first, or import `database/schema.sql`)*.

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Populate Realistic Demo Data
Run the built-in seed command to instantly populate admin, farmers, customers, categories, crops, stock, orders, and messages:
```bash
python manage.py seed_data
```

### 7. Run Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser!

### 8. Run Streamlit Interactive Data App & Analytics
An interactive Streamlit application connected directly to the Django backend is also included:
```bash
streamlit run streamlit_app.py
```
This opens **http://localhost:8501** featuring:
- 📊 **Executive Analytics & GMV Telemetry**: Interactive Plotly donut charts for Category Sales, best-selling harvests bar charts, and one-click Farmer KYC approval.
- 🌾 **Farmer Portal Simulation**: Switch between farmers, manage live physical stock, adjust prices on-the-fly, and update order dispatch milestones.
- 🛒 **Customer Marketplace**: Interactive produce catalog with instant one-click ordering and stock deduction.
- 💬 **Direct Messages Hub**: Live messaging between farmers and buyers.
- 🗄️ **Database Tables Explorer**: Live tabular view of all Django relational models.

---

## 🔑 Default Demo Login Credentials

| Role | Username | Password | Dashboard URL | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | `/admin-panel/dashboard/` | Full platform control & farmer approvals |
| **Farmer 1** | `farmer_ramesh` | `farmer123` | `/farmer/dashboard/` | Ramesh Reddy (Paddy, Toor Dal, Cotton) |
| **Farmer 2** | `farmer_venkat` | `farmer123` | `/farmer/dashboard/` | Venkat Rao (Foxtail Millet, Teja Chilli) |
| **Farmer 3** | `farmer_laxmi` | `farmer123` | `/farmer/dashboard/` | Laxmi Devi (Fresh Farm Tomatoes, Veggies) |
| **Customer 1** | `customer_anita` | `customer123` | `/customer/dashboard/` | Anita Sharma (Hitec City, Hyderabad) |
| **Customer 2** | `customer_rajesh` | `customer123` | `/customer/dashboard/` | Rajesh Kumar (Secunderabad) |

---

## 🧪 Running Automated Tests

Run the test suite to verify user roles, stock deductions, direct savings calculation, and cart checkout:
```bash
python manage.py test
```
All 4 test cases run and pass cleanly with `OK`.

---

## 🌐 Main URLs Mapping

| Page Name | URL Path | Access Level |
| :--- | :--- | :--- |
| **Home Page** | `/` | Public |
| **Farmer Portal Login** | `/accounts/farmer-login/` | Public |
| **Customer Portal Login** | `/accounts/customer-login/` | Public |
| **Admin Portal Login** | `/accounts/admin-login/` | Public / Staff |
| **Farmer Registration** | `/accounts/register/farmer/` | Public |
| **Customer Registration** | `/accounts/register/customer/` | Public |
| **Produce Catalog** | `/products/` | Public |
| **Farmer Dashboard** | `/farmer/dashboard/` | Farmer Only |
| **Farmer Stock Control** | `/farmer/stock/` | Farmer Only |
| **Farmer Price Management** | `/farmer/price/` | Farmer Only |
| **Customer Dashboard** | `/customer/dashboard/` | Customer Only |
| **Customer Cart** | `/orders/cart/` | Customer Only |
| **Customer Checkout** | `/orders/checkout/` | Customer Only |
| **Customer Orders & Tracking**| `/customer/my-orders/` | Customer Only |
| **Admin Dashboard** | `/admin-panel/dashboard/` | Admin Only |
| **Admin Farmer Approvals** | `/admin-panel/farmers/` | Admin Only |
| **Admin Reports & Analytics** | `/admin-panel/reports/` | Admin Only |
| **Django Native Admin** | `/admin/` | Staff Only |

=======
# FromRythu
>>>>>>> bc4c7fad09d02abcbe6485b61d7123100c30f68e
