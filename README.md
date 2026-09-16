# LOOP — Mini Social Media Platform (Flask)

Task 2 of the CodeAlpha internship: a social media app with profiles, posts,
comments, likes, and follows.

## Features
- User profiles (bio, avatar, stats: posts / followers / following)
- Posts (create, delete your own)
- Comments (threaded under each post)
- Like system (toggle, live count)
- Follow / unfollow system
- People page to discover and follow other users
- Auth: register/login (Flask-Login, hashed passwords)

## Design
Custom look (not a template): warm paper background, one violet accent,
"loop ring" avatars — the ring around someone's avatar lights up violet
once you follow them, everywhere they appear (feed, comments, profile,
people page). Comments are connected to the post by a vertical thread
line, echoing the "loop" idea of connected people.

## Tech stack
- Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login
- Database: SQLite (`loop.db`, created automatically)
- Frontend: HTML + a hand-written CSS design system (`static/style.css`,
  no framework) + Google Fonts (Sora, Inter, Space Mono)

## How to run it

1. Open a terminal in this folder (`loop`).
2. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open your browser at: http://127.0.0.1:5000

## Demo accounts
The first run seeds 3 demo users with posts, comments, likes, and follows
already set up between them, so the feed isn't empty and you can test the
follow/like/comment features immediately:

| username | password    |
|----------|-------------|
| alice    | password123 |
| raj      | password123 |
| meera    | password123 |

Log in as one, follow/comment as another (open a second browser or an
incognito window to be logged in as two accounts at once), and watch the
loop ring, like count, and comment thread update.

You can also just register your own account from the Sign Up page.

## Project structure
```
loop/
├── app.py                    <- all backend logic (models, routes)
├── requirements.txt
├── templates/
│   ├── base.html              <- nav + layout
│   ├── macros.html            <- reusable post-card component
│   ├── feed.html               <- home feed + compose box
│   ├── post_detail.html        <- single post + comment thread
│   ├── profile.html            <- user profile page
│   ├── people.html             <- discover/follow other users
│   ├── login.html
│   ├── register.html
│   └── edit_profile.html
└── static/
    └── style.css              <- entire design system (CSS variables at top)
```

## Notes for beginners
- Likes and follows use a database `UniqueConstraint` so a user can't
  like/follow the same thing twice by accident.
- `avatar_class` and `stock_bars`-style computed properties live on the
  model itself (`app.py`) so templates stay simple — they just read
  `user.avatar_class`, they don't calculate anything.
- Fonts load from Google Fonts via CDN — needs internet on first page
  load. Offline, it falls back to the default system sans-serif; nothing
  breaks.

## Ideas to extend later
- Image uploads for posts and profile pictures
- Notifications when someone follows/likes/comments
- Search for users or posts
- Pagination for long feeds
