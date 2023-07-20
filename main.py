from pydantic import BaseModel
from fastapi import FastAPI,Body, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from tarzapay import *
import json
from fastapi.middleware.cors import CORSMiddleware

from database import *
from email_api import *

tarzapay_api_Key = 'GSLL9GDA84URSS7TSA2Z'
tarzapay_secret = 'sandbox_gPIMe0IIIxd7x3HHVBpUPki32eNV8AC84lByYTNaD7JDgGpIMZRZa4dVUmFlY0M8otDUyAxBw8AoSLObmkvZEtL5Aq70U7IPAgKddMy7bU7vIx4SWokkcVfI9CI4pWXB'

app = FastAPI()
security = HTTPBasic()
# Allow all origins for demonstration purposes. Replace "*" with your specific origins.
origins = ["*"]


valid_api_keys = ["ee0e1e35-cdvn-3471-3xbv-ac73611ac1e2"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Buyer(BaseModel):
    ind_bus_type: str = Field("Individual")
    email: str
    country: str
    first_name: str
    last_name: str

class Transaction(BaseModel):
    buyer: Buyer
    invoice_currency: str = Field("USD")
    invoice_amount: float
    txn_description: str



def verify_api_key(api_key: str = None):
    if api_key is None or api_key not in valid_api_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/transactions/")
async def create_transaction(
    transaction: Transaction = Body(...),
    api_key: str = Depends(verify_api_key)
):
    # Process the logic to create a transaction and save it to the database

    transaction_json = jsonable_encoder(transaction)
    response = create_checkout_session(transaction_json, tarzapay_api_Key, tarzapay_secret)

    receiver_email = response['email']
    subject = "Guide for Tazapay Transaction"
    payment_link = response['redirect_url']
    # Generate the HTML content with the payment link
    html_content = generate_html_content(payment_link)
    
    # Send the email
    send_html_email(receiver_email, subject, html_content)


    return {
        "payment": response,
        "transaction": transaction}


@app.get("/checkout/{txn_no}")
async def get_checkout(txn_no: str, api_key: str = Depends(verify_api_key)):
    # Perform logic to retrieve checkout details based on `txn_no`
    response = get_checkout_session(txn_no, tarzapay_api_Key, tarzapay_secret)
    if response['state'] == 'Payment_Received':
        txn_no = response['txn_no']
        # Split the txn_description to extract uid_user and plan
        txn_description = response['txn_description']
        try:
            uid_user, aggregated_plan  = txn_description.split(';')
        except:
            uid_user = 'anonymous'
            aggregated_plan = 'unknown'

        invoice_amount = response['invoice_amount']
        note = "Payment for Gold Plan subscription"
        handle_payment_success(uid_user, invoice_amount, txn_no, aggregated_plan, note)

    return response

#2307-562822

#ee0e1e35-cdvn-3471-3xbv-ac73611ac1e2