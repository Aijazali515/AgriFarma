# AgriFarma - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Setup Environment
```powershell
# Clone/Navigate to project directory
cd flask-datta-able-master

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Application
```powershell
# Copy environment template
copy .env.example .env

# Edit .env with your settings (optional for testing)
# notepad .env
```

**Minimal .env for testing:**
```env
SECRET_KEY=dev-secret-key-change-in-production
MAIL_SUPPRESS_SEND=True
PAYMENT_GATEWAY=mock
```

### Step 3: Initialize Database
```powershell
# Run database migration to add payment fields
python migrate_add_payment_fields.py
```

Expected output:
```
✓ Added payment_status column
✓ Added payment_transaction_id column
✅ Database migration completed successfully!
```

### Step 4: Run Tests (Optional)
```powershell
# Verify everything works
python test_enhancements.py
```

Expected output:
```
============================================================
ALL ENHANCEMENT TESTS COMPLETED SUCCESSFULLY
============================================================

✓ Global Search: WORKING
✓ Payment Processing: WORKING
✓ Order Integration: WORKING
✓ Routes: REGISTERED
✓ Configuration: VERIFIED
✓ Forms: VALIDATED
✓ Models: ENHANCED
```

### Step 5: Start Application
```powershell
# Run development server
python run.py
```

Application will be available at:
- **URL:** http://localhost:5000
- **Admin:** Create account and set role to "Admin" in database

---

## 🎯 Key Features to Test

### 1. Global Search
1. Navigate to any page
2. Use search bar in navigation
3. Search for "wheat" or any keyword
4. Try filtering by module (Forum, Blog, Shop, Consultants)

**Test URL:** http://localhost:5000/search/?q=wheat

### 2. E-Commerce with Payment
1. Browse shop: http://localhost:5000/shop
2. Add products to cart
3. Go to checkout: http://localhost:5000/checkout
4. Complete order with mock payment
5. Check email confirmation (if MAIL_SUPPRESS_SEND=False)

**Payment Methods:**
- **Card:** Uses mock gateway (always succeeds)
- **COD:** Cash on Delivery option

### 3. Blog System
1. Browse blog: http://localhost:5000/blog
2. Create new post (login required)
3. Upload media files (images, videos, PDFs)
4. Test file validation (try uploading .exe - should fail)

### 4. Forum
1. Browse forum: http://localhost:5000/forum
2. Create new thread
3. Post replies
4. Search forum posts via global search

---

## 🛠️ Common Issues & Solutions

### Issue: "No module named 'agrifarma'"
**Solution:**
```powershell
# Make sure you're in the correct directory
cd flask-datta-able-master

# Verify structure
dir agrifarma
```

### Issue: "Table orders has no column named payment_status"
**Solution:**
```powershell
# Run the migration script
python migrate_add_payment_fields.py
```

### Issue: "SMTP connection error"
**Solution:**
```env
# In .env file, set:
MAIL_SUPPRESS_SEND=True
```

### Issue: "Search results not showing"
**Solution:**
1. Make sure you have data in the database
2. Run seed data script (if available):
```powershell
python seed_data.py
```

### Issue: "Payment fails in production"
**Solution:**
Configure real payment gateway in `.env`:
```env
PAYMENT_GATEWAY=stripe
STRIPE_API_KEY=your_key_here
STRIPE_PUBLISHABLE_KEY=your_public_key_here
```

---

## 📊 Database Schema Updates

New columns added to `orders` table:
- `payment_status` (VARCHAR 16) - Values: Pending/Paid/Failed/Refunded
- `payment_transaction_id` (VARCHAR 128) - Stores transaction IDs

---

## 🔐 Default Configuration

### Development Mode (default)
- **Database:** SQLite (instance/agrifarma.db)
- **Email:** Suppressed (no actual emails sent)
- **Payment:** Mock gateway (always succeeds)
- **Debug:** Enabled
- **Port:** 5000

### Production Mode (when deploying)
Update `.env`:
```env
FLASK_ENV=production
SECRET_KEY=generate-strong-random-key
DATABASE_URL=postgresql://user:pass@host/db
MAIL_SUPPRESS_SEND=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
PAYMENT_GATEWAY=stripe  # or jazzcash
```

---

## 📝 Quick Reference

### Important URLs
- **Home:** http://localhost:5000/
- **Login:** http://localhost:5000/login
- **Register:** http://localhost:5000/register
- **Shop:** http://localhost:5000/shop
- **Blog:** http://localhost:5000/blog
- **Forum:** http://localhost:5000/forum
- **Search:** http://localhost:5000/search/
- **Admin:** http://localhost:5000/admin (requires Admin role)

### Test Accounts
Create accounts via registration, then manually set role in database:
```sql
UPDATE users SET role = 'Admin' WHERE email = 'your-email@example.com';
```

### File Structure
```
flask-datta-able-master/
├── agrifarma/              # Main application package
│   ├── routes/             # URL routes/blueprints
│   ├── models/             # Database models
│   ├── services/           # Business logic services
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── tests/                  # Test suite
├── instance/               # Database files (created automatically)
├── run.py                  # Application entry point
├── config.py               # Configuration classes
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (create this)
```

---

## 🧪 Testing Checklist

- [ ] Application starts without errors
- [ ] Database migration completes successfully
- [ ] All tests pass (run `test_enhancements.py`)
- [ ] Can register new user
- [ ] Can login
- [ ] Global search works
- [ ] Can create blog post
- [ ] Can upload files
- [ ] Can browse shop
- [ ] Can add to cart
- [ ] Can complete checkout
- [ ] Payment processes successfully
- [ ] Email confirmation received (if enabled)

---

## 📚 Additional Resources

- **Full Documentation:** See `CORE_ENHANCEMENTS_COMPLETE.md`
- **SRS Requirements:** See `docs/AGRIFARMA_SRS_EXTRACT.md`
- **Implementation Summary:** See `PARTIAL_IMPLEMENTATION_COMPLETE.md`

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** in terminal where server is running
2. **Review configuration** in `.env` and `config.py`
3. **Run tests** to identify specific issues: `python test_enhancements.py`
4. **Check database** - make sure migration ran: `python migrate_add_payment_fields.py`

---

## ✅ Success Indicators

You'll know everything is working when:
- ✅ All tests pass (7/7 test categories)
- ✅ Server starts on http://localhost:5000
- ✅ Search returns results
- ✅ Checkout creates orders with payment status
- ✅ No errors in terminal/console

---

*Quick Start Guide - AgriFarma v1.0*
*Last Updated: November 12, 2025*
