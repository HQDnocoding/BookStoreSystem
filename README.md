# 📚 BookStoreSystem

A **Book Store Management System** built with **Python Flask**, featuring **VNPAY payment integration**, **role-based access control**, and complete bookstore management (users, books, orders, inventory).

---

## 🚀 Features
- 👤 **User Management**
  - Register, login with JWT authentication  
  - Roles: **Admin**, **Staff**, **Customer**  
  - Permissions based on roles  

- 📚 **Book & Inventory Management**
  - CRUD operations for books  
  - Inventory tracking (stock in/out)  
  - Staff can update warehouse  

- 🛒 **Order Management**
  - Customers can purchase books  
  - Staff/Admin can manage orders  

- 💳 **Payment**
  - Integration with **VNPAY Payment Gateway**  

- 📊 **Admin Panel**
  - Manage users, staff, books, orders, and warehouse  

---

## 🔧 Tech Stack
- **Backend**: Python, Flask  
- **Database**: MySQL (SQLAlchemy + Flask-Migrate)  
- **Authentication**: JWT  
- **Payment**: VNPAY Gateway  
- **Environment**: Virtualenv / pip  
