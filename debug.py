import os
import sqlite3

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("Working dir:", os.getcwd())
print("Data dir exists:", os.path.exists("/app/data"))
print("Data dir contents:", os.listdir("/app/data"))

# Test SQLite connection
db_path = "./data/math_service.db"
print(f"Trying to connect to: {db_path}")
print(f"Absolute path: {os.path.abspath(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    print("SQLite connection successful!")
    conn.close()
except Exception as e:
    print(f"SQLite connection failed: {e}")

# Test creating file directly
try:
    with open("./data/test.txt", "w") as f:
        f.write("test")
    print("File creation successful!")
except Exception as e:
    print(f"File creation failed: {e}")
