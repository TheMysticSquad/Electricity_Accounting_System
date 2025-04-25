from db.database import SessionLocal
from db.models import Feeder, DTR, Consumer, Reading
from config import BASE_KWH, GROWTH_RATE, FEEDER_TO_DTR_EFF, DTR_TO_CONSUMER_EFF, SIMULATE_DATE, DAYS_SINCE_START
from datetime import timedelta
import math

def simulate_day_readings():
    session = SessionLocal()

    # Iterate over all feeders in the database
    feeders = session.query(Feeder).all()
    for feeder in feeders:
        # Calculate the number of days since the feeder's start date
        days_since_start = DAYS_SINCE_START
        feeder_kwh = round(BASE_KWH * ((1 + GROWTH_RATE) ** days_since_start), 2)
        
        # Insert the simulated feeder reading into the database
        session.add(Reading(entity_type='feeder', entity_id=feeder.id, reading_kwh=feeder_kwh, reading_date=SIMULATE_DATE))
        
        # Get all DTRs for the current feeder
        dtrs = session.query(DTR).filter_by(feeder_id=feeder.id).all()
        dtr_kwh_total = feeder_kwh * FEEDER_TO_DTR_EFF
        dtr_kwh_each = dtr_kwh_total / len(dtrs) if dtrs else 0

        # Insert DTR readings
        for dtr in dtrs:
            session.add(Reading(entity_type='dtr', entity_id=dtr.id, reading_kwh=round(dtr_kwh_each, 2), reading_date=SIMULATE_DATE))
            
            # Get all consumers for the current DTR
            consumers = session.query(Consumer).filter_by(dtr_id=dtr.id).all()
            consumer_kwh_total = dtr_kwh_each * DTR_TO_CONSUMER_EFF
            consumer_kwh_each = consumer_kwh_total / len(consumers) if consumers else 0

            # Insert consumer readings
            for consumer in consumers:
                session.add(Reading(entity_type='consumer', entity_id=consumer.id, reading_kwh=round(consumer_kwh_each, 2), reading_date=SIMULATE_DATE))
    
    # Commit the transaction to save all the readings
    session.commit()
    session.close()

def main():
    # Running the ETL process to simulate energy readings
    simulate_day_readings()

if __name__ == "__main__":
    main()
