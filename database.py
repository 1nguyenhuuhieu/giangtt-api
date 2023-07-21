from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from enum import Enum
from email_api import *
# Replace "your_database_name.db" with the desired name for your SQLite database
DATABASE_URL = "sqlite:///your_database_name.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()



# Define the "payment_success" table using the ORM approach
class PaymentSuccess(Base):
    __tablename__ = 'payment_success'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_amount = Column(Float, nullable=False)
    uid_user = Column(String, nullable=False)
    txn_no = Column(String, nullable=False, unique=True)
    time_created = Column(DateTime, default=datetime.utcnow)
    email = Column(String) 
    email_sent = Column(Boolean, default=False) 


# Define the "credit_transfer" table using the ORM approach
class CreditTransfer(Base):
    __tablename__ = 'credit_transfer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    credit = Column(Float, nullable=False)
    uid_user = Column(String, nullable=False)
    note = Column(String)
    time_created = Column(DateTime, default=datetime.utcnow)


class Plan(Enum):
    Starter = "Starter"
    Creator = "Creator"
    Innovator = "Innovator"

# Define the "user" table using the ORM approach
class User(Base):
    __tablename__ = 'user'

    uid_user = Column(String, primary_key=True)
    plan = Column(String, default=Plan.Starter.value)
    plan_started_time = Column(DateTime, nullable=True)
    plan_ended_time = Column(DateTime, nullable=True)
    credit = Column(Float, nullable=False, default=1)
    email = Column(String) 


# Create the database tables
Base.metadata.create_all(bind=engine)
# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


# Function to check if txn_no exists in payment_success table
def is_txn_no_exists(txn_no):
    return session.query(PaymentSuccess).filter_by(txn_no=txn_no).first() is not None


def payment_success_callback(user_email, user_name, amount):
    template_file = "payment_success_email_template.html"
    subject = "Payment Successful"
    context = {
        "user_name": user_name,
        "amount": amount
    }

    send_email2(user_email, subject, template_file, context)


# Function to handle payment success when txn_no does not exist in payment_success table
def handle_payment_success(uid_user, invoice_amount, txn_no, aggregated_plan=None, note=None, email=None):
    if not is_txn_no_exists(txn_no):
        # Update the payment_success table
        new_payment_success = PaymentSuccess(
            invoice_amount=invoice_amount,
            uid_user=uid_user,
            txn_no=txn_no,
            email = email,
            email_sent = True
        )
        session.add(new_payment_success)
        # Send the email to the user
        user_email = email
        user_name = uid_user  # Get the user's name from the database or payment_data
        amount = invoice_amount

        # Call the function to send the email
        payment_success_callback(user_email, user_name, amount)

        # Update the email_sent flag to True in the database
        # Check if the user exists in the user table
        user = session.query(User).filter_by(uid_user=uid_user).first()

        # If the user does not exist, create a new user in the user table
        if not user:
            user = User(
                uid_user=uid_user,
                plan="Basic",  # Set the appropriate default plan
                plan_started_time=datetime.utcnow(),  # Set the appropriate default plan start time
                plan_ended_time=datetime.utcnow() + timedelta(days=30),  # Set the appropriate default plan end time
                credit=0,  # Set the appropriate default credit
                email = email
            )
            session.add(user)

        # Update the credit and plan for the user
        user.credit += invoice_amount
        if aggregated_plan:
            user.plan = aggregated_plan
        else:
            user.plan = "Premium"  # Set the appropriate plan based on the payment
        user.plan_started_time = datetime.utcnow()  # Set the appropriate plan start time
        user.plan_ended_time = datetime.utcnow() + timedelta(days=30)  # Set the appropriate plan end time

        # Update the credit_transfer table
        new_credit_transfer = CreditTransfer(
            credit=invoice_amount,
            uid_user=uid_user,
            note=note
        )
        session.add(new_credit_transfer)

        # Commit the changes to the database
        session.commit()
        
def update_credit_and_record_transfer(user_id, credit_change, note):
    # Find the user in the database
    user = session.query(User).filter_by(uid_user=user_id).first()

    if user:
        # Update the credit in the user table
        user.credit += credit_change

        # Record the credit transfer in the credit_transfer table
        credit_transfer = CreditTransfer(
            credit=credit_change,
            uid_user=user_id,
            note=note,
            time_created=datetime.now()
        )
        session.add(credit_transfer)

        # Commit the changes to the database
        session.commit()

        # Close the session
        session.close()

        return True
    else:
        return False
    

session.close()