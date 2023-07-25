import requests
import json


def create_payment(item,coinbase_api_key):
    headers = {
        'Content-Type': 'application/json',
        'X-CC-Api-Key': coinbase_api_key,
        'X-CC-Version': '2018-03-22'
    }

    payload = {
        'name': item.email,
        'description': item.description,
        'local_price': {
            'amount': str(item.amount),
            'currency': item.currency
        },
        'pricing_type': 'fixed_price'
    }

    response = requests.post('https://api.commerce.coinbase.com/charges/', headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        response_data = response.json()
        hosted_url = response_data['data']['hosted_url']
        charge_code = response_data['data']['code']
        return {
            'hosted_url': hosted_url,
            'charge_code': charge_code
        }

    return None



def is_payment_successful(response):
    # Access the 'timeline' field in the response
    timeline = response.get('data', {}).get('timeline', [])

    # Check if there's a status 'PAID' in the timeline
    for item in timeline:
        if item.get('status') == 'PAID':
            return True

    return False


def get_charge_amount(response):
    # Access the 'pricing' field in the response
    pricing = response.get('data', {}).get('pricing', {})
    
    # Get the local amount
    local_amount = pricing.get('local', {}).get('amount')

    return local_amount


def get_charge(charge_id,coinbase_api_key):
    url = f'https://api.commerce.coinbase.com/charges/{charge_id}'

    headers = {
        'Content-Type': 'application/json',
        'X-CC-Api-Key': coinbase_api_key,
        'X-CC-Version': '2018-03-22'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()

        is_success = is_payment_successful(response_data)
        amount = get_charge_amount(response_data)
        user_email = response.get('data', {}).get('name', '')
        description = response.get('data', {}).get('description', '')

        return {
            'is_success': is_success,
            'amount': amount,
            'user_email': user_email,
            'description': description
        }
    else:
        print(f"Request failed with status {response.status_code}")
        return None
    