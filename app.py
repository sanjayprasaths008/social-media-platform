"""
LOOP - Mini Social Media Platform (Flask)
-----------------------------------------
Features:
- User profiles (bio, stats)
- Posts + comments
- Like system
- Follow/unfollow system

Run with: python app.py
Then open: http://127.0.0.1:5000

Demo accounts (see README): alice / raj / meera, all with password "password123"
"""

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'


# ---------------------------------------------------------
# Database Models
# ---------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def avatar_class(self):
        """Rotates through 4 accent colors based on user id, so avatars
        aren't all the same color when there's no real photo upload."""
        return f"avatar-{self.id % 4}"

    @property
    def posts_count(self):
        return Post.query.filter_by(user_id=self.id).count()

    @property
    def followers_count(self):
        return Follow.query.filter_by(followed_id=self.id).count()

    @property
    def following_count(self):
        return Follow.query.filter_by(follower_id=self.id).count()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='posts')

    @property
    def like_count(self):
        return Like.query.filter_by(post_id=self.id).count()

    @property
    def comment_count(self):
        return Comment.query.filter_by(post_id=self.id).count()


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='comments')


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uq_like'),)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   # the one clicking "Follow"
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   # the one being followed
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='uq_follow'),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------
# Template helpers (available in every Jinja template)
# ---------------------------------------------------------
def user_liked(post, user):
    if not user.is_authenticated:
        return False
    return Like.query.filter_by(post_id=post.id, user_id=user.id).first() is not None


def is_following(follower, followed):
    if not follower.is_authenticated:
        return False
    return Follow.query.filter_by(follower_id=follower.id, followed_id=followed.id).first() is not None


def time_ago(dt):
    diff = datetime.utcnow() - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return 'just now'
    minutes = int(seconds // 60)
    if minutes < 60:
        return f'{minutes}m ago'
    hours = int(minutes // 60)
    if hours < 24:
        return f'{hours}h ago'
    days = int(hours // 24)
    if days < 7:
        return f'{days}d ago'
    weeks = int(days // 7)
    if weeks < 5:
        return f'{weeks}w ago'
    return dt.strftime('%d %b %Y')


app.jinja_env.globals['user_liked'] = user_liked
app.jinja_env.globals['is_following'] = is_following
app.jinja_env.filters['timeago'] = time_ago


# ---------------------------------------------------------
# Routes: Feed + Posts
# ---------------------------------------------------------
@app.route('/')
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('feed.html', posts=posts)


@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content', '').strip()
    if content:
        db.session.add(Post(user_id=current_user.id, content=content))
        db.session.commit()
        flash('Post shared to your loop.', 'success')
    else:
        flash("A post can't be empty.", 'warning')
    return redirect(url_for('feed'))


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return render_template('post_detail.html', post=post, comments=comments)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id == current_user.id:
        Comment.query.filter_by(post_id=post.id).delete()
        Like.query.filter_by(post_id=post.id).delete()
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', 'info')
    return redirect(url_for('feed'))


# ---------------------------------------------------------
# Routes: Likes + Comments
# ---------------------------------------------------------
@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Like(post_id=post.id, user_id=current_user.id))
    db.session.commit()
    return redirect(request.referrer or url_for('feed'))


@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    if content:
        db.session.add(Comment(post_id=post.id, user_id=current_user.id, content=content))
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post.id))


# ---------------------------------------------------------
# Routes: Profiles + Follow
# ---------------------------------------------------------
@app.route('/profile/<username>')
def profile(username):
    profile_user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=profile_user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', profile_user=profile_user, posts=posts)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def toggle_follow(username):
    target = User.query.filter_by(username=username).first_or_404()
    if target.id == current_user.id:
        flash("You can't follow yourself.", 'warning')
        return redirect(url_for('profile', username=username))

    existing = Follow.query.filter_by(follower_id=current_user.id, followed_id=target.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Follow(follower_id=current_user.id, followed_id=target.id))
    db.session.commit()
    return redirect(request.referrer or url_for('profile', username=username))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio', '').strip()[:200]
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile', username=current_user.username))
    return render_template('edit_profile.html')


@app.route('/people')
def people():
    users = User.query.order_by(User.username.asc()).all()
    return render_template('people.html', users=users)


# ---------------------------------------------------------
# Routes: Auth
# ---------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        email = request.form['email'].strip()
        password = request.form['password']

        if not username.isalnum():
            flash('Username can only contain letters and numbers.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('That email is already registered.', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('feed'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('feed'))


# ---------------------------------------------------------
# Seed demo data so the feed isn't empty on first run
# ---------------------------------------------------------
def seed_data():
    if User.query.count() > 0:
        return

    demo_users = [
        User(username='alice', email='alice@example.com',
             bio='Design student. Coffee-powered.'),
        User(username='raj', email='raj@example.com',
             bio='Backend guy. Building things nobody asked for.'),
        User(username='meera', email='meera@example.com',
             bio='Photography + long walks + bad puns.'),
    ]
    for u in demo_users:
        u.set_password('password123')
    db.session.add_all(demo_users)
    db.session.commit()

    alice, raj, meera = demo_users

    posts = [
        Post(user_id=alice.id, content="Redesigned my portfolio site this weekend. Small changes, but they add up."),
        Post(user_id=raj.id, content="Finally fixed a bug that's been bothering me for three days. It was a missing semicolon."),
        Post(user_id=meera.id, content="Golden hour on the way back from campus today. Chennai skies showing off."),
        Post(user_id=alice.id, content="Does anyone have a good recommendation for a lightweight note-taking app?"),
        Post(user_id=raj.id, content="Started learning Flask this week. Small steps, but it's clicking."),
    ]
    db.session.add_all(posts)
    db.session.commit()

    db.session.add_all([
        Comment(post_id=posts[0].id, user_id=raj.id, content="Looks clean! What did you use for the layout?"),
        Comment(post_id=posts[1].id, user_id=meera.id, content="The classic. Happens to the best of us."),
        Comment(post_id=posts[2].id, user_id=alice.id, content="This is beautiful, where was this taken?"),
    ])

    db.session.add_all([
        Like(post_id=posts[0].id, user_id=raj.id),
        Like(post_id=posts[0].id, user_id=meera.id),
        Like(post_id=posts[2].id, user_id=alice.id),
    ])

    db.session.add_all([
        Follow(follower_id=alice.id, followed_id=raj.id),
        Follow(follower_id=alice.id, followed_id=meera.id),
        Follow(follower_id=raj.id, followed_id=alice.id),
        Follow(follower_id=meera.id, followed_id=alice.id),
    ])

    db.session.commit()
    print('Demo users, posts, comments, likes, and follows added.')


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
