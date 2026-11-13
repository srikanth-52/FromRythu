-- =====================================================================
-- FromRythu (RYTHU_DIRECT) - Database Schema for MySQL
-- Farmer-to-Customer Direct Selling Marketplace
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `rythu_direct_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `rythu_direct_db`;

-- ---------------------------------------------------------------------
-- 1. USERS & AUTHENTICATION TABLE
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `accounts_user` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `password` VARCHAR(128) NOT NULL,
    `last_login` DATETIME(6) NULL,
    `is_superuser` TINYINT(1) NOT NULL DEFAULT 0,
    `username` VARCHAR(150) NOT NULL UNIQUE,
    `first_name` VARCHAR(150) NOT NULL DEFAULT '',
    `last_name` VARCHAR(150) NOT NULL DEFAULT '',
    `email` VARCHAR(254) NOT NULL DEFAULT '',
    `is_staff` TINYINT(1) NOT NULL DEFAULT 0,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `date_joined` DATETIME(6) NOT NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'customer',
    `phone_number` VARCHAR(15) NULL,
    `address` LONGTEXT NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `pincode` VARCHAR(10) NULL,
    `profile_picture` VARCHAR(100) NULL,
    `is_verified` TINYINT(1) NOT NULL DEFAULT 0,
    INDEX `idx_user_role` (`role`),
    INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 2. FARMER PROFILES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `farmers_farmerprofile` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL UNIQUE,
    `farm_name` VARCHAR(200) NOT NULL,
    `farm_location` VARCHAR(255) NOT NULL,
    `village` VARCHAR(100) NULL,
    `mandal` VARCHAR(100) NULL,
    `district` VARCHAR(100) NULL,
    `state` VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    `farm_size_acres` DECIMAL(6,2) NOT NULL DEFAULT 2.00,
    `primary_crops` VARCHAR(255) NOT NULL,
    `farming_experience_years` INT UNSIGNED NOT NULL DEFAULT 5,
    `farming_type` VARCHAR(50) NOT NULL DEFAULT 'Organic',
    `aadhaar_or_id` VARCHAR(30) NULL,
    `id_document` VARCHAR(100) NULL,
    `bank_name` VARCHAR(100) NULL,
    `bank_account_no` VARCHAR(50) NULL,
    `ifsc_code` VARCHAR(20) NULL,
    `upi_id` VARCHAR(60) NULL,
    `is_approved` TINYINT(1) NOT NULL DEFAULT 0,
    `bio` LONGTEXT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_farmer_user` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 3. CUSTOMER PROFILES
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `customers_customerprofile` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL UNIQUE,
    `default_delivery_address` LONGTEXT NULL,
    `landmark` VARCHAR(150) NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    `pincode` VARCHAR(10) NULL,
    `alternate_phone` VARCHAR(15) NULL,
    `dietary_preference` VARCHAR(50) NULL DEFAULT 'Direct Farm Fresh',
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_customer_user` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 4. PRODUCT CATEGORIES & PRODUCTS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `products_category` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(120) NOT NULL UNIQUE,
    `slug` VARCHAR(140) NOT NULL UNIQUE,
    `icon_class` VARCHAR(50) NOT NULL DEFAULT 'bi-basket',
    `image` VARCHAR(100) NULL,
    `description` LONGTEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `products_product` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `farmer_id` BIGINT NOT NULL,
    `category_id` BIGINT NULL,
    `name` VARCHAR(200) NOT NULL,
    `slug` VARCHAR(220) NOT NULL UNIQUE,
    `variety` VARCHAR(100) NULL,
    `description` LONGTEXT NOT NULL,
    `harvest_date` DATE NULL,
    `unit` VARCHAR(30) NOT NULL DEFAULT 'kg',
    `price_per_unit` DECIMAL(10,2) NOT NULL,
    `mrp` DECIMAL(10,2) NULL,
    `min_order_quantity` DECIMAL(6,2) NOT NULL DEFAULT 1.00,
    `is_organic` TINYINT(1) NOT NULL DEFAULT 1,
    `image` VARCHAR(100) NULL,
    `image_url_fallback` VARCHAR(500) NULL,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `featured` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_product_farmer` FOREIGN KEY (`farmer_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_product_category` FOREIGN KEY (`category_id`) REFERENCES `products_category` (`id`) ON DELETE SET NULL,
    INDEX `idx_product_active` (`is_active`),
    INDEX `idx_product_price` (`price_per_unit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `products_pricehistory` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `product_id` BIGINT NOT NULL,
    `old_price` DECIMAL(10,2) NOT NULL,
    `new_price` DECIMAL(10,2) NOT NULL,
    `reason` VARCHAR(255) NULL,
    `changed_by_id` BIGINT NULL,
    `created_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_price_product` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_price_user` FOREIGN KEY (`changed_by_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `products_review` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `product_id` BIGINT NOT NULL,
    `customer_id` BIGINT NOT NULL,
    `rating` SMALLINT UNSIGNED NOT NULL DEFAULT 5,
    `comment` LONGTEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_review_product` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_review_customer` FOREIGN KEY (`customer_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 5. INVENTORY & STOCK TRANSACTIONS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `inventory_stockrecord` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `product_id` BIGINT NOT NULL,
    `transaction_type` VARCHAR(10) NOT NULL DEFAULT 'IN',
    `quantity` DECIMAL(10,2) NOT NULL,
    `batch_no` VARCHAR(60) NULL,
    `notes` LONGTEXT NULL,
    `created_by_id` BIGINT NULL,
    `created_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_stock_product` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_stock_user` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL,
    INDEX `idx_stock_tx_type` (`transaction_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 6. CARTS & CART ITEMS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `orders_cart` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL UNIQUE,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_cart_customer` FOREIGN KEY (`customer_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `orders_cartitem` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `cart_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `quantity` DECIMAL(8,2) NOT NULL DEFAULT 1.00,
    `added_at` DATETIME(6) NOT NULL,
    UNIQUE KEY `unique_cart_product` (`cart_id`, `product_id`),
    CONSTRAINT `fk_cartitem_cart` FOREIGN KEY (`cart_id`) REFERENCES `orders_cart` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cartitem_product` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 7. ORDERS & ORDER ITEMS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `orders_order` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `order_number` VARCHAR(50) NOT NULL UNIQUE,
    `customer_id` BIGINT NOT NULL,
    `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    `delivery_fee` DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    `final_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `payment_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `shipping_full_name` VARCHAR(150) NOT NULL,
    `shipping_phone` VARCHAR(20) NOT NULL,
    `shipping_address` LONGTEXT NOT NULL,
    `shipping_city` VARCHAR(100) NOT NULL,
    `shipping_state` VARCHAR(100) NOT NULL DEFAULT 'Telangana',
    `shipping_pincode` VARCHAR(10) NOT NULL,
    `delivery_instructions` LONGTEXT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_order_customer` FOREIGN KEY (`customer_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
    INDEX `idx_order_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `orders_orderitem` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `order_id` BIGINT NOT NULL,
    `product_id` BIGINT NULL,
    `farmer_id` BIGINT NOT NULL,
    `product_name` VARCHAR(200) NOT NULL,
    `unit` VARCHAR(30) NOT NULL,
    `unit_price` DECIMAL(10,2) NOT NULL,
    `quantity` DECIMAL(8,2) NOT NULL,
    `subtotal` DECIMAL(12,2) NOT NULL,
    `item_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    CONSTRAINT `fk_item_order` FOREIGN KEY (`order_id`) REFERENCES `orders_order` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_item_product` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_item_farmer` FOREIGN KEY (`farmer_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 8. PAYMENTS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `payments_payment` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `order_id` BIGINT NOT NULL UNIQUE,
    `payment_method` VARCHAR(20) NOT NULL DEFAULT 'COD',
    `transaction_id` VARCHAR(100) NULL,
    `amount` DECIMAL(12,2) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `payment_notes` LONGTEXT NULL,
    `paid_at` DATETIME(6) NULL,
    `created_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_payment_order` FOREIGN KEY (`order_id`) REFERENCES `orders_order` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 9. MESSAGING & CHAT
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `messaging_message` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `sender_id` BIGINT NOT NULL,
    `receiver_id` BIGINT NOT NULL,
    `product_id` BIGINT NULL,
    `order_id` BIGINT NULL,
    `subject` VARCHAR(200) NULL,
    `content` LONGTEXT NOT NULL,
    `is_read` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL,
    CONSTRAINT `fk_msg_sender` FOREIGN KEY (`sender_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_msg_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `accounts_user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_msg_product` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_msg_order` FOREIGN KEY (`order_id`) REFERENCES `orders_order` (`id`) ON DELETE SET NULL,
    INDEX `idx_msg_unread` (`receiver_id`, `is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

