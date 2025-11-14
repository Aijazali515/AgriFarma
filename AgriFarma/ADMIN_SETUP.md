# AgriFarma - Admin Account Setup Guide

## Creating Administrator Accounts

AgriFarma uses role-based access control. By default, newly registered users have the `User` role. To create administrator accounts, you have three options:

---

## Method 1: Flask Shell (Recommended for First Admin)

Use the Flask shell to directly promote an existing user to Admin:

```bash
# Start the Flask shell
flask shell

# Or using Python
python app.py shell
```

Then run the following commands:

```python
from agrifarma.extensions import db
from agrifarma.models.user import User

# Find the user by email
user = User.query.filter_by(email='admin@example.com').first()

# Promote to Admin
if user:
    user.role = 'Admin'
    db.session.commit()
    print(f"✅ {user.email} is now an Admin!")
else:
    print("❌ User not found!")
```

---

## Method 2: Direct Database Update (SQLite)

If you're using SQLite (default), you can update the database directly:

```bash
# Open the database
sqlite3 agrifarma.db

# View current users
SELECT id, email, role FROM users;

# Promote user to Admin (replace 1 with the user's ID)
UPDATE users SET role = 'Admin' WHERE id = 1;

# Verify the change
SELECT id, email, role FROM users;

# Exit
.quit
```

---

## Method 3: Registration Modification (Development Only)

For development/testing, you can temporarily modify the registration route to create admin accounts:

**⚠️ WARNING: Never use this in production!**

Edit `agrifarma/routes/auth.py` temporarily:

```python
# In the register route, after creating the user:
new_user = User(email=email, password_hash=hashed_password)

# Add this line temporarily:
new_user.role = 'Admin'  # ONLY FOR FIRST ADMIN - REMOVE AFTER USE

db.session.add(new_user)
db.session.commit()
```

**Remember to remove this line after creating your first admin!**

---

## Method 4: CLI Command (Recommended for Production)

Create a custom Flask CLI command for admin creation. Add this to `app.py` or create `manage.py`:

```python
import click
from flask.cli import with_appcontext
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from werkzeug.security import generate_password_hash

@click.command('create-admin')
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--name', prompt=True, help='Admin full name')
@with_appcontext
def create_admin(email, password, name):
    """Create a new admin user."""
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo(f"❌ Error: User with email {email} already exists!")
        return
    
    # Create new admin user
    hashed_password = generate_password_hash(password)
    new_admin = User(
        email=email,
        password_hash=hashed_password,
        role='Admin',
        is_active=True
    )
    db.session.add(new_admin)
    db.session.flush()  # Get the user ID
    
    # Create profile
    profile = Profile(
        user_id=new_admin.id,
        full_name=name
    )
    db.session.add(profile)
    db.session.commit()
    
    click.echo(f"✅ Admin user created successfully!")
    click.echo(f"   Email: {email}")
    click.echo(f"   Name: {name}")
    click.echo(f"   Role: Admin")

# Register the command
app.cli.add_command(create_admin)
```

Then use it:

```bash
flask create-admin
# Follow the prompts to enter email, password, and name
```

---

## Verifying Admin Access

After creating an admin account:

1. **Login** with the admin credentials
2. **Check the sidebar** - You should see an "Administration" section with:
   - Admin Dashboard
   - User Management
   - Moderation
   - Reports
3. **Navigate to** `/admin` - You should see the admin analytics dashboard

---

## Available Roles

The AgriFarma platform supports the following roles:

| Role | Description | Access Level |
|------|-------------|--------------|
| `User` | Default role for registered users | Community features, shop, forum, consultancy |
| `Consultant` | Users approved as agricultural consultants | All User features + consultant profile |
| `Admin` | Platform administrators | Full access to all features + moderation tools |

---

## Role Permissions Summary

### Regular Users Can:
- Browse and participate in forums
- Read approved blog posts
- Create blog posts (subject to moderation)
- Contact consultants
- Purchase products
- Leave reviews
- View community dashboard

### Admins Can (in addition to User permissions):
- Access admin dashboard with analytics
- Manage all users (activate/deactivate)
- Moderate blog posts (approve/reject/delete)
- Moderate products (approve/delete)
- Review consultant applications
- View detailed reports and analytics
- Manage orders and inventory
- Access all admin routes under `/admin/*`

---

## Security Best Practices

1. **Use strong passwords** for admin accounts (min 12 characters, mixed case, numbers, symbols)
2. **Limit admin accounts** - Only promote trusted users
3. **Regular audits** - Periodically review admin access via User Management
4. **Separate accounts** - Don't use admin accounts for daily community participation
5. **Enable logging** - Monitor admin actions (future feature)

---

## Troubleshooting

### "I can't see the admin menu"
- Verify your role is exactly `Admin` (case-sensitive)
- Clear browser cache and re-login
- Check the database: `SELECT role FROM users WHERE email = 'your@email.com';`

### "403 Forbidden when accessing /admin"
- Your role is not set to `Admin`
- Use one of the methods above to promote your account

### "I forgot the admin password"
Reset it via Flask shell:

```python
from agrifarma.extensions import db
from agrifarma.models.user import User
from werkzeug.security import generate_password_hash

user = User.query.filter_by(email='admin@example.com').first()
user.password_hash = generate_password_hash('new_secure_password')
db.session.commit()
```

---

## Quick Reference Commands

```bash
# Method 1: Flask Shell
flask shell
>>> from agrifarma.models.user import User
>>> from agrifarma.extensions import db
>>> user = User.query.filter_by(email='user@example.com').first()
>>> user.role = 'Admin'
>>> db.session.commit()

# Method 2: SQLite Direct
sqlite3 agrifarma.db
sqlite> UPDATE users SET role = 'Admin' WHERE email = 'user@example.com';

# Method 4: CLI Command (if implemented)
flask create-admin
```

---

For more information, see the main [README.md](README.md) or visit the AgriFarma documentation.
