# Mini Social Media Platform

A basic full-stack social media web application developed as part of my Full Stack Development Internship at CodeAlpha.

The application allows users to create profiles, share posts, interact through likes and comments, and follow other users.

## 🚀 Features

- 👤 User registration and login
- 🧑‍💻 User profiles
- 📝 Create and publish posts
- 💬 Comment on posts
- ❤️ Like posts
- 👥 Follow and unfollow users
- 📰 Social media feed
- 🔐 User authentication
- 🗄️ Database for users, posts, comments, and followers

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Django (Python)

### Database
- SQLite

## 📂 Project Structure

```text
social-media-platform/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── socialmedia/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── posts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── create_post.html
│   └── post_detail.html
│
└── static/
    ├── css/
    ├── js/
    └── images/
