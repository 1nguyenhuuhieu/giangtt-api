from pydantic import BaseModel
from fastapi import FastAPI,Body, Depends, HTTPException, Query
from fastapi.security import HTTPBasic
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from tarzapay import *
from fastapi.middleware.cors import CORSMiddleware

from database import *
from email_api import *


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



# Your SMTP email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "1nguyenhuuhieu@gmail.com"
SENDER_PASSWORD = "qlwzbxcnfvceiwfb"

tarzapay_api_Key = 'GSLL9GDA84URSS7TSA2Z'
tarzapay_secret = 'sandbox_gPIMe0IIIxd7x3HHVBpUPki32eNV8AC84lByYTNaD7JDgGpIMZRZa4dVUmFlY0M8otDUyAxBw8AoSLObmkvZEtL5Aq70U7IPAgKddMy7bU7vIx4SWokkcVfI9CI4pWXB'

coinbase_api_key = '9c99c9ad-29a9-4179-9a4a-e31514b7b391'

app = FastAPI()
security = HTTPBasic()
# Allow all origins for demonstration purposes. Replace "*" with your specific origins.
origins = ["*"]


valid_api_keys = ["test-apikey-22072023"]

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


@app.post("/api/create_transaction/")
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


@app.get("/api/checkout/{txn_no}")
async def get_checkout(txn_no: str, api_key: str = Depends(verify_api_key)):
    # Perform logic to retrieve checkout details based on `txn_no`
    response = get_checkout_session(txn_no, tarzapay_api_Key, tarzapay_secret)
    if response['state'] == 'Payment_Received':
        txn_no = response['txn_no']
        email = response['email']
        # Split the txn_description to extract uid_user and plan
        txn_description = response['txn_description']
        try:
            uid_user, aggregated_plan  = txn_description.split(';')
        except:
            uid_user = 'anonymous'
            aggregated_plan = 'unknown'

        invoice_amount = response['invoice_amount']
        if aggregated_plan == 'unknown':
            note = txn_no
        else:
            note = f"Payment for {aggregated_plan} Plan subscription"

        handle_payment_success(uid_user, invoice_amount, txn_no, aggregated_plan, note, email)
    return response


# Assuming you have already defined the update_credit_and_record_transfer function
@app.post("/api/create_user/")
async def create_user(uid_user: str, email: str, api_key: str = Depends(verify_api_key)):
    # Check if the user already exists in the database
    existing_user = SessionLocal().query(User).filter_by(uid_user=uid_user).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    # Get the current time
    current_time = datetime.now()
    endded_time = current_time + timedelta(days=30)
    # Create a new user object
    new_user = User(uid_user=uid_user, plan_started_time=current_time, 
                    plan_ended_time=endded_time, email=email)

    # Add the new user to the database
    session = SessionLocal()
    credit_transfer = CreditTransfer(
    credit=1,
    uid_user=uid_user,
    note="Free 1 credit for sigup",
    time_created=current_time
    )
    session.add(credit_transfer)
    session.add(new_user)

    
    session.commit()

    return {"status": "User created successfully.", "user_id": uid_user}

@app.get("/api/check_generate/{user_id}/")
async def check_generate(user_id: str, api_key: str = Depends(verify_api_key)):
    # Query the user from the database based on the provided uid_user
    user = session.query(User).filter_by(uid_user=user_id).first()

    if user:
        # Get the current time
        current_time = datetime.now()

        # Check if the credit is less than 10 and send alert email
        if user.credit < 10:
            email_message = f"Alert: Your credit is low! Current credit: {user.credit}"
            send_email(user.email, "Credit Alert", email_message)
            if user.credit <= 0:
                return {"status": "Credit is not valid."}
        # Check if the plan end time is in the future
        if user.plan_ended_time > current_time:
            return {"status": "Credit and plan are valid."}
        else:
            return {"status": "Credit or plan is not valid."}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
@app.get("/api/generate_success/{user_id}/")
async def generate_success(user_id: str, api_key: str = Depends(verify_api_key)):
    # Query the user from the database based on the provided uid_user
    user = session.query(User).filter_by(uid_user=user_id).first()

    if user:
        # Get the current time
        current_time = datetime.now()

        # Check if the credit is less than or equal to 0 or the plan end time is in the past
        if user.credit <= 0 or user.plan_ended_time < current_time:
            return {"status": "No allow to generate."}

        # If credit is valid, decrement it by 1 and create a new credit transfer record
        user.credit -= 1
        credit_transfer = CreditTransfer(
            credit=-1,
            uid_user=user_id,
            note="generate",
            time_created=current_time
        )
        session.add(credit_transfer)
        session.commit()

        return {"status": "Allow to generate."}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/user/{user_id}/")
