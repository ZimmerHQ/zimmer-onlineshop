import requests
import json

# Test the API directly
response = requests.get('http://localhost:8000/api/orders/')
if response.status_code == 200:
    data = response.json()
    if data:
        latest = data[-1]
        print(f'Latest Order: {latest["order_number"]}')
        print(f'Items Count: {latest["items_count"]}')
        print(f'Final Amount: {latest["final_amount"]}')
        print(f'Customer Snapshot: {bool(latest.get("customer_snapshot"))}')
    else:
        print('No orders found')
else:
    print(f'API Error: {response.status_code}')

