import requests
import json

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
API_URL = f"{BASE_URL}/api"

# Credentials
EMAIL = "usa@test.com"
PASSWORD = "testpassword123"

session = requests.Session()

def login():
    print(f"Logging in as {EMAIL}...")
    # Get CSRF token first
    check = session.get(LOGIN_URL)
    csrf = session.cookies['csrftoken']
    
    login_data = {
        'login': EMAIL,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf
    }
    
    headers = {
        'Referer': LOGIN_URL
    }
    
    response = session.post(LOGIN_URL, data=login_data, headers=headers)
    if response.ok:
        print("✅ Login Successful")
        return True
    else:
        print(f"❌ Login Failed: {response.status_code}")
        return False

def get_csrf_token():
    return session.cookies.get('csrftoken')

def verify_flow():
    if not login():
        return

    csrf = get_csrf_token()
    headers = {
        'X-CSRFToken': csrf,
        'Content-Type': 'application/json'
    }

    print("\n--- 1. Fetching Tables ---")
    tables_resp = session.get(f"{API_URL}/tables/")
    data = tables_resp.json()
    if 'results' in data:
        tables = data['results']
    else:
        tables = data
        
    print(f"Found {len(tables)} tables.")
    if not tables:
        print("No tables found.")
        return

    target_table = tables[0]
    print(f"Using Table {target_table['table_number']} (ID: {target_table['id']}) Status: {target_table['status']}")

    print("\n--- 2. Fetching Menu ---")
    menu_resp = session.get(f"{API_URL}/food-items/")
    menu = menu_resp.json()['results']
    if not menu:
        print("No food items found. Cannot place order.")
        return
    item = menu[0]
    print(f"Selected Item: {item['name']} (${item['price']})")

    print("\n--- 3. Placing Order ---")
    order_data = {
        "table": target_table['id'],
        "items": [item['id']]
    }
    order_resp = session.post(f"{API_URL}/dining-orders/", json=order_data, headers=headers)
    if order_resp.status_code == 201:
        order = order_resp.json()
        print(f"✅ Order #{order['id']} Placed! Status: {order['status']}")
    else:
        print(f"❌ Order Failed: {order_resp.text}")
        return

    print("\n--- 4. Kitchen: Updating Status ---")
    # Mark Preparing
    session.post(f"{API_URL}/dining-orders/{order['id']}/update_status/", json={'status': 'Preparing'}, headers=headers)
    print("➡️ Order marked as Preparing")
    
    # Mark Served
    session.post(f"{API_URL}/dining-orders/{order['id']}/update_status/", json={'status': 'Served'}, headers=headers)
    print("➡️ Order marked as Served")
    
    print("\n--- 5. Generating Bill ---")
    bill_data = {
        "action": "generate",
        "table_id": target_table['id']
    }
    bill_resp = session.post(f"{API_URL}/billing/", json=bill_data, headers=headers)
    if bill_resp.status_code == 200:
        bill = bill_resp.json()
        print(f"✅ Bill Generated! Total: ${bill['grand_total']}")
    else:
        print(f"❌ Bill Generation Failed: {bill_resp.text}")
        return

    print("\n--- 6. Processing Payment ---")
    pay_data = {
        "action": "pay",
        "bill_id": bill['id'],
        "payment_method": "Card"
    }
    pay_resp = session.post(f"{API_URL}/billing/", json=pay_data, headers=headers)
    if pay_resp.status_code == 200:
        print("✅ Payment Successful!")
        print(f"Table Status Updated to: {pay_resp.json()['table_status']}")
    else:
        print(f"❌ Payment Failed: {pay_resp.text}")

if __name__ == "__main__":
    try:
        verify_flow()
    except Exception as e:
        print(f"Error: {e}")
