from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Database connection setup toi MySQL
DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/book_management"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# gets the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define Book table
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False)
    isbn = Column(String(13), unique=True, nullable=False)
    price = Column(Float, nullable=False)

# Ensure database tables are created
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI()

# Pydantic model for Book validation
class BookCreate(BaseModel):
    title: str
    author: str
    publication_year: int
    isbn: str
    price: float
    
# Pydantic model created the reponse for CRUD action of Books validations
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    publication_year: int
    isbn: str
    price: float

    class Config:
        from_attributes = True  # Tells Pydantic to handle ORM objects



# post the book information
@app.post("/books/", response_model=dict)
def create_book(book: BookCreate, db: SessionLocal = Depends(get_db)):
    new_book = Book(
        title=book.title,
        author=book.author,
        publication_year=book.publication_year,
        isbn=book.isbn,
        price=book.price
    )
    try:
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        # Convert to BookResponse
        return {"message": "Book created successfully.", "book": BookResponse.from_orm(new_book)}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# This is to update existing content. You have to put all the information on and make sure that it is accurate.
@app.put("/books/{book_id}", response_model=dict)
def update_book(book_id: int, book: BookCreate, db: SessionLocal = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found.")
    # calling to db and inserting information
    db_book.title = book.title
    db_book.author = book.author
    db_book.publication_year = book.publication_year
    db_book.isbn = book.isbn
    db_book.price = book.price
    
    db.commit()
    db.refresh(db_book)
    # Convert to BookResponse
    return {"message": "Book updated successfully.", "book": BookResponse.from_orm(db_book)}


#Get all the book details in the database
@app.get("/books/", response_model=list[BookResponse])
def list_books(db: SessionLocal = Depends(get_db)):
    books = db.query(Book).all()
    return books

# Get the id of a certain book with its details
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: SessionLocal = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    return book

# This is for the web
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Book Management API. Use /books/ to manage books."}

# This is to update exisiting content. You have to put all the information on and make sure that it is accurate.
# @app.put("/books/{book_id}", response_model=dict)
# def update_book(book_id: int, book: BookCreate, db: SessionLocal = Depends(get_db)):
#     db_book = db.query(Book).filter(Book.id == book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not found.")
#     # calling to db and inserting information
#     db_book.title = book.title
#     db_book.author = book.author
#     db_book.publication_year = book.publication_year
#     db_book.isbn = book.isbn
#     db_book.price = book.price
    
#     db.commit()
#     db.refresh(db_book)
#     # Returns in the body of what is accompished. 
#     return {"message": "Book updated successfully.", "book": {
#         "id": db_book.id,
#         "title": db_book.title,
#         "author": db_book.author,
#         "publication_year": db_book.publication_year,
#         "isbn": db_book.isbn,
#         "price": db_book.price
#     }}
    
# Deletes the book 
@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: SessionLocal = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found.")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully."}
