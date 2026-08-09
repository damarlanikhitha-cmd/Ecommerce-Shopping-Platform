# 🛒 E-Commerce Shopping Platform

A web-based **E-Commerce Shopping Platform** developed using **Python, Django, and MySQL**. The project provides essential online shopping functionality including product browsing, search, categories, cart management, wishlist, checkout, order management, product reviews, and coupon support.

## 🚀 Features

* 👤 User authentication
* 🛍️ Product listing and product details
* 🔎 Product search
* 📂 Product categories
* 🛒 Add products to cart
* ➕ Increase/decrease cart quantities
* 💰 Automatic cart total calculation
* ❤️ Wishlist functionality
* ⭐ Product reviews and ratings
* 🎟️ Coupon/discount functionality
* 📦 Checkout and order placement
* 📋 My Orders section
* 🚚 Order status management
* 🧾 Invoice generation/download
* 🔐 Django admin panel
* 🗄️ MySQL database integration
* 📱 Responsive web interface

## 🛠️ Technologies Used

### Backend

* Python
* Django

### Frontend

* HTML5
* CSS3
* JavaScript

### Database

* MySQL

### Development Tools

* Visual Studio Code
* Git
* GitHub

## 📁 Project Structure

```text
Ecommerce-Shopping-Platform/
│
├── ecommerce/
│   └── Django project configuration
│
├── shop/
│   └── E-commerce application
│
├── products/
│   └── Product-related functionality
│
├── templates/
│   └── HTML templates
│
├── manage.py
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/damarlanikhitha-cmd/Ecommerce-Shopping-Platform.git
```

### 2. Navigate to the project

```bash
cd Ecommerce-Shopping-Platform
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install django mysqlclient
```

> If your project uses a different MySQL Python package, install the package specified by your project configuration instead.

### 6. Configure MySQL

Create a MySQL database and configure the database settings in Django's `settings.py`.

Example:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**Do not commit real passwords, API keys, or other secrets to GitHub.**

### 7. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create an admin user

```bash
python manage.py createsuperuser
```

### 9. Start the development server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

## 🛒 Main Shopping Flow

```text
Browse Products
       ↓
Search / Categories
       ↓
View Product Details
       ↓
Add to Cart
       ↓
Review Cart
       ↓
Apply Coupon
       ↓
Checkout
       ↓
Place Order
       ↓
View Order
       ↓
Download Invoice
```

## 📦 Order Management

The application supports:

* Creating orders during checkout
* Saving customer information
* Storing order totals
* Tracking order status
* Viewing previous orders
* Downloading invoices

Order status can be managed through the Django admin panel.

## ⭐ Product Reviews

Users can submit:

* A rating
* A written review/comment

Reviews are associated with products and displayed on the product details page.

## 🔐 Security

The project follows Django's built-in security mechanisms and keeps sensitive configuration outside the Git repository.

Sensitive files such as `.env` should remain excluded through `.gitignore`.

## 🔮 Future Enhancements

Possible future improvements include:

* Online payment gateway integration
* Email notifications
* Advanced product filtering
* Product recommendations
* User profile management
* Improved responsive design
* Order tracking
* Stock management improvements
* Deployment to a production server
* Automated testing

## 👩‍💻 Author

**Nikhitha Damarla**

GitHub:
https://github.com/damarlanikhitha-cmd

## 📄 License

This project is currently developed as an internship/learning project.
