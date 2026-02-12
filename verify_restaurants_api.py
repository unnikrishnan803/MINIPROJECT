import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/api/restaurants/')
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response Data Type:", type(data))
        if isinstance(data, dict):
             print("Keys:", data.keys())
             if 'results' in data:
                 print("Results count:", len(data['results']))
                 if len(data['results']) > 0:
                     print("First Item Keys:", data['results'][0].keys())
        elif isinstance(data, list):
             print("List Length:", len(data))
             if len(data) > 0:
                 print("First Item Keys:", data[0].keys())
        else:
            print("Unknown structure")
    except Exception as e:
        print("JSON Decode Error:", e)
        print("Raw Content:", response.text[:500])

except Exception as e:
    print("Connection Error:", e)
