import requests
import json

API_KEY = '9c99c9ad-29a9-4179-9a4a-e31514b7b391'  # replace 'Your-API-Key' with your actual API key

headers = {
    'Content-Type': 'application/json',
    'X-CC-Api-Key': API_KEY,
    'X-CC-Version': '2018-03-22'
}

payload = {
    'name': 'Test Product',
    'description': 'Description of the product',
    'local_price': {
        'amount': '100.00',
        'currency': 'USD'
    },
    'pricing_type': 'fixed_price'
}

response = requests.post('https://api.commerce.coinbase.com/charges/', headers=headers, data=json.dumps(payload))

if response.status_code == 201:
    response_data = response.json()
    print(f'Success: {response_data}')
    payment_url = response_data['data']['hosted_url']
    print(f'Payment URL: {payment_url}')
else:
    print(f'Error: {response.content}')
