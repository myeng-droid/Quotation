-- Final SQL Fix for Master Ports table
-- Run this to fix the column length issue

ALTER TABLE master_ports ALTER COLUMN country_code TYPE VARCHAR(100);
ALTER TABLE master_ports ALTER COLUMN un_locode TYPE VARCHAR(50);
ALTER TABLE master_ports ALTER COLUMN harbor_size TYPE VARCHAR(100);
ALTER TABLE master_ports ALTER COLUMN harbor_type TYPE VARCHAR(100);

-- Clear the table if needed to rerun migration
TRUNCATE TABLE master_ports;
