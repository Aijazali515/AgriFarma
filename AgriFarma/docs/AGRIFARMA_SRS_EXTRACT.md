# AGRIFARMA SRS — Slide Text Extract

## Slide 1

Project Title: AgriFarma
Farmers’ Digital Hub

## Slide 2

1. Introduction
1.1 Purpose
AgriFarma aims to create a digital platform for farmers where they can:
Gain agricultural knowledge
Connect with consultants and experts
Share success stories and advice
Buy and sell agricultural products online
This web platform serves as a one-stop portal for agriculture-related learning, collaboration, and commerce in Sindh, Pakistan.

## Slide 3

1.2 Target Users
👨‍🌾 Farmers – to gain knowledge, share experiences, and sell produce
👩‍🔬 Consultants / Experts – to offer paid or voluntary consultancy
🧑‍🏫 Academics / Students – to post research and educational content
🛒 Buyers / Sellers – for agricultural e-commerce

## Slide 4

⚙️ 2. System Features
2.1 User Profiles
Register, login, and reset password
Profile fields: Name, Email, Mobile, Location(City, State, Country), Profession, level of expertise (expert, intermediate, beginner), Picture
View join date, number of posts, likes, latest posts
Edit profile and change password

## Slide 5

2.2 Discussion Forum
Categories & subcategories (e.g., Crops → Wheat → Diseases)
Start threads, post replies, and search discussions
Admin moderation: delete/move inappropriate posts
Latest discussions displayed in sidebar

## Slide 6

2.3 Knowledge Base (Blogs)
Post blogs with multimedia (images, video, PPT, docs)
Categorized (e.g., Success Stories, Techniques, Weather Tips)
Commenting system
Admin approval & removal of inappropriate content
Search functionality + sidebar for trending articles

## Slide 7

2.4 Consultancy Services
Users can register as consultants
Admin reviews & approves profiles
Consultancy listed by category (e.g., soil, irrigation, crop disease)
Contact option via message or email

## Slide 8

2.5 E-Commerce (Agri Marketplace)
Farmers and Admins can post items for sale
Product info: name, price, images, category, description
Shopping cart system (add/edit/remove items)
Orders, payments, and shipping options
Admin dashboard:
Add/remove products
Approve/delete reviews
Manage orders & view reports
Date-range sales report, low inventory alert

## Slide 9

💾 3. Technology Stack

## Slide 10

🧠 4. Functional Modules

## Slide 11

🧱 5. Project Folder Structure

## Slide 12

🗓️ 6. 5-Day Roadmap (Milestone Plan)
🧩 Day 1 — Project Setup & User Authentication
Goal: Establish base Flask app and user managementTasks:
Create project structure and virtual environment
Setup Flask, Flask-Login, Flask-WTF, and SQLite database
Build User model (name, email, password, role, expertise)
Implement routes: /register, /login, /logout
Create templates for authentication
Add session handling & password hashing✅ Output: Fully working user login/register module

## Slide 13

💬 Day 2 — Discussion Forum & Knowledge Base
Goal: Implement forum & blog systemTasks:
Create models: Category, Post, Comment
Routes for:
Add new post (category-based)
Reply/comment
Admin: delete/move posts
Implement blog system with multimedia upload (Flask-Uploads)
Add search bar and sidebar for latest posts✅ Output: Working forum and knowledge base with post/comment functionality

## Slide 14

🤝 Day 3 — Consultancy & Profile Module
Goal: Build consultant registration and profile systemTasks:
Add Consultant model (category, expertise, contact info)
Consultant registration form
Admin approval panel
Update user profile view: show posts, join date, likes, etc.✅ Output: Consultant profiles visible on public directory

## Slide 15

🛒 Day 4 — E-Commerce Module
Goal: Add marketplace for products & ordersTasks:
Create Product, Order, Cart models
Admin: add/remove/update products
Farmer: post produce for sale
User: add to cart, view order history
Implement search, sort, and filtering (using Pandas)✅ Output: Working buy/sell functionality with data persistence

## Slide 16

📊 Day 5 — Admin Panel, Reports & Testing
Goal: Integrate all modules + polish interfaceTasks:
Build Admin dashboard (view stats, manage users, products)
Generate reports using Pandas:
Top-selling products
Low inventory
New users by date
Add error handling for invalid input and missing files
Final testing and responsive design polishing✅ Output: Complete web application ready for demo/deployment

## Slide 17

🧩 7. Data Collection & Management

