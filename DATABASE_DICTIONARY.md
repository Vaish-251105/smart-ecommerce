# SMART ECOMMERCE PLATFORM

## 6.2 Database Design

### 6.2.1 Data Dictionary

#### 1. AppUser Table
Central table for user identity and role management.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Unique identifier for the user | Primary Key | Auto-increment |
| user_auth | Integer | Reference to Django Auth User | Foreign Key | Nullable |
| username | Varchar(100) | Unique display name | | Required |
| email | Varchar(255) | Official email for authentication | | Required, Unique |
| password | Varchar(255) | Hashed password | | Required |
| role | Varchar(20) | User role (admin, supplier, consumer) | | Choices |
| phone | Varchar(15) | Contact mobile number | | Required |
| is_active | Boolean | Account status | | Default = True |
| created_at | DateTime | Account creation timestamp | | Auto-generated |

#### 2. ConsumerProfile Table
Stores supplementary data for users with the 'consumer' role.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Profile primary ID | Primary Key | Auto-increment |
| user_id | Integer | Link to AppUser | Foreign Key | 1-to-1 Mapping |
| wallet_balance| Decimal(10,2) | User's virtual credit balance | | Default = 0.00 |
| is_opted_in | Boolean | Subscription status for marketing | | Default = True |

#### 3. SupplierProfile Table
Stores business details for users with the 'supplier' role.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Profile primary ID | Primary Key | Auto-increment |
| user_id | Integer | Link to AppUser | Foreign Key | 1-to-1 Mapping |
| company_name | Varchar(150) | Business entity name | | Nullable |
| logo | Image | Company brand logo | | Nullable |
| gst_number | Varchar(50) | GST tax identification number | | Nullable |
| address | Text | Registered business address | | Nullable |
| rating | Float | Performance/Satisfaction rating | | Default = 0 |
| verified | Boolean | KYC Verification status | | Default = False |

#### 4. Address Table
Stores geographical and contact details for deliveries.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Address record ID | Primary Key | Auto-increment |
| user_id | Integer | Reference to AppUser | Foreign Key | Required |
| full_name | Varchar(150) | Consignee's name | | Required |
| phone_number | Varchar(15) | Delivery contact number | | Required |
| address_line1 | Varchar(255) | House/Bldg/Street details | | Required |
| locality | Varchar(150) | Neighborhood or sector | | Required |
| city | Varchar(100) | City name | | Required |
| district | Varchar(100) | District name | | Required |
| state | Varchar(100) | State name | | Required |
| pincode | Varchar(10) | Postal ZIP code | | Required |
| is_default | Boolean | Is this the primary address? | | Default = False |

#### 5. Category Table
Organizes products into hierarchies.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Category unique ID | Primary Key | Auto-increment |
| name | Varchar(100) | Label of the category | | Unique |
| slug | Slug | URL segment for category | | Unique |
| is_active | Boolean | Toggle for category visibility | | Default = True |

#### 6. Product Table
The master catalog of all physical or digital goods.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Unique product ID | Primary Key | Auto-increment |
| supplier_id | Integer | Link to Supplier User | Foreign Key | Required |
| category_id | Integer | Link to Category Table | Foreign Key | Required |
| name | Varchar(200) | Commercial product name | | Required |
| description | Text | Full product technicalities | | Required |
| price | Decimal(10,2) | Retail selling price | | Required |
| stock | Integer | Current warehouse quantity | | Minimum 0 |
| image | Image | High-res product photograph | | Nullable |
| approval_status| Varchar(20) | Admin vetting status | | Pending/Approved |
| created_at | DateTime | Date of product onboarding | | Auto-generated |

#### 7. Wishlist Table
Enables users to save products for later consideration.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Wishlist identity ID | Primary Key | Auto-increment |
| user_id | Integer | Reference to User | Foreign Key | Required |
| products | ManyToMany | Collection of saved products | | Junction Table |

#### 8. Cart Table
Stores the data for current shopping intent.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Cart session ID | Primary Key | Auto-increment |
| user_id | Integer | Owner of the shopping cart | Foreign Key | Required |
| created_at | DateTime | Cart creation time | | Auto-generated |

