-- Supabase Schema for Quotation App Master Data (UPDATED)
-- Run this in Supabase SQL Editor to update the tables

-- Drop existing tables if you want to recreate them
-- DROP TABLE IF EXISTS master_customers CASCADE;
-- DROP TABLE IF EXISTS master_currencies CASCADE;
-- DROP TABLE IF EXISTS master_ports CASCADE;
-- DROP TABLE IF EXISTS master_overhead CASCADE;
-- DROP TABLE IF EXISTS master_factory_expense CASCADE;
-- DROP TABLE IF EXISTS master_yield_loss CASCADE;

-- Table: master_customers
CREATE TABLE IF NOT EXISTS master_customers (
    id SERIAL PRIMARY KEY,
    company_code VARCHAR(10),
    customer_code VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_address TEXT,
    country VARCHAR(100),
    payment_term_customer VARCHAR(50),
    payment_term_customer_name VARCHAR(255),
    hold_shipment BOOLEAN DEFAULT FALSE,
    payment_term_custcomp VARCHAR(50),
    payment_term_custcomp_name VARCHAR(255),
    credit_limit_custcomp DECIMAL(18,2),
    bl_date DATE,
    document_no VARCHAR(100),
    org_code VARCHAR(50),
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: master_currencies
CREATE TABLE IF NOT EXISTS master_currencies (
    id SERIAL PRIMARY KEY,
    sequence_no INTEGER,
    code VARCHAR(10) NOT NULL,
    currency_name VARCHAR(100),
    symbol VARCHAR(10),
    is_base_currency BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: master_ports (UPDATED - changed country_code to VARCHAR(50))
CREATE TABLE IF NOT EXISTS master_ports (
    id SERIAL PRIMARY KEY,
    port_index_number INTEGER,
    region_name VARCHAR(255),
    main_port_name VARCHAR(255) NOT NULL,
    alternate_port_name VARCHAR(255),
    un_locode VARCHAR(20),
    country_code VARCHAR(50),  -- Changed from VARCHAR(10)
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    harbor_size VARCHAR(50),
    harbor_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: master_overhead
CREATE TABLE IF NOT EXISTS master_overhead (
    id SERIAL PRIMARY KEY,
    group_number INTEGER NOT NULL UNIQUE,
    overhead_rate DECIMAL(10,4),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: master_factory_expense (UPDATED - simplified)
CREATE TABLE IF NOT EXISTS master_factory_expense (
    id SERIAL PRIMARY KEY,
    expense_rate DECIMAL(10,4),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: master_yield_loss
CREATE TABLE IF NOT EXISTS master_yield_loss (
    id SERIAL PRIMARY KEY,
    group_number INTEGER NOT NULL,
    yield_loss_percent DECIMAL(10,4),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: shipping_rates
CREATE TABLE IF NOT EXISTS shipping_rates (
    id SERIAL PRIMARY KEY,
    min_qty INTEGER NOT NULL,
    max_qty INTEGER NOT NULL,
    price_per_container DECIMAL(18,2) NOT NULL,
    unit VARCHAR(50),
    description_th TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_customers_code ON master_customers(customer_code);
CREATE INDEX IF NOT EXISTS idx_customers_name ON master_customers(customer_name);
CREATE INDEX IF NOT EXISTS idx_ports_name ON master_ports(main_port_name);
CREATE INDEX IF NOT EXISTS idx_ports_country ON master_ports(country_code);
CREATE INDEX IF NOT EXISTS idx_overhead_group ON master_overhead(group_number);
CREATE INDEX IF NOT EXISTS idx_yield_loss_group ON master_yield_loss(group_number);

-- If you need to alter existing port table:
-- ALTER TABLE master_ports ALTER COLUMN country_code TYPE VARCHAR(50);
