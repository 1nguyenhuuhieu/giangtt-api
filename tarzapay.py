import requests
import base64

API_url = 'https://api-sandbox.tazapay.com/v1/checkout'
API_Key = 'GSLL9GDA84URSS7TSA2Z'
API_Secret = 'sandbox_gPIMe0IIIxd7x3HHVBpUPki32eNV8AC84lByYTNaD7JDgGpIMZRZa4dVUmFlY0M8otDUyAxBw8AoSLObmkvZEtL5Aq70U7IPAgKddMy7bU7vIx4SWokkcVfI9CI4pWXB'



# Tạo header Authorization với thông tin xác thực Basic
def create_basic_auth_header(username, password):
    auth_string = f"{username}:{password}"
    encoded_auth_string = auth_string.encode("utf-8")
    base64_auth_string = base64.b64encode(encoded_auth_string).decode("utf-8")
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {base64_auth_string}"
        }
    return headers


# Tạo yêu cầu sử dụng phương thức Basic Authentication
def make_authenticated_request(url, username, password):
    payload = {
        "buyer": {
            "ind_bus_type": "Individual",
            "email": "a@string.com",
            "country": "SG",
            "first_name": "sg",
            "last_name": "buyer"
        },
        "invoice_currency": "USD",
        "invoice_amount": 100,
        "txn_description": "test"
    }
    headers = create_basic_auth_header(username, password)
    response = requests.get(url, json=payload, headers=headers)
    return response


# Thực hiện yêu cầu với thông tin xác thực Basic
response = make_authenticated_request(API_url, API_Key, API_Secret)

print(response.text)