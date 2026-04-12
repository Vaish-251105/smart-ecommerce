# 🛒 Bloom & Buy - Smart Ecommerce Platform

A production-ready, full-stack E-commerce platform built with **Django REST Framework** (Backend) and **React Vite** (Frontend).

## 🔗 Live Demo
- **Frontend:** [https://smart-ecommerce-frontend.onrender.com](https://smart-ecommerce-frontend.onrender.com)
- **Backend API:** [https://smart-ecommerce-backend.onrender.com](https://smart-ecommerce-backend.onrender.com)

---

## 🚀 Key Features

### 🔔 Multi-Channel Notification System
- **Professional HTML Emails:** Sent automatically for registration, subscriptions, order placement, and payment confirmation.
- **SMS & WhatsApp Alerts:** Powered by **Twilio**, providing real-time order tracking and status updates to your phone.
- **Branded Experience:** All communications are custom-templated under the "Bloom & Buy" brand.

### 💳 Secure Payments & Backend
- **Razorpay Integration:** Secure checkout and payment processing.
- **Order Management:** Automated cart-to-order workflow.
- **Invoice Generation:** Automatic PDF invoice generation for every successful order.
- **Role-Based Access:** Distinct experiences for Consumers and Suppliers (Sellers).

### 🤖 Smart Features
- **AI-Powered Support:** Integrated OpenAI for smart customer queries.
- **Interactive Dashboard:** Full-featured admin and seller panels for product and order management.

---

## 🏗 Tech Stack

- **Backend:** Python (Django, DRF, PostgreSQL/SQLite)
- **Frontend:** React JS (Vite, Tailwind CSS/Vanilla CSS)
- **Communication:** Twilio (SMS/WhatsApp), SMTP (Email)
- **Deployment:** Render (Infrastructure as Code via `render.yaml`)
- **Authentication:** JWT (JSON Web Tokens)

---

## 📂 Project Structure

```text
Smart_Ecommerce/
├── Backend/          # Django REST APIs & Business Logic
│   ├── accounts/     # User Auth & Google Login
│   ├── orders/       # Order & Payment Processing
│   ├── store/        # Product & Category Management
│   ├── users/        # Profiles & Email/SMS Utilities
│   └── manage.py
└── frontend/         # React SPA
    ├── src/          # Components & State Management
    └── public/       # Static assets
```

---

## ⚙️ Installation & Setup (Local)

1. **Clone the Repo**
   ```bash
   git clone https://github.com/Vaish-251105/smart-ecommerce.git
   ```

2. **Backend Setup**
   ```bash
   cd Backend
   python -m venv venv
   source venv/bin/activate # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

---

## 🔑 Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Postgres Database URL (Production) |
| `EMAIL_HOST_USER` | SMTP Username |
| `EMAIL_HOST_PASSWORD` | SMTP App Password |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `RAZORPAY_KEY_ID` | Razorpay Public Key |

---

## 👩‍💻 Author
**Developed by Vaishnavi**
*Project for Scalable E-commerce Application*
