import requests
from pydantic import BaseModel
import base64
import hashlib
import hmac
from fastapi import FastAPI, HTTPException


app = FastAPI()

api_url = "https://api-sandbox.tazapay.com"
api_key = 'GSLL9GDA84URSS7TSA2Z'
api_secret = 'sandbox_gPIMe0IIIxd7x3HHVBpUPki32eNV8AC84lByYTNaD7JDgGpIMZRZa4dVUmFlY0M8otDUyAxBw8AoSLObmkvZEtL5Aq70U7IPAgKddMy7bU7vIx4SWokkcVfI9CI4pWXB'

def generate_signature(api_secret, data):
    key_bytes = bytes(api_secret, 'latin-1')
    data_bytes = bytes(data, 'latin-1')
    signature = hmac.new(key_bytes, msg=data_bytes, digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode('latin-1')

def send_request(endpoint, method, api_url, api_key, api_secret, data=None):
    url = api_url + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{api_key}:".encode()).decode()}'
    }
    if data:
        signature = generate_signature(api_secret, data)
        headers['Signature'] = signature

    response = requests.request(method, url, headers=headers, json=data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/payment")
def make_payment(amount: float, user_id: int):
    endpoint = '/v1/payment'  # Địa chỉ API cụ thể trong Tarzapay

    data = {
        'amount': amount,
        'user_id': user_id
    }

    try:
        response = send_request(endpoint, 'POST', api_url, api_key, api_secret, data)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
