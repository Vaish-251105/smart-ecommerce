# Detailed Database Design & Data Flow Diagrams (DFD)

This document provides a highly detailed technical specification of the **Bloom & Buy** database architecture and logical data flow.

---

## 1. Data Flow Diagrams (DFD)

### DFD Level 0: Context Diagram
The Level 0 DFD defines the system boundary and external entities.

```mermaid
graph LR
    U[Consumer/User]
    S[Supplier/Seller]
    A[Global Admin]
    RP[[Razorpay Gateway]]
    TW[[Twilio/Email API]]
    OA[[OpenAI API]]
    
    System((Smart Ecommerce Platform))
    
    U -- "Browse, Cart, Order, Chat" --> System
    System -- "Products, Success Msg, AI Reply" --> U
    
    S -- "Manage Inventory, View Stats" --> System
    System -- "Sales Reports, Approval Notifications" --> S
    
    A -- "Manage Users, Approve Items" --> System
    System -- "Audit Logs, Global Metrics" --> A
    
    System -- "Payment Intent / Msg Payload" --> RP
    RP -- "Payment Success / Webhook" --> System
```

### DFD Level 1: Functional Breakdown
Breaking the system into core sub-processes.

```mermaid
graph TD
    %% Processes
    P1[1.0 Auth & Profile Mgmt]
    P2[2.0 Catalog & Search]
    P3[3.0 Transaction Engine]
    P4[4.0 AI Assistant]
    P5[5.0 Notification Hub]

    %% Flow
    User([User]) -->|Register/Login| P1
    P1 -->|Session| User
    
    User -->|Queries| P2
    P2 -->|Product Info| User
    
    User -->|Checkout| P3
    P3 -->|Payment Verification| RP[[Razorpay]]
    
    User -->|Chat| P4
    P4 -->|Contextual Advice| OA[[OpenAI]]
    
    P3 -->|Trigger| P5
    P5 -->|SMS/WA/Email| User
```

### DFD Level 2: Order Processing Detail
Refining the transaction process (3.0 from Level 1).

```mermaid
graph TD
    Proc1[3.1 Validation]
    Proc2[3.2 Payment Request]
    Proc3[3.3 Signature Verif]
    Proc4[3.4 Record Order]
    
    Cart[(Cart Data)] --> Proc1
    Proc1 --> Proc2
    Proc2 -->|API Call| RP[[Razorpay]]
    RP -->|Callback| Proc3
    Proc3 -->|Success| Proc4
    Proc4 -->|Data Store| DB[(Order DB)]
```

### DFD Level 3: Logic flow for Notifications
Micro-level steps for the notification mesh.

```mermaid
graph TD
    Steps1[5.1 Match User Preferences]
    Steps2[5.2 Route to Provider]
    Steps3[5.3 Format Message]
    Steps4[5.4 Execution]
    
    DB[(Notification Log)] --> Steps1
    Steps1 --> Steps2
    Steps2 -->|Email| Steps3
    Steps2 -->|SMS/WA| TW[[Twilio]]
    Steps3 -->|SMTP| EM[[Mail Server]]
```

---

## 2. Comprehensive Database Design (Data Dictionary)

### Table 1: `auth_user` (Django Default + Extension)
| Field Name | Datatype | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK, Auto Inc | Primary ID of the user. |
| `username`| VARCHAR(150)| Unique | Unique login handle. |
| `email` | VARCHAR(255)| Unique | User email for Auth/Email. |
| `password`| VARCHAR(255)| Encrypted | Hashed user password. |

### Table 2: `store_product` (Inventory)
| Field Name | Datatype | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK | Unique product identifier. |
| `name` | VARCHAR(200)| NOT NULL | Name of the product. |
| `price` | DECIMAL(10,2)| > 0 | Unit price. |
| `stock` | INT | NOT NULL | Available quantity. |
| `category_id`| INT | FK (store_category) | Link to category. |
| `supplier_id`| INT | FK (auth_user) | Link to seller user. |
| `approval` | VARCHAR(20) | Default 'pending' | Status: approved/rejected. |

### Table 3: `orders_order` (Transactions)
| Field Name | Datatype | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK | Unique order ID. |
| `user_id` | INT | FK (auth_user) | Consumer who ordered. |
| `total_price`| DECIMAL(10,2)| NOT NULL | Final amount including tax. |
| `status` | VARCHAR(20) | Default 'Pending' | Pending, Shipped, Delivered. |
| `is_paid` | BOOLEAN | Default False | Payment status flag. |
| `tracking_id`| VARCHAR(100)| Nullable | Logistic tracking number. |

### Table 4: `orders_payment` (Finance)
| Field Name | Datatype | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK | Payment record ID. |
| `order_id` | INT | FK, Unique (Order)| Link to specific order. |
| `rp_order_id`| VARCHAR(100)| Unique | Razorpay generated ID. |
| `signature` | VARCHAR(255)| NOT NULL | Razorpay verification sig. |
| `status` | VARCHAR(20) | NOT NULL | Success, Failed, Refunded. |

---

## 3. Database Relationship Diagram (DRD)

```mermaid
erDiagram
    User ||--o| SupplierProfile : "has"
    User ||--o| ConsumerProfile : "has"
    User ||--o{ Order : "places"
    Category ||--o{ Product : "contains"
    User ||--o{ Product : "posts (Seller)"
    Order ||--o{ OrderItem : "details"
    Product ||--o{ OrderItem : "appears-in"
    Order ||--o| Payment : "settles"
    User ||--o{ Address : "saved-at"
```

---

## 4. Entity Relationship (ER) Diagram
Detailed attributes and entity sets.

```mermaid
erDiagram
    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
        string status
    }
    CATEGORY {
        int id PK
        string name
        string slug
    }
    ORDER {
        int id PK
        timestamp created_at
        decimal total
        string payment_status
    }
    ORDER_ITEM {
        int id PK
        int quantity
        decimal price
    }
    ADDRESS {
        int id PK
        string city
        string pincode
        string state
    }

    PRODUCT }o--|| CATEGORY : "categorized-as"
    ORDER_ITEM }o--|| ORDER : "part-of"
    ORDER_ITEM }o--|| PRODUCT : "refers-to"
    ORDER ||--o{ ADDRESS : "ships-to"
```

---
*End of Technical Specification.*
