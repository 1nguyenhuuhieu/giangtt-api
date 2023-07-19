from pydantic import BaseModel
from fastapi import FastAPI
from pydantic import BaseModel, Field

from tarzapay import *


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
async def create_transaction(transaction: Transaction):
    # Process the logic to create a transaction and save it to the database
    # For example: Print transaction information and return a response
    return {"message": "Transaction created successfully", "transaction": transaction}