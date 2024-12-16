from fastapi import FastAPI, HTTPException, Depends, Request, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection setup
DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/book_management"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define JWT secret key and algorithm for token encoding/decoding
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Function to authenticate a user using JWT token
def authenticate_user(user_id: int, token: str):
    try:
        # Decode the JWT token to validate its payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["user_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

# Pydantic model for user data validation
class User(BaseModel):
    id: int
    name: str
    username: str
    password: str
    email: EmailStr  # Validate email format

# SQLAlchemy model for database User table
class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

# Pydantic model for inventory item data validation
class Item(BaseModel):
    id: int
    name: str
    quantity: int
    capacity: int
    description: Optional[str] = None  # Optional field for item description
    price: float

# Endpoint to register a new user
@app.post("/register")
def user_register(user: User, db: SessionLocal = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail=f"Username {user.username} already exists.")
    new_user = DBUser(
        id=user.id,
        name=user.name,
        username=user.username,
        password=user.password,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully.", "user": user}

# Endpoint for user login
@app.post("/login")
def user_login(username: str, password: str, db: SessionLocal = Depends(get_db)):
    # Find user by username and password
    user = db.query(DBUser).filter(DBUser.username == username, DBUser.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Generate a JWT token for the user
    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    }, SECRET_KEY, algorithm=ALGORITHM)

    return {"message": "Login successful.", "token": token}

# Ensure database tables are created
Base.metadata.create_all(bind=engine)
