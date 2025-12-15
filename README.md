# Workshop Management System

## 📌 Project Overview
This project is a **full-stack e-commerce application** designed for managing workshop inventory, orders, and sales.  
It features a robust backend built with **Python (Flask)** and **PostgreSQL**, connected to a dynamic frontend using **HTML, CSS, and JavaScript**.

The system supports complex workflows including:
- User authentication
- Product browsing
- Blinkit-style shopping cart
- Checkout processing
- Payment simulation
- Order history management (cancellations & returns)

---

## 🧱 Tech Stack

### Backend
- Python 3
- Flask
- SQLAlchemy (ORM)

### Database
- PostgreSQL

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript (Fetch API)

### Data Generation
- Python (pandas, faker)

---

## ⚙️ Installation & Setup

### 1️ Prerequisites
- Python 3.x
- PostgreSQL (running)
- pgAdmin (recommended)

---

### 2️ Database Setup

1. Open **pgAdmin**
2. Create a database named: workshop_management
3. Create the tables in PostgreSQL (or Python) as per your interest.

### 3 Install Dependencies
pip install -r requirements.txt

### 4 Add your data
For sample data use "python data_generator.py"
This generates 11 CSV files, including:

Sellers.csv

Products.csv

Customers.csv

Orders.csv

Payments.csv

### 5 Run the Application
python app.py

Access the app at:
http://127.0.0.1:5000


---

## 📂 File Structure & Functionality

### Core Application

- **app.py**  
  Entry point of the application. Initializes Flask, sets up routes, and connects all backend modules.

- **Database_config.py**  
  Stores PostgreSQL database connection configuration.

- **models.py**  
  Defines database schema using SQLAlchemy ORM and manages table relationships.

---

## 🔧 Backend Logic Modules

### User Authentication
- `handle_register()`  
  Registers or logs in users based on phone number or username.

---

### Product Management
- Fetches only available products (`stock_remaining > 0`)
- Joins inventory and seller data
- Returns structured JSON responses for frontend rendering

---

### Order Management (Core Engine)
- Atomic checkout using database transactions
- Inventory row locking to prevent race conditions
- Handles:
  - Order creation
  - Order cancellation
  - Order returns
  - Inventory restoration

---

### Payment Module
- Simulated payment processing
- Transaction logging with **SHA-256 hash** for integrity

---

## 🖥️ Frontend Structure

### Templates
- `index.html`
- `shop.html`
- `payment.html`
- `profile.html`
- `client_login.html`

### JavaScript Modules
- **auth.js** – Handles user login & registration
- **shop.js** – Manages Blinkit-style cart logic (+ / − buttons, single-seller constraint)
- **payment.js** – Handles payment flow & cancellations
- **profile.js** – Displays order history and manages returns/cancellations

---



