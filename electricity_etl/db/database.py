from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite database for simplicity
engine = create_engine("sqlite:///electricity.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
