# Detailed Database Relationship Diagram (ERD)

This document provides a comprehensive technical mapping of the **Bloom & Buy** database schema, showing every table, field, data type, and relationship as implemented in the Django backend.

```mermaid
erDiagram
    %% Identity & User Management
    APP_USER {
        int id PK
        int user_auth_id FK
        string username
        string email
        string password
        string role "admin/supplier/consumer"
        string phone
        boolean is_active
        datetime created_at
    }

    SUPPLIER_PROFILE {
        int id PK
        int user_id FK
        string company_name
        string gst_number
        text address
        float rating
        boolean verified
        image logo
    }

    CONSUMER_PROFILE {
        int id PK
        int user_id FK
        decimal wallet_balance
        boolean is_opted_in
    }

    ADDRESS {
        int id PK
        int user_id FK
        string full_name
        string phone_number
        string address_line1
        string address_line2
        string locality
        string city
        string district
        string state
        string pincode
        boolean is_default
        datetime created_at
    }

    %% Store & Catalog
    CATEGORY {
        int id PK
        string name
        slug slug
        boolean is_active
    }

    PRODUCT {
        int id PK
        int supplier_id FK "Django Auth User"
        int category_id FK
        string name
        text description
        decimal price
        decimal base_price
        int stock
        string brand
        string seasonal_tag
        string tags
        string approval_status "pending/approved/rejected"
        text rejection_reason
        boolean is_active
        image image
        datetime created_at
    }

    BANNER {
        int id PK
        string title
        text subtitle
        string background_gradient
        string accent_color
        string link
        string button_text
        string badge_text
        string emoji
        boolean is_active
        int order
    }

    %% Shopping Session
    CART {
        int id PK
        int user_id FK
        datetime created_at
    }

    CART_ITEM {
        int id PK
        int cart_id FK
        int product_id FK
        int quantity
    }

    WISHLIST {
        int id PK
        int user_id FK
    }

    %% Transactions & Logistics
    ORDER {
        int id PK
        int user_id FK
        datetime created_at
        datetime updated_at
        decimal subtotal
        decimal discount
        decimal cgst
        decimal sgst
        decimal igst
        decimal shipping
        decimal total_price
        boolean is_paid
        string status "Pending...Delivered"
        string payment_status
        json delivery_address
        string tracking_id
        string carrier
        date estimated_delivery
        json tracking_history
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }

    PAYMENT {
        int id PK
        int order_id FK
        string payment_method
        string transaction_id
        string razorpay_order_id
        string razorpay_payment_id
        string razorpay_signature
        decimal amount
        boolean is_successful
        string status
        datetime created_at
    }

    %% Communications
    NOTIFICATION {
        int id PK
        int user_id FK
        string type "Email/SMS/WhatsApp"
        string title
        text message
        boolean is_read
        string status
        datetime created_at
    }

    %% Relationships
    APP_USER ||--|| SUPPLIER_PROFILE : "associated-with"
    APP_USER ||--|| CONSUMER_PROFILE : "associated-with"
    APP_USER ||--o{ ADDRESS : "manages"
    APP_USER ||--o{ ORDER : "initiates"
    APP_USER ||--o| CART : "fills"
    APP_USER ||--o| WISHLIST : "maintains"
    APP_USER ||--o{ NOTIFICATION : "receives"

    CATEGORY ||--o{ PRODUCT : "categorizes"
    PRODUCT ||--o{ CART_ITEM : "unit-of"
    PRODUCT ||--o{ ORDER_ITEM : "unit-of"
    PRODUCT ||--o{ WISHLIST : "included-in"
    
    CART ||--o{ CART_ITEM : "contains"
    ORDER ||--o{ ORDER_ITEM : "contains"
    ORDER ||--|| PAYMENT : "settles"
```

### Logical Annotations:
1.  **Identity Split:** The system uses a Django `User` model for authentication, linked to an `AppUser` for role-based logic, which further branches into `SupplierProfile` or `ConsumerProfile` for specific metadata.
2.  **Financial Integrity:** The `ORDER` table stores a calculated snapshot of taxes (CGST/SGST/IGST) and discounts at the time of purchase to ensure historical audit accuracy.
3.  **Logistics Tracking:** The `tracking_history` is stored as a JSON blob to allow flexible, timeline-based tracking updates without schema changes.
4.  **Moderation Workflow:** The `PRODUCT` table includes `approval_status` and `rejection_reason` to facilitate the Admin-to-Supplier communication loop.
