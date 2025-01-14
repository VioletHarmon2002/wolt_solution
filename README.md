
# Wolt Delivery Order Price Calculator

## Project Overview

This project implements a Delivery Order Price Calculator (DOPC) service for Wolt. It calculates the delivery price for an order based on the cart value, the user's location, and the venue's location and pricing rules.


## Technologies Used

- Python 3.12+
- FastAPI
- Uvicorn (ASGI server)
- Pytest for testing

## Installation

1. Clone the repository:

2. Create a virtual environment

3. Install the required packages


## Usage

1. Start the server: uvicorn main:app --reload
2. The API will be available at `http://localhost:8000`

3. Use the `/api/v1/delivery-order-price` endpoint to calculate delivery prices:    GET /api/v1/delivery-order-price?venue_slug=example-venue&cart_value=1000&user_lat=60.1709&user_lon=24.9409


## API Documentation

Once the server is running, you can access the automatic API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

To run the tests, execute: pytest


## Project Structure
wolt_solution/
│
├── main.py            # Main application file
├── requirements.txt   # Project dependencies
├── README.md          # This file
│
└── tests/
    ├── init.py
    └── test_main.py   # Test cases for the main application