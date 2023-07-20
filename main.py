from pydantic import BaseModel
from fastapi import FastAPI,Body
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from tarzapay import *
import json


tarzapay_api_Key = 'GSLL9GDA84URSS7TSA2Z'
tarzapay_secret = 'sandbox_gPIMe0IIIxd7x3HHVBpUPki32eNV8AC84lByYTNaD7JDgGpIMZRZa4dVUmFlY0M8otDUyAxBw8AoSLObmkvZEtL5Aq70U7IPAgKddMy7bU7vIx4SWokkcVfI9CI4pWXB'

app = FastAPI()



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

@app.post("/transactions/")
async def create_transaction(transaction: Transaction = Body(...)):
    # Process the logic to create a transaction and save it to the database

    transaction_json = jsonable_encoder(transaction)
    response = create_checkout_session(transaction_json, tarzapay_api_Key, tarzapay_secret)

    return {
        "payment": response,
        "transaction": transaction}


@app.get("/checkout/{txn_no}")
async def get_checkout(txn_no: str):
    # Perform logic to retrieve checkout details based on `txn_no`
    # For example: query a database or retrieve from a data source
    response = get_checkout_session(txn_no, tarzapay_api_Key, tarzapay_secret)

    return response