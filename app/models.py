from datetime import datetime
from flask_login import UserMixin
import bcrypt
from app import db, login_manager


# Many-to-many: users can have favorite genres, genres can have many users
user_favorite_genres = db.Table(
    'user_favorite_genres',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

# Many-to-many: books can have multiple genres
book_genres = db.Table(
    'book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    # many-to-many with books
    books = db.relationship('Book', secondary=book_genres, back_populates='genres')
    # many-to-many with users (favorites)
    fans = db.relationship('User', secondary=user_favorite_genres, back_populates='favorite_genres')

    def __repr__(self):
        return f'<Genre {self.name}>'


class UserProfile(db.Model):
    """One-to-one relationship with User"""
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    avatar_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='profile')

    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    hashed_password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150))
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-one: profile
    profile = db.relationship('UserProfile', back_populates='user',
                               uselist=False, cascade='all, delete-orphan')
    # One-to-many: borrowings
    borrowings = db.relationship('Borrowing', back_populates='user',
                                  cascade='all, delete-orphan', lazy='dynamic')
    # Many-to-many: favorite genres
    favorite_genres = db.relationship('Genre', secondary=user_favorite_genres,
                                       back_populates='fans')

    def set_password(self, password):
        self.hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.hashed_password.encode('utf-8')
        )

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_active_borrowings_count(self):
        return self.borrowings.filter_by(status='borrowed').count()

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True, index=True)
    published_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-many: borrowings
    borrowings = db.relationship('Borrowing', back_populates='book',
                                  cascade='all, delete-orphan', lazy='dynamic')
    # Many-to-many: genres
    genres = db.relationship('Genre', secondary=book_genres, back_populates='books')

    def __repr__(self):
        return f'<Book {self.title}>'


class Borrowing(db.Model):
    __tablename__ = 'borrowings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='borrowed')  # 'borrowed' or 'returned'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='borrowings')
    book = db.relationship('Book', back_populates='borrowings')

    def __repr__(self):
        return f'<Borrowing user={self.user_id} book={self.book_id}>'
