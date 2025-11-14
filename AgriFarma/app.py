# -*- coding: utf-8 -*-
from agrifarma import create_app
import click
from flask.cli import with_appcontext
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.profile import Profile
from werkzeug.security import generate_password_hash

app = create_app("config.DevelopmentConfig")


@app.cli.command('create-admin')
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--name', prompt=True, help='Admin full name')
@with_appcontext
def create_admin(email, password, name):
    """Create a new admin user with full privileges."""
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo(click.style(f"❌ Error: User with email {email} already exists!", fg='red'))
        if existing_user.role == 'Admin':
            click.echo(click.style(f"   This user is already an Admin.", fg='yellow'))
        else:
            if click.confirm(f"   Promote {email} (currently {existing_user.role}) to Admin?"):
                existing_user.role = 'Admin'
                db.session.commit()
                click.echo(click.style(f"✅ User promoted to Admin successfully!", fg='green'))
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
        name=name
    )
    db.session.add(profile)
    db.session.commit()
    
    click.echo(click.style("✅ Admin user created successfully!", fg='green'))
    click.echo(f"   Email: {email}")
    click.echo(f"   Name: {name}")
    click.echo(f"   Role: Admin")
    click.echo(click.style("\n🔐 You can now login with these credentials.", fg='cyan'))


@app.cli.command('list-admins')
@with_appcontext
def list_admins():
    """List all admin users."""
    admins = User.query.filter_by(role='Admin').all()
    if not admins:
        click.echo(click.style("No admin users found.", fg='yellow'))
        return
    
    click.echo(click.style(f"\n📋 Admin Users ({len(admins)}):", fg='cyan'))
    click.echo("─" * 60)
    for admin in admins:
        status = "🟢 Active" if admin.is_active else "🔴 Inactive"
        name = admin.profile.name if admin.profile and admin.profile.name else "N/A"
        click.echo(f"{status} | {admin.email:30} | {name}")
    click.echo("─" * 60)


if __name__ == "__main__":
    app.run()