#### 9. CartItem Table
Detailed breakdown of items inside a cart.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Item line-ID | Primary Key | Auto-increment |
| cart_id | Integer | Parent cart reference | Foreign Key | Required |
| product_id | Integer | Reference to Product | Foreign Key | Required |
| quantity | Integer | Volume of units | | Minimum 1 |

#### 10. Order Table
Records finalized transactions and fulfillment status.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Order reference number | Primary Key | Auto-increment |
| user_id | Integer | Consuming user reference | Foreign Key | Required |
| total_price | Decimal(10,2) | Final payable amount | | Required |
| status | Varchar(20) | Current shipment/delivery stage | | Default = Pending |
| delivery_address| JSON | Snapshotted address data | | Required |
| created_at | DateTime | Ordering timestamp | | Auto-generated |

#### 11. OrderItem Table
The specific inventory units tied to a confirmed order.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Entry reference ID | Primary Key | Auto-increment |
| order_id | Integer | Link to Order parent | Foreign Key | Required |
| product_id | Integer | Link to Product | Foreign Key | Required |
| quantity | Integer | Units purchased | | Required |
| price | Decimal(10,2) | Price locked at time of order | | Required |

#### 12. Payment Table
Audit trail for financial settlements.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Payment record ID | Primary Key | Auto-increment |
| order_id | Integer | One-to-one link to Order | Foreign Key | Unique |
| transaction_id | Varchar(100) | Gateway reference (Razorpay/Stripe) | | Nullable |
| amount | Decimal(10,2) | Settlement amount | | Required |
| is_successful | Boolean | Transaction success flag | | Required |

#### 13. Notification Table
Logs system alerts and direct messages for users.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Notification ID | Primary Key | Auto-increment |
| user_id | Integer | Recipient user ID | Foreign Key | Required |
| message | Text | Body of the notification | | Required |
| is_read | Boolean | View status | | Default = False |
| created_at | DateTime | Alert timestamp | | Auto-generated |

#### 14. PromotionalMessage Table
Broadcast messages and campaigns.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Message ID | Primary Key | Auto-increment |
| title | Varchar(150) | Headline of promotion | | Required |
| content | Text | Detailed promo body | | Required |
| target_role | Varchar(20) | User segment (e.g. consumer) | | Default = consumer |
| created_at | DateTime | Generation timestamp | | Auto-generated |

#### 15. Banner Table
Stores dynamic UI assets for the homepage.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Banner identity ID | Primary Key | Auto-increment |
| title | Varchar(200) | Branding title text | | Required |
| subtitle | Text | Call-to-action details | | Required |
| is_active | Boolean | Visibility status | | Default = True |

#### 16. AdminLog Table
Audit logs for administrative operations.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Log entry ID | Primary Key | Auto-increment |
| admin_id | Integer | Reference to the performing Admin | Foreign Key | Required |
| action | Text | Detailed activity description | | Required |
| timestamp | DateTime | Event timestamp | | Auto-generated |

#### 17. ChatbotLog Table
Logs of AI-driven customer support sessions.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Session entry ID | Primary Key | Auto-increment |
| user_id | Integer | User interacting with AI | Foreign Key | Required |
| query | Text | User's question/input | | Required |
| intent | Varchar(50) | Decoded goal (e.g. Track Order) | | Required |
| response | Text | AI-generated reply | | Required |
| created_at | DateTime | Log timestamp | | Auto-generated |

#### 18. ProductAIScore Table
AI-calculated metrics for supply-demand analysis.

| Field Name | Data Type | Description | Key | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| id | Integer | Score entry ID | Primary Key | Auto-increment |
| product_id | Integer | Link to Product | Foreign Key | Required |
| demand_score | Float | Popularity metric | | 0.0 - 1.0 |
| trust_score | Float | Reliability metric | | 0.0 - 1.0 |
| final_ai_score | Float | Weighted aggregate | | Required |
| updated_at | DateTime | Last calculation date | | Auto-generated |
