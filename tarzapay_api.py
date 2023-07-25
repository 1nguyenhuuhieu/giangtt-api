import requests
import base64
import json

# Tạo header Authorization với thông tin xác thực Basic
def create_basic_auth_header(username, password):
    auth_string = f"{username}:{password}"
    encoded_auth_string = auth_string.encode("utf-8")
    base64_auth_string = base64.b64encode(encoded_auth_string).decode("utf-8")
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {base64_auth_string}"}
    return headers

# Tạo yêu cầu thanh toán
def create_checkout_session(payload, username, password):
    url = "https://api-sandbox.tazapay.com/v1/checkout"
    headers = create_basic_auth_header(username, password)
    response = requests.post(url, json=payload, headers=headers)

    response_data = response.text
    data = json.loads(response_data)

    email = data['data']['buyer']['email']
    status = data['status']
    message = data['message']
    redirect_url = data['data']['redirect_url']
    txn_no = data['data']['txn_no']

    response = {
    "email": email,
    "status": status,
    "message": message,
    "redirect_url": redirect_url,
    "txn_no": txn_no
    }
    return response

# Kiểm tra thông tin thanh toán
def get_checkout_session(txn_no, username, password):
    headers = create_basic_auth_header(username, password)
    base_url = "https://api-sandbox.tazapay.com/v1/checkout/"
    url = base_url + txn_no

    response = requests.get(url, headers=headers)
    response_data = response.text
    data = json.loads(response_data)

    txn_no = data['data']['txn_no']
    state = data['data']['state']
    txn_description = data['data']['txn_description']
    invoice_amount = data['data']['invoice_amount']
    email = data['data']['buyer']['email']
    response = {
    "txn_no": txn_no,
    "state": state,
    "txn_description": txn_description,
    "invoice_amount": invoice_amount,
    'email': email
    }

    return response