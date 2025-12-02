# load_to_postgres.py
import pandas as pd
from sqlalchemy import create_engine
import os

# Get DB config from environment
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bank_reviews_db")

# Path to your existing processed CSV
CSV_PATH = "data/processed/reviews_with_sentiment_themes.csv"
TABLE_NAME = "bank_reviews"

# Create PostgreSQL connection
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Load and push data
print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows. Pushing to PostgreSQL...")

df.to_sql(
    name=TABLE_NAME,
    con=engine,
    if_exists='replace',
    index=False,
    method='multi'
)

print(f"✅ Successfully loaded data into '{TABLE_NAME}' table.")