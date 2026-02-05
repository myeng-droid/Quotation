-- Database Migration Script (Doc-Aligned)
-- Structure matches the 5 Excel files in Doc/ folder

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Table: trx_general_infos
-- Source: Doc/General Data.xlsx
CREATE TABLE IF NOT EXISTS public.trx_general_infos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_no TEXT NOT NULL UNIQUE,
    doc_date DATE,
    trader_name TEXT,
    team TEXT,
    customer_importer TEXT,
    customer_end_user TEXT,
    incoterm TEXT,
    ship_date_from DATE,
    ship_date_to DATE,
    
    currency TEXT,
    spot_rate DECIMAL(10,4),
    discount_rate DECIMAL(10,4),
    premium_rate DECIMAL(10,4),
    exchange_rate DECIMAL(10,4),
    
    dest_1 TEXT,
    dest_2 TEXT,
    dest_3 TEXT,
    dest_4 TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gen_doc_no ON public.trx_general_infos(doc_no);


-- 2. Table: trx_export_expenses
-- Source: Doc/Export Expense .xlsx
CREATE TABLE IF NOT EXISTS public.trx_export_expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.trx_general_infos(id) ON DELETE CASCADE,
    
    -- Container Info
    container_size TEXT,
    container_qty INTEGER,
    invoice_qty INTEGER,
    ton_per_container DECIMAL(10,2),
    
    -- Expenses
    freight_cost DECIMAL(15,2),
    shipping_cost DECIMAL(15,2),
    truck_cost DECIMAL(15,2),
    survey_check_cost DECIMAL(15,2),
    survey_vehicle_cost DECIMAL(15,2),
    insurance_cost DECIMAL(15,2),
    
    -- Port Fees
    thc_cost DECIMAL(15,2),
    seal_cost DECIMAL(15,2),
    bl_fee DECIMAL(15,2),
    handling_fee DECIMAL(15,2),
    
    -- Document Fees
    doc_prep_fee DECIMAL(15,2),
    doc_agri_fee DECIMAL(15,2),
    doc_phyto_fee DECIMAL(15,2),
    doc_health_fee DECIMAL(15,2),
    doc_origin_fee DECIMAL(15,2),
    doc_ms24_fee DECIMAL(15,2),
    doc_chamber_fee DECIMAL(15,2),
    doc_dft_fee DECIMAL(15,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exp_qid ON public.trx_export_expenses(quotation_id);


-- 3. Table: trx_interests
-- Source: Doc/Interest .xlsx
CREATE TABLE IF NOT EXISTS public.trx_interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.trx_general_infos(id) ON DELETE CASCADE,
    
    payment_term_auto TEXT,
    payment_term_ship TEXT,
    
    ar_rate DECIMAL(5,2),
    ar_days INTEGER,
    rm_rate DECIMAL(5,2),
    rm_days INTEGER,
    wh_days INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_int_qid ON public.trx_interests(quotation_id);


-- 4. Table: trx_production_costs
-- Source: Doc/ProductionCost.xlsx
-- Stores line items
CREATE TABLE IF NOT EXISTS public.trx_production_costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.trx_general_infos(id) ON DELETE CASCADE,
    item_order INTEGER,
    
    product_name TEXT,
    product_rm TEXT,
    rm_price_snapshot DECIMAL(15,4),
    
    yield_loss_pct DECIMAL(5,2),
    yield_loss_val DECIMAL(15,4),
    bp_val DECIMAL(15,4),
    rm_net_yield DECIMAL(15,4),
    
    packaging DECIMAL(15,4),
    brand TEXT,
    pack_size TEXT,
    
    overhead_group INTEGER,
    overhead_val DECIMAL(15,4),
    
    quantity DECIMAL(15,2),
    factory_expense DECIMAL(15,4),
    
    freight_val DECIMAL(15,4),
    export_expense DECIMAL(15,4),
    
    commission DECIMAL(15,4),
    ap_expense DECIMAL(15,4),
    agreement DECIMAL(15,4),
    other_cost DECIMAL(15,4),
    
    total_cost DECIMAL(15,4),
    selling_price DECIMAL(15,4),
    
    margin_cost DECIMAL(15,4),
    ar_interest DECIMAL(15,4),
    rm_interest DECIMAL(15,4),
    wh_storage DECIMAL(15,4),
    margin_after DECIMAL(15,4),
    
    status TEXT, -- From Excel 'Status' col
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prod_qid ON public.trx_production_costs(quotation_id);


-- 5. Table: trx_loadings
-- Source: Doc/RemarkLoading.xlsx (Loading part)
CREATE TABLE IF NOT EXISTS public.trx_loadings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.trx_general_infos(id) ON DELETE CASCADE,
    
    order_no INTEGER, -- Matches 'Item'
    product_name TEXT, -- Matches 'Remark' (Loading Item)
    qty_cartons INTEGER, -- Matches 'Container'
    
    -- Not explicitly in RemarkLoading.xlsx but needed for logic:
    weight_per_unit DECIMAL(10,2), 
    total_weight DECIMAL(15,2),
    container_no TEXT,
    remark TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_load_qid ON public.trx_loadings(quotation_id);


-- 6. Table: trx_remarks
-- Source: Doc/RemarkLoading.xlsx (Remark part)
CREATE TABLE IF NOT EXISTS public.trx_remarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES public.trx_general_infos(id) ON DELETE CASCADE,
    
    order_no INTEGER,
    remark_text TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rem_qid ON public.trx_remarks(quotation_id);

-- RLS Policies
ALTER TABLE public.trx_general_infos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trx_export_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trx_interests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trx_production_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trx_loadings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trx_remarks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all access" ON public.trx_general_infos FOR ALL USING (true);
CREATE POLICY "Enable all access" ON public.trx_export_expenses FOR ALL USING (true);
CREATE POLICY "Enable all access" ON public.trx_interests FOR ALL USING (true);
CREATE POLICY "Enable all access" ON public.trx_production_costs FOR ALL USING (true);
CREATE POLICY "Enable all access" ON public.trx_loadings FOR ALL USING (true);
CREATE POLICY "Enable all access" ON public.trx_remarks FOR ALL USING (true);
