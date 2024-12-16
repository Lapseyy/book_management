from database import SessionLocal, Book

def populate_books():
    db = SessionLocal()
    books = [
        {"title": "1984", "author": "George Orwell", "publication_year": 1949, "isbn": "1234567890123", "price": 10.99},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "publication_year": 1960, "isbn": "1234567890124", "price": 10.99},
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "publication_year": 1925, "isbn": "1234567890125", "price": 12.99},
        {"title": "Pride and Prejudice", "author": "Jane Austen", "publication_year": 1813, "isbn": "1234567890126", "price": 9.99},
        {"title": "The Shining", "author": "Stephen King", "publication_year": 1977, "isbn": "1234567890127", "price": 14.99},
        {"title": "Pet Sematary", "author": "Stephen King", "publication_year": 1983, "isbn": "1234567890128", "price": 13.99},
        {"title": "It", "author": "Stephen King", "publication_year": 1986, "isbn": "1234567890129", "price": 18.99},
        {"title": "Carrie", "author": "Stephen King", "publication_year": 1974, "isbn": "1234567890130", "price": 12.99},
        {"title": "Misery", "author": "Stephen King", "publication_year": 1987, "isbn": "1234567890131", "price": 14.49},
        {"title": "The Stand", "author": "Stephen King", "publication_year": 1978, "isbn": "1234567890132", "price": 19.99},
        {"title": "Salem's Lot", "author": "Stephen King", "publication_year": 1975, "isbn": "1234567890133", "price": 13.49},
        {"title": "Doctor Sleep", "author": "Stephen King", "publication_year": 2013, "isbn": "1234567890134", "price": 15.99},
        {"title": "Christine", "author": "Stephen King", "publication_year": 1983, "isbn": "1234567890135", "price": 12.99}
    ]
    try:
        for book_data in books:
            book = Book(**book_data) 
            db.add(book)
        db.commit()
        print("Books populated successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error populating books: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_books()
