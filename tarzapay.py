import requests
import base64

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

    print(payload)

    url = "https://api-sandbox.tazapay.com/v1/checkout"
    headers = create_basic_auth_header(username, password)
    response = requests.post(url, json=payload, headers=headers)
    return response
