from pydantic import BaseModel
from fastapi import FastAPI,Body, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from tarzapay import *
import json
from fastapi.middleware.cors import CORSMiddleware

from database import*

tarzapay_api_Key = 'GSLL9GDA84URSS7TSA2Z'
tarzapay_secret = 'sandbox_gPIMe0IIIxd7x3HHVBpUPki32eNV8AC84lByYTNaD7JDgGpIMZRZa4dVUmFlY0M8otDUyAxBw8AoSLObmkvZEtL5Aq70U7IPAgKddMy7bU7vIx4SWokkcVfI9CI4pWXB'

app = FastAPI()
security = HTTPBasic()
# Allow all origins for demonstration purposes. Replace "*" with your specific origins.
origins = ["*"]


# Sample username and password for demonstration purposes
fake_users = {
    "tungnguyen1": {
        "password": "Pass@123"
    }
}

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



def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users.get(credentials.username)
    if user is None or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/transactions/")
async def create_transaction(
    transaction: Transaction = Body(...),
    username: str = Depends(authenticate_user)
):
    # Process the logic to create a transaction and save it to the database

    transaction_json = jsonable_encoder(transaction)
    response = create_checkout_session(transaction_json, tarzapay_api_Key, tarzapay_secret)

    return {
        "payment": response,
        "transaction": transaction}


@app.get("/checkout/{txn_no}")
async def get_checkout(txn_no: str, username: str = Depends(authenticate_user)):
    # Perform logic to retrieve checkout details based on `txn_no`
    response = get_checkout_session(txn_no, tarzapay_api_Key, tarzapay_secret)
    print('dfsd')
    if response['state'] == 'Payment_Received':
        print(response)
        txn_no = response['txn_no']
        uid_user = response['txn_description']
        invoice_amount = response['invoice_amount']
        note = "Payment for Premium plan"
        handle_payment_success(uid_user, invoice_amount, txn_no, note)

    else:
        print('df')
    return response

#2307-902801