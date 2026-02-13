-- Robust SQL Fix for Master Ports
-- This drops and recreates the table to ensure correct column lengths

DROP TABLE IF EXISTS master_ports CASCADE;

CREATE TABLE master_ports (
    id SERIAL PRIMARY KEY,
    port_index_number INTEGER,
    region_name VARCHAR(255),
    main_port_name VARCHAR(255) NOT NULL,
    alternate_port_name VARCHAR(255),
    un_locode VARCHAR(50),
    country_code VARCHAR(100), -- Increased from 10
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    harbor_size VARCHAR(100),
    harbor_type VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ports_name ON master_ports(main_port_name);
CREATE INDEX idx_ports_country ON master_ports(country_code);
