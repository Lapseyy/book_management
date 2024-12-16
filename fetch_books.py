import requests

response = requests.get("http://127.0.0.1:8000/books/")
if response.status_code == 200:
    books = response.json()
    print("Books List:")
    for book in books:
        print(book)
else:
    print("Failed to fetch books:", response.status_code)
