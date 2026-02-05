-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Table: quotations (Transaction Header)
CREATE TABLE IF NOT EXISTS public.quotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_no TEXT NOT NULL,
    document_date DATE,
    status TEXT DEFAULT 'Draft',
    
    -- General Info
    trader_name TEXT,
    team TEXT,
    customer_importer_code TEXT,
    customer_end_user_code TEXT,
    incoterm TEXT,
    shipment_date_from DATE,
    shipment_date_to DATE,
    
    -- Financials & Exchange Rate
    currency TEXT,
    spot_rate NUMERIC(10,4),
    discount_rate NUMERIC(10,4),
    premium_rate NUMERIC(10,4),
    exchange_rate NUMERIC(10,4), -- Critical snapshot
    
    -- Interest Rates
    ar_interest_rate NUMERIC(5,2),
    ar_interest_days INTEGER,
    rm_interest_rate NUMERIC(5,2),
    rm_interest_days INTEGER,
    wh_storage_days INTEGER,

    -- Destinations
    destination_1 TEXT,
    destination_2 TEXT,
    destination_3 TEXT,
    destination_4 TEXT,
    
    -- Shipping Details
    container_size TEXT,
    container_qty INTEGER DEFAULT 1,
    invoice_qty INTEGER DEFAULT 1,
    ton_per_container NUMERIC(10,2),
    
    -- Costs
    freight_cost NUMERIC(15,2) DEFAULT 0,
    shipping_cost NUMERIC(15,2) DEFAULT 0,
    truck_cost NUMERIC(15,2) DEFAULT 0,
    
    survey_check_cost NUMERIC(15,2) DEFAULT 0,
    survey_vehicle_cost NUMERIC(15,2) DEFAULT 0,
    
    insurance_type TEXT,
    insurance_cost NUMERIC(15,2) DEFAULT 0,
    
    -- JSONB for fixed/standard export fees to keep schema clean
    -- Structure: { "thc": 2800, "seal": 300, "bl": 2000, "handling": 1000, "doc_prep": 5500, ... }
    fixed_export_expenses JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for searching
CREATE INDEX IF NOT EXISTS idx_quotations_doc_no ON public.quotations(document_no);


-- 2. Table: quotation_items (Section 4: Production Cost)
CREATE TABLE IF NOT EXISTS public.quotation_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.quotations(id) ON DELETE CASCADE,
    item_order INTEGER, -- 1 to 15
    
    product_name TEXT,
    product_rm_code TEXT,
    
    -- Cost Factors (Snapshots)
    rm_base_price NUMERIC(15,4) DEFAULT 0,
    
    overhead_group INTEGER, -- 0-6
    overhead_rate NUMERIC(10,4) DEFAULT 0, -- Snapshot
    yield_loss_pct NUMERIC(5,2) DEFAULT 0, -- Snapshot
    
    quantity NUMERIC(15,2) DEFAULT 0,
    
    -- Costs
    packaging_cost NUMERIC(15,4) DEFAULT 0,
    factory_expense_rate NUMERIC(10,4) DEFAULT 0, -- Snapshot
    
    -- Expenses
    commission NUMERIC(15,4) DEFAULT 0,
    ap_expense NUMERIC(15,4) DEFAULT 0,
    agreement_expense NUMERIC(15,4) DEFAULT 0,
    other_cost NUMERIC(15,4) DEFAULT 0,
    
    -- Selling
    brand TEXT,
    pack_size TEXT,
    selling_price NUMERIC(15,4) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quotation_items_qid ON public.quotation_items(quotation_id);


-- 3. Table: quotation_expenses (Section 2: Other Expenses List - 10 rows)
CREATE TABLE IF NOT EXISTS public.quotation_expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.quotations(id) ON DELETE CASCADE,
    item_no INTEGER, 
    description TEXT,
    amount NUMERIC(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quotation_expenses_qid ON public.quotation_expenses(quotation_id);


-- 4. Table: quotation_loadings (Loading Plan)
CREATE TABLE IF NOT EXISTS public.quotation_loadings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.quotations(id) ON DELETE CASCADE,
    order_no INTEGER,
    
    item_name TEXT,
    quantity_cartons INTEGER DEFAULT 0,
    weight_per_unit NUMERIC(10,2) DEFAULT 0,
    total_weight NUMERIC(15,2) DEFAULT 0,
    
    container_no TEXT,
    remark TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quotation_loadings_qid ON public.quotation_loadings(quotation_id);


-- 5. Table: quotation_remarks (Remarks - 20 lines)
CREATE TABLE IF NOT EXISTS public.quotation_remarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.quotations(id) ON DELETE CASCADE,
    order_no INTEGER,
    remark_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quotation_remarks_qid ON public.quotation_remarks(quotation_id);

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE public.quotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quotation_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quotation_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quotation_loadings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quotation_remarks ENABLE ROW LEVEL SECURITY;

-- Create Policy (Allow all for now, adjust based on auth needs)
CREATE POLICY "Enable all access for authenticated users" ON public.quotations FOR ALL USING (true);
CREATE POLICY "Enable all access for authenticated users" ON public.quotation_items FOR ALL USING (true);
CREATE POLICY "Enable all access for authenticated users" ON public.quotation_expenses FOR ALL USING (true);
CREATE POLICY "Enable all access for authenticated users" ON public.quotation_loadings FOR ALL USING (true);
CREATE POLICY "Enable all access for authenticated users" ON public.quotation_remarks FOR ALL USING (true);
