from models import db
from sqlalchemy import create_engine, inspect
from Database_config import config 

# Initialize engine
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
try:
    with engine.connect() as conn:
        print("Database connection successful")

        #Reflect and inspect tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n Found tables in DB:")
        for t in tables:
            print(" -", t)

        # Try creating the ORM metadata in memory (without modifying DB)
        db.metadata.create_all(bind=engine, checkfirst=True)
        print("\n SQLAlchemy models are valid and compatible!")

except Exception as e:
    print("Error connecting or verifying models:")
    print(e)
