# Energy Consumption Dashboard

This project is an interactive dashboard built using **Dash** and **Plotly** to visualize energy consumption data. The data is fetched in real-time from a MongoDB database hosted online, and it provides insights into energy consumption by feeders, daily growth, and an energy flow network.

## Features
- **Energy Consumption by Feeder**: A bar chart that displays energy consumption for each feeder over time.
- **Energy Growth Over Time**: A line chart showing how energy consumption has grown over a selected period.
- **Energy Flow Network**: A network graph that visualizes energy distribution between different feeders and their connections.

## Technologies Used
- **Dash**: A Python framework for building analytical web applications.
- **Plotly**: A graphing library used to create interactive plots.
- **MongoDB**: A NoSQL database used to store real-time energy consumption data.
- **Python**: The programming language used to implement the dashboard and data processing.

## Installation

### Prerequisites
- Python 3.7 or higher
- MongoDB (Remote Instance on MongoDB Atlas or any other hosting service)

### Install Dependencies
To install the required libraries, run the following command:

```bash
pip install -r requirements.txt
