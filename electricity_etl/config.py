from datetime import date

# Configuration parameters for the simulation
BASE_KWH = 10000  # Base energy consumption for the first day
GROWTH_RATE = 0.012  # Daily growth rate (1.2%)
FEEDER_TO_DTR_EFF = 0.93  # Efficiency from feeder to DTR
DTR_TO_CONSUMER_EFF = 0.95  # Efficiency from DTR to consumer
SIMULATE_DATE = date.today()  # Date for the simulation (today's date)

# Number of days for simulation (can be backdated if needed)
DAYS_SINCE_START = 10  # Example for 10 days of growth
