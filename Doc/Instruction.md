# 🛠 Full Tech Stack & Architecture Specifications (Updated)
**Project Name:** Antigravity Trader Quotation System

## 1. Executive Summary
The **Antigravity Quotation System** is engineered as a high-performance web application designed for rapid data entry and precise cost calculation. The architecture prioritizes **scalability, data integrity, and accessibility**, leveraging a modern Python stack connected to a cloud-native database (**Supabase**) to ensure real-time data synchronization and enterprise-grade security.

---

## 2. Technology Stack Breakdown

### 🖥️ Frontend & User Interface (The Presentation Layer)
* **Framework:** **Streamlit** (Python-based Web Framework)
    * *Why:* Renders reactive, data-driven web interfaces instantly. Eliminates frontend complexity (HTML/CSS/JS) while maintaining high responsiveness.
* **Styling Engine:** **Custom CSS Injection**
    * *Why:* Enforces the **Red & White Corporate Identity (CI)**. Overrides default styles for a clean, professional, and brand-consistent look (referencing `Theme.jpg`).
* **Layout Strategy:** **Grid System**
    * *Why:* Optimization for "Left-to-Right, Top-to-Bottom" workflow, reducing user cognitive load during high-volume data entry.

### ⚙️ Backend & Logic (The Application Layer)
* **Core Language:** **Python 3.10+**
    * *Why:* Industry standard for data processing, ensuring type safety and extensive library support.
* **Data Processing Engine:** **Pandas**
    * *Why:* High-speed in-memory data manipulation for complex cost calculations before syncing to the database.
* **API Connector:** **Supabase Python Client (`supabase-py`)**
    * *Why:* Provides a secure, type-safe interface to communicate with the Supabase backend via RESTful APIs.

### ☁️ Database & Storage (The Persistence Layer - Upgraded)
* **Cloud Database:** **Supabase (PostgreSQL)**
    * *Why:*
        * **Relational Integrity:** Uses PostgreSQL, the world's most advanced open-source relational database, ensuring data consistency (ACID compliance) far superior to Excel.
        * **Real-time:** Changes are reflected instantly across all connected clients.
        * **Scalability:** Handles thousands of quotation records without performance degradation.
        * **Accessibility:** Data is safely stored in the cloud, accessible from any authorized machine, eliminating "file lock" issues common in local Excel files.
* **Table Structure (Supabase):**
    * Table: `quotations` (Stores transaction data: Customer, Product, Cost, Profit, etc.)
    * Table: `master_products` (Replaces local master files for centralized management)
    * Table: `master_customers` (Centralized customer list)

---

## 3. System Architecture Context

### 🏗️ Data Flow Diagram (Cloud-Native)
```mermaid
graph LR
    User[User / Trader] -- Input Data --> UI[Web Interface (Streamlit)]
    UI -- Process Request --> Logic[Python Business Logic]
    
    subgraph "Calculation Layer"
    Logic -- Compute Cost --> Pandas[Pandas DataFrame]
    end
    
    subgraph "Cloud Persistence Layer (Supabase)"
    Logic -- API Request (JSON) --> Client[Supabase Client]
    Client -- Secure HTTPS --> CloudDB[(Supabase PostgreSQL)]
    end

    CloudDB -- Real-time Data --> UI