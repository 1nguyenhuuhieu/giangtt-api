import requests

url = "https://api-sandbox.tazapay.com/v1/checkout"

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
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic R1NMTDlHREE4NFVSU1M3VFNBMlo6c2FuZGJveF9nUElNZTBJSUl4ZDd4M0hIVkJwVVBraTMyZU5WOEFDODRsQnlZVE5hRDdKRGdHcElNWlJaYTRkVlVtRmxZME04b3REVXlBeEJ3OEFvU0xPYm1rdlpFdEw1QXE3MFU3SVBBZ0tkZE15N2JVN3ZJeDRTV29ra2NWZkk5Q0k0cFdYQg=="
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)