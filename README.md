# Cloud Kitchen

Cloud Kitchen is a Django-based web application designed to manage online food orders, restaurants, menus, and customer interactions efficiently. This system provides a robust admin dashboard, and user authentication features.

## Features

### **1. User Management**
- User authentication (Login, Signup, Logout)
- Role-based access (Admin, Restaurant Owner, Customer)
- Profile management

### **2. Restaurant Management**
- Add, update, and delete restaurant details
- Manage multiple restaurants
- Upload restaurant images and descriptions

### **3. Menu Management**
- Add, update, and remove food items
- Categorize menu items (Starters, Main Course, Desserts, Drinks, etc.)
- Set pricing and availability

### **4. Ordering System**
- Customers can browse menus and place orders
- Real-time order tracking
- Payment integration (if applicable)

### **5. Admin Dashboard**
- Admin panel for managing restaurants, orders, and users
- Dashboard statistics and reports

### **6. Additional Features**
- Search and filter options for restaurants and menu items
- User reviews and ratings

## Installation Guide

### **Prerequisites**
Make sure you have the following installed:
- Python 3.8+
- Django 5+
- Virtualenv (optional but recommended)
- MySQL or SQLite for database management

### **Step 1: Clone the Repository**
```sh
 git clone https://github.com/Nishanchaudhary/Cloud_kitchen.git
 cd Cloud_kitchen
```

### **Step 2: Create and Activate Virtual Environment**
```sh
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate (Mac/Linux)
venv\Scripts\activate  # Activate (Windows)
```

### **Step 3: Install Dependencies**
```sh
pip install -r requirements.txt
```

### **Step 4: Configure Database**
By default, the project uses SQLite. If you want to use MySQL:
1. Install MySQL and create a database.
2. Update `settings.py`:
   ```python
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # MySQL database engine
        'NAME': config('DB_NAME'),            # Database name
        'USER': config('DB_USER'),            # Database user
        'PASSWORD': config('DB_PASSWORD'),    # Database password
        'HOST': config('DB_HOST'),            # Database host (e.g., 'localhost')
        'PORT': config('DB_PORT'),            # Database port (default is 3306 for MySQL)
        'OPTIONS': {
            'charset': 'utf8mb4',             # Use utf8mb4 for full Unicode support 
        },
    }}
   ```

### **Step 5: Run Migrations**
```sh
python manage.py migrate
```

### **Step 6: Create a Superuser**
```sh
python manage.py createsuperuser
```
Follow the prompts to set up an admin account.

### **Step 7: Run the Development Server**
```sh
python manage.py runserver
```
Access the application at **http://127.0.0.1:8000/**.

## Admin Panel
- Login at **http://127.0.0.1:8000/admin/**
- Use the superuser credentials to access the dashboard.
- Customized admin panel settings:
  ```python
  admin.site.site_header = "Cloud Kitchen Admin"
  admin.site.site_title = "Cloud Kitchen Dashboard"
  admin.site.index_title = "Welcome to Cloud Kitchen"
  ```

## Contact
For any issues or feature requests, contact:
- **GitHub**: [Nishanchaudhary](https://github.com/Nishanchaudhary)
- **Email**: chaudharynishan314@gmail.com
