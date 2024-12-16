from fastapi import FastAPI, HTTPException, Depends, Request, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta
from functools import wraps
import uvicorn

# Sample placeholder for database and data handling
# This simulates a database structure for users and inventories
db = {
    "users": [],  # List to store user data
    "inventories": {}  # Dictionary to store inventories by user ID
}

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

# Pydantic model for inventory item data validation
class Item(BaseModel):
    id: int
    name: str
    quantity: int
    capacity: int
    description: Optional[str] = None  # Optional field for item description
    price: float

# Pydantic model for inventory structure
class Inventory(BaseModel):
    id: int
    db_type: str  # Type of database (e.g., SQL, MongoDB)
    items: List[Item]  # List of items in the inventory

# Endpoint to register a new user
@app.post("/register")
def user_register(user: User):
    # Check if username already exists
    if any(existing_user.username == user.username for existing_user in db["users"]):
        raise HTTPException(status_code=409, detail=f"Username {user.username} already exists.")
    db["users"].append(user)  # Add user to the database
    return {"message": "User registered successfully.", "user": user}

# Endpoint for user login
@app.post("/login")
def user_login(username: str, password: str):
    # Find user by username and password
    user = next((u for u in db["users"] if u.username == username and u.password == password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Generate a JWT token for the user
    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    }, SECRET_KEY, algorithm=ALGORITHM)

    return {"message": "Login successful.", "token": token}

# Endpoint to retrieve a user's inventory
@app.get("/inventory/{user_id}")
def get_inventory(user_id: int, token: str):
    authenticate_user(user_id, token)  # Validate user authentication
    inventory = db["inventories"].get(user_id, None)  # Get inventory for the user
    if not inventory:
        raise HTTPException(status_code=404, detail="No inventory found for this user.")
    return inventory

# Endpoint to add an item to a user's inventory
@app.post("/inventory/{user_id}")
def add_item(user_id: int, token: str, item: Item):
    authenticate_user(user_id, token)  # Validate user authentication
    if user_id not in db["inventories"]:
        db["inventories"][user_id] = []  # Initialize inventory if not present
    db["inventories"][user_id].append(item)  # Add item to inventory
    return {"message": "Item added successfully.", "item": item}

# Endpoint to update the quantity of an item in a user's inventory
@app.put("/inventory/{user_id}/{item_id}")
def update_item(user_id: int, item_id: int, token: str, quantity: int):
    authenticate_user(user_id, token)  # Validate user authentication
    inventory = db["inventories"].get(user_id, None)  # Get user's inventory
    if not inventory:
        raise HTTPException(status_code=404, detail="No inventory found for this user.")

    # Find the item in the inventory
    item = next((i for i in inventory if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    item.quantity = quantity  # Update the item's quantity
    return {"message": "Item updated successfully.", "item": item}

# Endpoint to delete an item from a user's inventory
@app.delete("/inventory/{user_id}/{item_id}")
def delete_item(user_id: int, item_id: int, token: str):
    authenticate_user(user_id, token)  # Validate user authentication
    inventory = db["inventories"].get(user_id, None)  # Get user's inventory
    if not inventory:
        raise HTTPException(status_code=404, detail="No inventory found for this user.")

    # Find the item in the inventory
    item = next((i for i in inventory if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    inventory.remove(item)  # Remove the item from the inventory
    return {"message": "Item deleted successfully."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
