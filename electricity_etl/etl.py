from sqlalchemy import create_engine, text
import random
from datetime import datetime

# PostgreSQL connection setup
DATABASE_URL = "postgresql://neondb_owner:npg_OqnZp0BDwSE1@ep-shy-poetry-abbw3imb-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)
connection = engine.connect()

# Helpers
def random_category_and_load():
    categories = {
        "Residential": (0.5, 5),
        "Commercial": (5, 20),
        "Industrial": (20, 100),
        "Agricultural": (1, 15)
    }
    category = random.choice(list(categories.keys()))
    low, high = categories[category]
    load = round(random.uniform(low, high), 2)
    return category, load

def add_consumers_and_update_load():
    # Get all DTR ids
    dtr_ids_result = connection.execute(text("SELECT id FROM dtrs")).fetchall()
    if not dtr_ids_result:
        print("⚠️ No DTRs found. Please add DTRs first.")
        return
    dtr_ids = [row[0] for row in dtr_ids_result]

    # Get consumer count
    consumer_count_result = connection.execute(text("SELECT COUNT(*) FROM consumers")).scalar()
    today = datetime.now().date()

    # Insert 10 new consumers
    insert_values = []
    for i in range(10):
        consumer_no = f"C{consumer_count_result + i + 1:06d}"
        dtr_id = random.choice(dtr_ids)
        category, load_kw = random_category_and_load()
        insert_values.append(f"('Consumer_{consumer_count_result + i + 1}', '{consumer_no}', {dtr_id}, '{category}', {load_kw}, '{today}')")

    insert_query = f"""
    INSERT INTO consumers (name, consumer_no, dtr_id, category, load_kw, created_at)
    VALUES {", ".join(insert_values)}
    """
    connection.execute(text(insert_query))

    # ✅ Update existing consumers' load with correct casting
    update_query = """
    UPDATE consumers
    SET load_kw = ROUND((load_kw * (CASE 
        WHEN random() < 0.8 THEN 1.08
        ELSE 0.96
    END))::numeric, 2)
    """
    connection.execute(text(update_query))

    print("✅ Inserted 10 new consumers and updated all existing consumer loads.")

# Run ETL
add_consumers_and_update_load()

# Close connection
connection.close()
