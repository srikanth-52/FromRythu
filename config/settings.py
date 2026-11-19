
from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

# ==================================================
# BASE DIRECTORY
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ==================================================
# SECURITY
# ==================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-local-development-only-key"
)

DEBUG = os.getenv("DEBUG", "False").strip().lower() in (
    "true", "1", "yes"
)

# Always allow local development and Vercel domains.
# A leading dot allows both the root domain and subdomains.
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".vercel.app",
    "from-rythu.vercel.app",
]

# Add extra hosts without replacing the defaults.
extra_hosts = os.getenv("ALLOWED_HOSTS", "")

ALLOWED_HOSTS.extend(
    host.strip()
    for host in extra_hosts.split(",")
    if host.strip()
)

ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))

CSRF_TRUSTED_ORIGINS = [
    "https://from-rythu.vercel.app",
    "https://*.vercel.app",
]

extra_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")

CSRF_TRUSTED_ORIGINS.extend(
    origin.strip()
    for origin in extra_origins.split(",")
    if origin.strip()
)

CSRF_TRUSTED_ORIGINS = list(set(CSRF_TRUSTED_ORIGINS))

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https"
    )
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ==================================================
# APPLICATIONS
# ==================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts.apps.AccountsConfig",
    "farmers.apps.FarmersConfig",
    "customers.apps.CustomersConfig",
    "products.apps.ProductsConfig",
    "inventory.apps.InventoryConfig",
    "orders.apps.OrdersConfig",
    "messaging.apps.MessagingConfig",
    "payments.apps.PaymentsConfig",
    "dashboard.apps.DashboardConfig",
]

# ==================================================
# MIDDLEWARE
# ==================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==================================================
# URL CONFIGURATION
# ==================================================

ROOT_URLCONF = "config.urls"

# ==================================================
# TEMPLATES
# ==================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "orders.context_processors.cart_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ==================================================
# DATABASE
# Production: Supabase PostgreSQL
# Local: MySQL or SQLite
# ==================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,
            ssl_require=True,
        )
    }

elif not DEBUG:
    raise ValueError(
        "DATABASE_URL is missing. "
        "Configure Supabase PostgreSQL in Vercel."
    )

elif os.getenv("DB_ENGINE", "sqlite3").lower() == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "rythu_direct_db"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "charset": "utf8mb4",
            },
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==================================================
# CUSTOM USER MODEL
# ==================================================

AUTH_USER_MODEL = "accounts.User"

# ==================================================
# PASSWORD VALIDATION
# ==================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

# ==================================================
# INTERNATIONALIZATION
# ==================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True
USE_TZ = True

# ==================================================
# STATIC FILES
# ==================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# ==================================================
# MEDIA FILES
# ==================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ==================================================
# DEFAULT PRIMARY KEY
# ==================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==================================================
# LOGIN / LOGOUT
# ==================================================

LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "dashboard:role_redirect"

LOGOUT_REDIRECT_URL = "home"

# ==================================================
# MESSAGE TAGS
# ==================================================

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}
