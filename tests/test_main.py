import pytest
from fastapi.testclient import TestClient
from main import app, calculate_distance, calculate_delivery_fee

client = TestClient(app)

def test_calculate_distance():
    assert calculate_distance(60.17094, 24.93087, 60.17096, 24.93089) == 2

def test_calculate_delivery_fee():
    base_price = 100
    distance_ranges = [
        {"min": 0, "max": 500, "a": 0, "b": 0},
        {"min": 500, "max": 1000, "a": 100, "b": 1},
        {"min": 1000, "max": 0, "a": 0, "b": 0}
    ]
    assert calculate_delivery_fee(400, base_price, distance_ranges) == 100
    assert calculate_delivery_fee(600, base_price, distance_ranges) == 260
    with pytest.raises(Exception):
        calculate_delivery_fee(1000, base_price, distance_ranges)

def test_delivery_order_price(mocker):
    mocker.patch('main.get_venue_data', return_value={
        "location": [24.93087, 60.17094],
        "order_minimum_no_surcharge": 1000,
        "base_price": 100,
        "distance_ranges": [
            {"min": 0, "max": 500, "a": 0, "b": 0},
            {"min": 500, "max": 1000, "a": 100, "b": 1},
            {"min": 1000, "max": 0, "a": 0, "b": 0}
        ]
    })

    response = client.get('/api/v1/delivery-order-price?venue_slug=test-venue&cart_value=800&user_lat=60.17096&user_lon=24.93089')
    assert response.status_code == 200
    data = response.json()
    assert data['total_price'] == 1160
    assert data['small_order_surcharge'] == 200
    assert data['cart_value'] == 800
    assert data['delivery']['fee'] == 160
    assert data['delivery']['distance'] == 2

def test_delivery_not_possible(mocker):
    mocker.patch('main.get_venue_data', return_value={
        "location": [24.93087, 60.17094],
        "order_minimum_no_surcharge": 1000,
        "base_price": 100,
        "distance_ranges": [
            {"min": 0, "max": 500, "a": 0, "b": 0},
            {"min": 500, "max": 0, "a": 0, "b": 0}
        ]
    })

    response = client.get('/api/v1/delivery-order-price?venue_slug=test-venue&cart_value=800&user_lat=60.18096&user_lon=24.94089')
    assert response.status_code == 400
    data = response.json()
    assert 'detail' in data
    assert data['detail'] == 'Delivery not possible for this distance'

def test_invalid_input():
    response = client.get('/api/v1/delivery-order-price?venue_slug=test-venue&cart_value=invalid&user_lat=60.17096&user_lon=24.93089')
    assert response.status_code == 422
    data = response.json()
    assert 'detail' in data
    assert 'cart_value' in str(data['detail'])