async def get_user(user_id: str, api_key: str = Depends(verify_api_key)):
    # Query the user from the database based on the provided uid_user
    user = session.query(User).filter_by(uid_user=user_id).first()

    if user:
        return {
            "uid_user": user.uid_user,
            "plan": user.plan,
            "plan_started_time": user.plan_started_time,
            "plan_ended_time": user.plan_ended_time,
            "credit": user.credit
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")
    

@app.get("/api/total_users/")
async def get_total_users(api_key: str = Depends(verify_api_key)):
    # Query the total number of users from the database
    total_users = session.query(User).count()

    return {"total_users": total_users}


@app.get("/api/get_users/")
async def get_users(page: int = Query(1, ge=1), limit: int = Query(10, le=100), api_key: str = Depends(verify_api_key)):
    # Calculate the offset based on the page and limit values
    offset = (page - 1) * limit

    # Query users from the database with pagination
    users = session.query(User).offset(offset).limit(limit).all()

    if users:
        user_list = [{"user_id": user.uid_user, "plan": user.plan, "credit": user.credit} for user in users]
        return {"users": user_list}
    else:
        return {"users": []}
    

@app.get("/api/payment_success/{user_id}/")
async def get_user_payment_success(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100), api_key: str = Depends(verify_api_key)
):
    # Calculate the offset based on the page and limit values
    offset = (page - 1) * limit

    # Query successful payment transactions for the specified user with pagination
    user_payment_success_list = (
        session.query(PaymentSuccess)
        .filter_by(uid_user=user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    if user_payment_success_list:
        success_list = [
            {
                "invoice_amount": payment.invoice_amount,
                "txn_no": payment.txn_no,
                "time_created": payment.time_created
            }
            for payment in user_payment_success_list
        ]
        return {"user_id": user_id, "payment_success_list": success_list}
    else:
        return {"user_id": user_id, "payment_success_list": []}
    

@app.get("/api/total_payment_success/")
async def get_total_payment_success(api_key: str = Depends(verify_api_key)):
    # Query the total number of successful payment transactions from the database
    total_success = session.query(PaymentSuccess).count()

    return {"total_payment_success": total_success}


@app.get("/api/payment_success/")
async def get_payment_success(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100)
    , api_key: str = Depends(verify_api_key)
):
    # Calculate the offset based on the page and limit values
    offset = (page - 1) * limit

    # Query successful payment transactions from the database with pagination
    payment_success_list = session.query(PaymentSuccess).offset(offset).limit(limit).all()

    if payment_success_list:
        success_list = [
            {
                "invoice_amount": payment.invoice_amount,
                "uid_user": payment.uid_user,
                "txn_no": payment.txn_no,
                "time_created": payment.time_created
            }
            for payment in payment_success_list
        ]
        return {"payment_success_list": success_list}
    else:
        return {"payment_success_list": []}
    


@app.get("/api/credit_transfer/{user_id}/")
async def get_user_credit_transfer(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100), api_key: str = Depends(verify_api_key)
):
    # Calculate the offset based on the page and limit values
    offset = (page - 1) * limit

    # Query credit transfers for the specified user with pagination
    user_credit_transfer_list = (
        session.query(CreditTransfer)
        .filter_by(uid_user=user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    if user_credit_transfer_list:
        transfer_list = [
            {
                "credit": credit_transfer.credit,
                "note": credit_transfer.note,
                "time_created": credit_transfer.time_created
            }
            for credit_transfer in user_credit_transfer_list
        ]
        return {"user_id": user_id, "credit_transfer_list": transfer_list}
    else:
        return {"user_id": user_id, "credit_transfer_list": []}


@app.get("/api/total_credit_transfer/")
async def get_total_credit_transfer(api_key: str = Depends(verify_api_key)):
    # Query the total number of credit transfers from the database
    total_credit_transfer = session.query(CreditTransfer).count()

    return {"total_credit_transfer": total_credit_transfer}


@app.get("/api/credit_transfer/")
async def get_credit_transfer(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100), api_key: str = Depends(verify_api_key)
):
    # Calculate the offset based on the page and limit values
    offset = (page - 1) * limit

    # Query credit transfers from the database with pagination
    credit_transfer_list = (
        session.query(CreditTransfer)
        .offset(offset)
        .limit(limit)
        .all()
    )

    if credit_transfer_list:
        transfer_list = [
            {
                "credit": credit_transfer.credit,
                "uid_user": credit_transfer.uid_user,
                "note": credit_transfer.note,
                "time_created": credit_transfer.time_created
            }
            for credit_transfer in credit_transfer_list
        ]
        return {"credit_transfer_list": transfer_list}
    else:
        return {"credit_transfer_list": []}




@app.post("/api/send_email/")
async def send_email(receiver_email: str, subject: str, body: str, api_key: str = Depends(verify_api_key)):
    try:
        # Prepare the email content
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()

        return {"message": "Email sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")




#2307-020710

#ee0e1e35-cdvn-3471-3xbv-ac73611ac1e2