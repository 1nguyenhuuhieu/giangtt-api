import requests

# Replace these values with your actual API endpoint and credentials if necessary
api_base_url = "http://localhost:8000"
username = "tungnguyen1"
password = "Pass@123"

# Sample data for the transaction
transaction_data = {
    "buyer": {
        "ind_bus_type": "Individual",
        "email": "hieu@gmal.com",
        "country": "US",
        "first_name": "string",
        "last_name": "string"
    },
    "invoice_currency": "USD",
    "invoice_amount": 100,
    "txn_description": "Test Transaction"
}

# Send a POST request with Basic Authentication
response = requests.post(
    f"{api_base_url}/transactions/",
    json=transaction_data,
    auth=(username, password)
)

# Check the response
if response.status_code == 200:
    print("Transaction created successfully!")
    print(response.json())
else:
    print(f"Failed to create transaction. Status code: {response.status_code}")
    print(response.json())
