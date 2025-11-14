# 🌾 AgriFarma - Agriculture Community Platform

> An integrated platform for agriculture knowledge, community discussions, consultancy services, and a trusted marketplace.

[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Features

### 🏠 **Role-Based Dashboards**
- **Community Dashboard** - For regular users featuring recent discussions, articles, consultants, and products
- **Admin Analytics Dashboard** - For administrators with platform metrics, moderation tools, and user management

### 💬 **Forum**
- Create and participate in agricultural discussions
- Category-based organization
- Reply threading
- Admin moderation capabilities

### 📚 **Knowledge Base**
- Create and publish agricultural articles
- Approval workflow for quality control
- Comment system
- Media attachments

### 👥 **Consultancy Services**
- Browse approved agricultural consultants
- Category filtering (Crop Management, Soil Health, Pest Control, etc.)
- Application system with admin approval
- Profile pages for consultants

### 🛒 **E-Commerce Shop**
- Browse and purchase agricultural products
- Shopping cart functionality
- Order history tracking
- Product reviews
- Admin product management

### 🔐 **Authentication & Authorization**
- User registration and login
- Role-based access control (User, Consultant, Admin)
- Profile management
- Secure password hashing

### 📊 **Admin Tools**
- User management (activate/deactivate)
- Content moderation (blog posts, products)
- Analytics and reports
- Low inventory alerts
- Sales tracking

---

## 🎨 Branding & Design

**AgriFarma** features a custom agricultural-themed design:

- **Color Palette**: Forest greens, earthy browns, harvest gold
- **Modern UI**: Card-based layouts with smooth animations
- **Responsive**: Mobile-first design with Bootstrap 5
- **Icons**: Bootstrap Icons for visual clarity
- **Accessibility**: High contrast, semantic HTML, ARIA labels

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd c:\Users\mirai\Downloads\free-flask-datta-able-master\flask-datta-able-master
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
   
   *Or let the app auto-create the database on first run (SQLite default)*

4. **Create your first admin account**
   ```bash
   flask create-admin
   ```
   Follow the prompts to enter:
   - Email address
   - Password
   - Full name

5. **Run the application**
   ```bash
   python app.py
   # or
   flask run
   ```

6. **Access the application**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 📁 Project Structure

```
agrifarma/
├── __init__.py           # App factory
├── extensions.py         # Flask extensions (db, login_manager, migrate)
├── config.py            # Configuration classes
├── models/              # Database models
│   ├── user.py          # User model
│   ├── profile.py       # User profile
│   ├── forum.py         # Forum threads & replies
│   ├── blog.py          # Blog posts & comments
│   ├── consultancy.py   # Consultant model
│   ├── ecommerce.py     # Products, orders, cart
│   └── shop.py          # Shop-related models
├── routes/              # Blueprint routes
│   ├── main.py          # Homepage & dashboards
│   ├── auth.py          # Authentication
│   ├── forum.py         # Forum functionality
│   ├── blog.py          # Knowledge base
│   ├── consultancy.py   # Consultancy services
│   ├── ecommerce.py     # Shop & cart
│   ├── admin.py         # Admin panel
│   └── media.py         # File uploads
├── services/            # Business logic
│   ├── analytics.py     # Data analytics
│   ├── email.py         # Email service (stub)
│   ├── security.py      # Access control decorators
│   └── uploads.py       # File upload helpers
├── forms/               # WTForms classes
├── templates/           # Jinja2 templates
│   ├── layouts/         # Base layouts
│   ├── includes/        # Reusable components (sidebar, nav)
│   ├── *.html          # Page templates
├── static/              # Static assets
│   ├── css/
│   │   └── agrifarma.css  # Custom branding
│   ├── js/
│   └── images/
└── uploads/             # User-uploaded files

tests/                   # Pytest test suite
app.py                   # Application entry point + CLI commands
wsgi.py                  # WSGI entry point for production
config.py                # Configuration
requirements.txt         # Python dependencies
ADMIN_SETUP.md          # Admin account creation guide
UI_IMPLEMENTATION_SUMMARY.md  # UI enhancement details
```

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///agrifarma.db'
    UPLOADED_MEDIA_DEST = 'agrifarma/uploads'
    LOW_INVENTORY_THRESHOLD = 5
```

---

## 🎯 CLI Commands

AgriFarma includes helpful CLI commands:

### Create Admin User
```bash
flask create-admin
```
Interactively creates a new admin account or promotes an existing user.

### List All Admins
```bash
flask list-admins
```
Displays all admin users with their status.

### Database Management
```bash
flask db init          # Initialize migrations
flask db migrate       # Generate migration
flask db upgrade       # Apply migrations
flask db downgrade     # Rollback migration
```

### Flask Shell
```bash
flask shell
```
Interactive Python shell with app context.

---

## 👤 User Roles

| Role | Permissions |
|------|-------------|
| **User** | Default role. Can participate in forums, read articles, purchase products, contact consultants |
| **Consultant** | User + consultant profile visible in consultancy directory |
| **Admin** | Full platform access including user management, moderation, analytics |

### Creating Admin Accounts

See **[ADMIN_SETUP.md](ADMIN_SETUP.md)** for detailed instructions including:
- Flask shell method
- Direct database updates
- CLI command usage
- Security best practices

---

## 🧪 Testing

Run the test suite:

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_auth.py # Run specific test file
pytest -k "test_admin"    # Run tests matching pattern
pytest --cov=agrifarma    # Generate coverage report
```

---

## 🔒 Security Features

- **Password Hashing**: Werkzeug security with bcrypt
- **CSRF Protection**: Flask-WTF automatic CSRF tokens
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Role-Based Access Control**: Decorators and template checks
- **Session Management**: Flask-Login secure sessions
- **XSS Prevention**: Jinja2 auto-escaping

---

## 🌐 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

### Using uWSGI

```bash
uwsgi --http :8000 --wsgi-file wsgi.py --callable application --processes 4 --threads 2
```

### Environment Variables

```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@localhost/agrifarma
```

---

## 📚 Dependencies

Key packages:
- **Flask** 2.3+ - Web framework
- **Flask-SQLAlchemy** 3.0+ - ORM
- **Flask-Login** 0.6+ - Authentication
- **Flask-WTF** 1.2+ - Forms with CSRF
- **Flask-Migrate** 4.0+ - Database migrations
- **Werkzeug** 2.3+ - WSGI utilities
- **Jinja2** 3.1+ - Templating engine
- **Bootstrap** 5.3 - CSS framework (CDN)
- **Bootstrap Icons** 1.11 - Icon library (CDN)

See `requirements.txt` for complete list.

---

## 📖 Documentation

- **[ADMIN_SETUP.md](ADMIN_SETUP.md)** - Admin account creation guide
- **[UI_IMPLEMENTATION_SUMMARY.md](UI_IMPLEMENTATION_SUMMARY.md)** - UI design and branding details
- **API Docs** - (Future: Swagger/OpenAPI documentation)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Use type hints where possible

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Flask** community for the excellent framework
- **Bootstrap** team for the UI components
- Original **Datta Able** template structure
- Agricultural community for inspiration

---

## 📞 Support

For questions, issues, or feature requests:
- **GitHub Issues**: Submit a ticket
- **Email**: support@agrifarma.local (placeholder)
- **Documentation**: Check ADMIN_SETUP.md and UI_IMPLEMENTATION_SUMMARY.md

---

## 🗺️ Roadmap

### Phase 1 (Current) ✅
- [x] Core platform features
- [x] Role-based dashboards
- [x] Custom branding
- [x] Admin management tools

### Phase 2 (Planned)
- [ ] Real-time notifications
- [ ] Advanced analytics charts
- [ ] Email integration (SMTP)
- [ ] File upload improvements
- [ ] Search functionality enhancement

### Phase 3 (Future)
- [ ] Mobile app (React Native)
- [ ] Payment gateway integration
- [ ] API endpoints (REST)
- [ ] Multi-language support
- [ ] Advanced reporting (PDF export)

---

**Built with ❤️ for the agricultural community**

🌾 Happy Farming! 🚜
