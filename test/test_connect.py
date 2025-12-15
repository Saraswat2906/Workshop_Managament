from sqlalchemy import create_engine, text
from Database_config import Database_url  

try:
    engine = create_engine(Database_url)
    with engine.connect() as conn:
        print("✅ Connected successfully!")
        version = conn.execute(text("SELECT version();"))
        print("🧠 PostgreSQL version:", version.fetchone()[0])
except Exception as e:
    print("❌ Connection failed!")
    print("Error:", e)
