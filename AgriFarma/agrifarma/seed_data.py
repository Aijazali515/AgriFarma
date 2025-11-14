# -*- coding: utf-8 -*-
"""Development data seeder for AgriFarma.

Generates realistic sample data for:
- Users with profiles (farmer / consultant / academic / expert)
- Consultants (subset of users)
- Products with reviews
- Forum categories, threads and posts
- Blog posts with comments
- Orders with order items

Run via Flask CLI after app creation:
  flask seed --users 120 --products 180 --posts 300
or simply:
  flask seed

You can also clear all data first:
  flask seed --fresh
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Tuple

from werkzeug.security import generate_password_hash
from flask import current_app
from agrifarma.extensions import db

# Models
from agrifarma.models.user import User
from agrifarma.models.profile import Profile, PROFESSIONS, EXPERTISE_LEVELS
from agrifarma.models.consultancy import Consultant, CONSULTANT_CATEGORIES
from agrifarma.models.ecommerce import Product, Review, Order, OrderItem
from agrifarma.models.forum import Category as ForumCategory, Thread, Post
from agrifarma.models.blog import BlogPost, Comment, PREDEFINED_CATEGORIES

try:
    from faker import Faker
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Faker is required: pip install Faker") from exc

fake = Faker()
fake.seed_instance(42)

# -----------------------------
# Helpers
# -----------------------------

CURRENCIES = ["USD", "INR", "EUR", "PKR"]
PRODUCT_CATEGORIES = [
    "Seeds", "Fertilizers", "Pesticides", "Irrigation", "Tools",
    "Sensors", "Soil Amendments", "Greenhouse", "Machinery", "Packaging"
]
FORUM_CATEGORIES = [
    "Soil Health", "Irrigation", "Pests & Disease", "Market Rates",
    "Weather", "Machinery", "Sustainability", "Seed Selection"
]
TAGS = ["organic", "hydroponics", "precision", "sustainable", "climate", "yield", "finance", "agronomy"]


def _rand_price(a: int = 10, b: int = 500) -> Decimal:
    return Decimal(str(round(random.uniform(a, b), 2)))


def _create_users(n_farmers=60, n_consultants=25, n_academics=20, n_experts=15) -> Tuple[List[User], List[User], List[User], List[User]]:
    users: List[User] = []
    farmers: List[User] = []
    consultants_users: List[User] = []
    academics: List[User] = []
    experts: List[User] = []

    def new_user(role: str = "User") -> User:
        email = fake.unique.email()
        user = User(
            email=email,
            password_hash=generate_password_hash("password123"),
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()  # get id for profile
        return user

    def add_profile(user: User, profession: str, expertise: str | None = None) -> None:
        profile = Profile(
            user_id=user.id,
            name=fake.name(),
            mobile=fake.msisdn()[:12],
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            profession=profession,
            expertise_level=expertise or random.choice(list(EXPERTISE_LEVELS)),
        )
        db.session.add(profile)

    # Farmers
    for _ in range(n_farmers):
        u = new_user("User")
        add_profile(u, "farmer")
        users.append(u)
        farmers.append(u)

    # Consultants (with Consultant record)
    for _ in range(n_consultants):
        u = new_user("Consultant")
        expertise = random.choice(list(EXPERTISE_LEVELS))
        add_profile(u, "consultant", expertise)
        c = Consultant(
            user_id=u.id,
            category=random.choice(list(CONSULTANT_CATEGORIES)),
            expertise_level=expertise,
            contact_email=u.email,
            approval_status="Approved",
        )
        db.session.add(c)
        users.append(u)
        consultants_users.append(u)

    # Academics / Students (use profession=academic)
    for _ in range(n_academics):
        u = new_user("User")
        add_profile(u, "academic")
        users.append(u)
        academics.append(u)

    # Experts (mark expertise_level=expert)
    for _ in range(n_experts):
        u = new_user("User")
        add_profile(u, random.choice(["farmer", "academic", "consultant"]), "expert")
        users.append(u)
        experts.append(u)

    return farmers, consultants_users, academics, experts


def _create_forum(farmers: List[User], consultants: List[User], experts: List[User], threads_per_cat=8, posts_per_thread=5) -> None:
    authors_answer_pool = consultants + experts
    for name in FORUM_CATEGORIES:
        cat = ForumCategory(name=name)
        db.session.add(cat)
        db.session.flush()
        for _ in range(threads_per_cat):
            author = random.choice(farmers)
            t = Thread(
                title=fake.sentence(nb_words=7).rstrip('.'),
                category_id=cat.id,
                author_id=author.id,
                created_at=fake.date_time_between(start_date='-8M', end_date='-1d'),
            )
            db.session.add(t)
            db.session.flush()
            # First post (question)
            db.session.add(Post(
                thread_id=t.id,
                author_id=author.id,
                content=fake.paragraph(nb_sentences=3),
                created_at=t.created_at + timedelta(minutes=5)
            ))
            # Replies
            for i in range(posts_per_thread - 1):
                replier = random.choice(authors_answer_pool)
                db.session.add(Post(
                    thread_id=t.id,
                    author_id=replier.id,
                    content=fake.paragraph(nb_sentences=random.randint(2, 5)),
                    created_at=t.created_at + timedelta(hours=i + 1)
                ))


def _product_name() -> str:
    noun = random.choice(["Seeder", "Pump", "Sensor", "Nozzle", "Drip Kit", "Sprayer", "Fertilizer", "Soil Mix", "Tray", "Net"])
    prefix = random.choice(["Eco", "Agri", "Pro", "Smart", "Vital", "Green"])
    return f"{prefix} {noun} {fake.bothify(text='##')}"


def _create_products(sellers: List[User], n_per_seller=(2, 6)) -> List[Product]:
    products: List[Product] = []
    # Real product images available (product_1.jpg to product_22.jpg)
    available_images = [f"product_{i}.jpg" for i in [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,18,19,20,21,22]]
    image_index = 0
    
    for seller in sellers:
        for _ in range(random.randint(*n_per_seller)):
            # Cycle through available images
            img = available_images[image_index % len(available_images)]
            image_index += 1
            
            p = Product(
                name=_product_name(),
                description=fake.paragraph(nb_sentences=4),
                price=_rand_price(5, 999),
                category=random.choice(PRODUCT_CATEGORIES),
                images=img,  # Use real downloaded images
                inventory=random.randint(5, 200),
                seller_id=seller.id,
                status="Active",
                featured=random.random() < 0.15,
                created_at=fake.date_time_between(start_date='-6M', end_date='-1d'),
            )
            products.append(p)
            db.session.add(p)
    return products


def _create_reviews(products: List[Product], users: List[User]) -> None:
    for p in products:
        for _ in range(random.randint(0, 6)):
            reviewer = random.choice(users)
            if reviewer.id == p.seller_id:
                continue
            db.session.add(Review(
                product_id=p.id,
                user_id=reviewer.id,
                rating=random.randint(3, 5),
                comment=fake.sentence(nb_words=18),
                approved=True,
                created_at=fake.date_time_between(start_date=p.created_at, end_date='now'),
            ))


def _create_orders(buyers: List[User], products: List[Product], n_orders=40) -> None:
    for _ in range(n_orders):
        buyer = random.choice(buyers)
        order = Order(
            user_id=buyer.id,
            shipping_address=fake.address().replace('\n', ', '),
            payment_method=random.choice(["COD", "Card", "Wallet"]),
            status=random.choice(["Pending", "Paid", "Shipped"]),
            created_at=fake.date_time_between(start_date='-4M', end_date='now'),
            total_amount=Decimal('0.00'),
        )
        db.session.add(order)
        db.session.flush()
        items_total = Decimal('0')
        for _ in range(random.randint(1, 4)):
            prod = random.choice(products)
            qty = random.randint(1, 5)
            oi = OrderItem(order_id=order.id, product_id=prod.id, quantity=qty, unit_price=prod.price)
            db.session.add(oi)
            items_total += (prod.price * qty)
        order.total_amount = items_total


def _create_blog(authors: List[User], n_posts=30) -> None:
    # Real article images available
    available_images = [f"article_{i}.jpg" for i in [1,9,11,12,13,14,15,16,17,18,19,20,21]]
    image_index = 0
    
    for _ in range(n_posts):
        author = random.choice(authors)
        # Cycle through available images
        img = available_images[image_index % len(available_images)]
        image_index += 1
        
        post = BlogPost(
            title=fake.sentence(nb_words=6).rstrip('.'),
            content="\n\n".join(fake.paragraphs(nb=random.randint(3, 7))),
            category=random.choice(PREDEFINED_CATEGORIES),
            author_id=author.id,
            tags=",".join(sorted(set(random.choices(TAGS, k=random.randint(2, 4))))),
            media_files=img,  # Use real downloaded images
            approved=True,
            created_at=fake.date_time_between(start_date='-6M', end_date='-1d'),
        )
        db.session.add(post)
        db.session.flush()
        # Comments
        for _ in range(random.randint(0, 5)):
            db.session.add(Comment(
                blog_id=post.id,
                author_id=random.choice(authors).id,
                content=fake.sentence(nb_words=22),
                approved=True,
                created_at=post.created_at + timedelta(days=random.randint(0, 60))
            ))


# -----------------------------
# Public API
# -----------------------------

def clear_all() -> None:
    """Drop all existing rows (development only)."""
    current_app.logger.warning("Clearing all data (development only)")
    # Order is important due to FKs
    for model in [Comment, BlogPost, OrderItem, Order, Review, Product, Post, Thread, ForumCategory, Consultant, Profile, User]:
        db.session.query(model).delete()
    db.session.commit()


def seed_all(users_total: int | None = None, products_total: int | None = None) -> None:
    """Seed the database with a large set of realistic data."""
    # Create users by roles
    farmers, consultants, academics, experts = _create_users(
        n_farmers=60,
        n_consultants=25,
        n_academics=20,
        n_experts=15,
    )
    db.session.commit()

    # Forum: farmers ask, consultants/experts reply
    _create_forum(farmers, consultants, experts, threads_per_cat=8, posts_per_thread=5)
    db.session.commit()

    # Products by farmers + consultants
    sellers = farmers + consultants
    products = _create_products(sellers, n_per_seller=(2, 6))
    db.session.commit()

    # Reviews by all users
    everyone = farmers + consultants + academics + experts
    _create_reviews(products, everyone)
    db.session.commit()

    # Orders by a mix of users
    _create_orders(everyone, products, n_orders=45)
    db.session.commit()

    # Blog posts by experts + consultants (and some academics)
    blog_authors = experts + consultants + academics
    _create_blog(blog_authors, n_posts=35)
    db.session.commit()

    current_app.logger.info("Seeding complete: %s users, %s products, forum/blog/orders populated.",
                            len(everyone), len(products))
