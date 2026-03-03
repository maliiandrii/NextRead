"""
Seed script: creates tables, admin user, sample books and genres.
Run once: python seed.py
"""
from app import create_app, db
from app.models import User, UserProfile, Book, Genre, Borrowing
from datetime import date

app = create_app('development')

with app.app_context():
    db.create_all()

    # --- Genres ---
    genre_names = [
        ('Fiction', 'Literary fiction and novels'),
        ('Science Fiction', 'Futuristic science and technology'),
        ('Classic', 'Timeless classic literature'),
        ('Fantasy', 'Magic and imaginary worlds'),
        ('Non-Fiction', 'Factual and informational books'),
    ]
    genres = {}
    for name, desc in genre_names:
        g = Genre.query.filter_by(name=name).first()
        if not g:
            g = Genre(name=name, description=desc)
            db.session.add(g)
        genres[name] = g
    db.session.flush()

    # --- Admin user ---
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@library.com',
                     full_name='Administrator', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        db.session.add(UserProfile(user_id=admin.id, bio='Library administrator'))

    # --- Regular users ---
    for uname, email, fullname in [
        ('john_doe', 'john@example.com', 'John Doe'),
        ('jane_smith', 'jane@example.com', 'Jane Smith'),
    ]:
        if not User.query.filter_by(username=uname).first():
            u = User(username=uname, email=email, full_name=fullname)
            u.set_password('user123')
            db.session.add(u)
            db.session.flush()
            db.session.add(UserProfile(user_id=u.id))

    # --- Books ---
    books_data = [
        {
            'title': 'To Kill a Mockingbird', 'author': 'Harper Lee',
            'isbn': '978-0-06-112008-4', 'published_year': 1960,
            'description': 'A story of racial injustice and loss of innocence in the American South.',
            'quantity': 5, 'genres': ['Classic', 'Fiction'],
        },
        {
            'title': '1984', 'author': 'George Orwell',
            'isbn': '978-0-45-228423-4', 'published_year': 1949,
            'description': 'A dystopian social science fiction novel.',
            'quantity': 3, 'genres': ['Fiction', 'Science Fiction'],
        },
        {
            'title': 'Pride and Prejudice', 'author': 'Jane Austen',
            'isbn': '978-0-14-143951-8', 'published_year': 1813,
            'description': 'A romantic novel of manners.',
            'quantity': 4, 'genres': ['Classic', 'Fiction'],
        },
        {
            'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald',
            'isbn': '978-0-74-323562-5', 'published_year': 1925,
            'description': 'A story of wealth, idealism, and the American Dream.',
            'quantity': 2, 'genres': ['Classic', 'Fiction'],
        },
        {
            'title': 'Harry Potter and the Philosopher\'s Stone',
            'author': 'J.K. Rowling', 'isbn': '978-0-74-753269-9',
            'published_year': 1997,
            'description': 'The beginning of the magical adventures of Harry Potter.',
            'quantity': 6, 'genres': ['Fantasy', 'Fiction'],
        },
        {
            'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger',
            'isbn': '978-0-31-676948-0', 'published_year': 1951,
            'description': 'Coming-of-age story of Holden Caulfield.',
            'quantity': 3, 'genres': ['Classic', 'Fiction'],
        },
        {
            'title': 'The Lord of the Rings', 'author': 'J.R.R. Tolkien',
            'isbn': '978-0-61-800222-1', 'published_year': 1954,
            'description': 'An epic fantasy adventure in Middle-earth.',
            'quantity': 4, 'genres': ['Fantasy'],
        },
    ]

    for bdata in books_data:
        if not Book.query.filter_by(isbn=bdata['isbn']).first():
            book = Book(
                title=bdata['title'], author=bdata['author'],
                isbn=bdata['isbn'], published_year=bdata['published_year'],
                description=bdata['description'],
                quantity=bdata['quantity'], available=bdata['quantity'],
            )
            book.genres = [genres[g] for g in bdata['genres'] if g in genres]
            db.session.add(book)

    db.session.commit()
    print("✅ Database seeded successfully!")
    print("   Admin:  username=admin   password=admin123")
    print("   User 1: username=john_doe  password=user123")
    print("   User 2: username=jane_smith password=user123")
