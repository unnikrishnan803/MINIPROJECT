import requests

def test_nearby():
    # Coordinates for Grill and Chill (approx)
    lat = 9.6902
    lng = 76.3422
    
    url = f"http://127.0.0.1:8000/api/nearby-restaurants/?lat={lat}&lng={lng}&radius=10"
    
    print(f"Calling: {url}")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print("Response:", response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nearby()
