from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
import math

app = FastAPI(
    title="Delivery Order Price Calculator",
    description="A service to calculate the total price and price breakdown of a delivery order.",
    version="1.0.0"
)

BASE_URL = "https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues"

class DeliveryResponse(BaseModel):
    """
    Pydantic model for the delivery response.
    All monetary values are in the lowest denomination of the local currency (cents/öre/yen).
    """
    total_price: int
    small_order_surcharge: int
    cart_value: int
    delivery: dict

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Calculate the straight-line distance between two points on Earth.
    """
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c)

def get_venue_data(venue_slug: str) -> dict:
    """
    Fetch venue data from the Home Assignment API.
    """
    static_url = f"{BASE_URL}/{venue_slug}/static"
    dynamic_url = f"{BASE_URL}/{venue_slug}/dynamic"

    try:
        static_response = requests.get(static_url)
        static_response.raise_for_status()
        static_data = static_response.json()

        dynamic_response = requests.get(dynamic_url)
        dynamic_response.raise_for_status()
        dynamic_data = dynamic_response.json()

        venue_location = static_data['venue_raw']['location']['coordinates']
        order_minimum_no_surcharge = dynamic_data['venue_raw']['delivery_specs']['order_minimum_no_surcharge']
        base_price = dynamic_data['venue_raw']['delivery_specs']['delivery_pricing']['base_price']
        distance_ranges = dynamic_data['venue_raw']['delivery_specs']['delivery_pricing']['distance_ranges']

        return {
            "location": venue_location,
            "order_minimum_no_surcharge": order_minimum_no_surcharge,
            "base_price": base_price,
            "distance_ranges": distance_ranges
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch venue data: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data structure in API response: {str(e)}")

def calculate_delivery_fee(distance: int, base_price: int, distance_ranges: list) -> int:
    """
    Calculate the delivery fee based on distance and venue-specific pricing rules.
    """
    fee = base_price

    for range_data in distance_ranges:
        if range_data['min'] <= distance < range_data['max'] or (range_data['max'] == 0 and distance >= range_data['min']):
            fee += range_data['a'] + range_data['b'] * distance
            break

    if fee == base_price:
        raise HTTPException(status_code=400, detail="Delivery not possible for this distance")

    return round(fee)

@app.get("/api/v1/delivery-order-price", response_model=DeliveryResponse)
async def delivery_order_price(
    venue_slug: str = Query(..., description="The unique identifier for the venue"),
    cart_value: int = Query(..., description="The total value of the items in the shopping cart"),
    user_lat: float = Query(..., description="The latitude of the user's location"),
    user_lon: float = Query(..., description="The longitude of the user's location")
):
    """
    Calculate the delivery order price based on venue data and user location.
    """
    venue_data = get_venue_data(venue_slug)

    venue_lon, venue_lat = venue_data['location']
    distance = calculate_distance(venue_lat, venue_lon, user_lat, user_lon)

    delivery_fee = calculate_delivery_fee(distance, venue_data['base_price'], venue_data['distance_ranges'])

    small_order_surcharge = max(0, venue_data['order_minimum_no_surcharge'] - cart_value)

    total_price = cart_value + small_order_surcharge + delivery_fee

    return DeliveryResponse(
        total_price=total_price,
        small_order_surcharge=small_order_surcharge,
        cart_value=cart_value,
        delivery={
            "fee": delivery_fee,
            "distance": distance
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)