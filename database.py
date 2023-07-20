from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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


# Define the "credit_transfer" table using the ORM approach
class CreditTransfer(Base):
    __tablename__ = 'credit_transfer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    credit = Column(Float, nullable=False)
    uid_user = Column(String, nullable=False)
    note = Column(String)
    time_created = Column(DateTime, default=datetime.utcnow)



# Define the "user" table using the ORM approach
class User(Base):
    __tablename__ = 'user'

    uid_user = Column(String, primary_key=True)
    plan = Column(String, nullable=False)
    plan_started_time = Column(DateTime, nullable=True)
    plan_ended_time = Column(DateTime, nullable=True)
    credit = Column(Float, nullable=False, default=0)


# Create the database tables
Base.metadata.create_all(bind=engine)
# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


def create_payment():
    # Create a session to interact with the database
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # Example usage: Insert a new payment success record into the table
    new_payment = PaymentSuccess(invoice_amount=100, uid_user="user123", txn_no="2307-123456")
    session.add(new_payment)
    session.commit()

# Function to check if a txn_no exists in the payment_success table
def check_txn_no_exists(txn_no):
    result = session.query(PaymentSuccess).filter_by(txn_no=txn_no).first()
    return result is not None

def create_user():
    # Example usage: Insert a new user record into the table
    new_user = User(
        uid_user="user123",
        plan="Basic",
        plan_started_time=datetime.utcnow(),
        plan_ended_time=datetime.utcnow(),  # Set the appropriate end time for the plan
        credit=100.0
    )
    session.add(new_user)
    session.commit()


# Function to update the credit value for a specific uid_user
def update_user_credit(uid_user, amount_to_add):
    user = session.query(User).filter_by(uid_user=uid_user).first()
    if user:
        user.credit += amount_to_add
        session.commit()
        return True
    else:
        return False
    
# Function to update the plan and time for a specific uid_user
def update_user_plan(uid_user, new_plan, plan_start_time, plan_end_time):
    user = session.query(User).filter_by(uid_user=uid_user).first()
    if user:
        user.plan = new_plan
        user.plan_started_time = plan_start_time
        user.plan_ended_time = plan_end_time
        session.commit()
        return True
    else:
        return False
    

# Function to check if a uid_user exists in the user table
def check_user_exists(uid_user):
    result = session.query(User).filter_by(uid_user=uid_user).first()
    return result is not None

def update_credit_transfer():

    # Example usage: Insert a new credit transfer record into the table
    new_credit_transfer = CreditTransfer(
        credit=50.0,
        uid_user="user123",
        note="signup",
        time_created=datetime.utcnow()
    )
    session.add(new_credit_transfer)
    session.commit()

session.close()



# Function to handle payment success
def handle_payment_success(uid_user, invoice_amount, txn_no, note=None):
    # Update the payment_success table
    new_payment_success = PaymentSuccess(
        invoice_amount=invoice_amount,
        uid_user=uid_user,
        txn_no=txn_no,
    )
    session.add(new_payment_success)

    # Check if the user exists in the user table
    user = session.query(User).filter_by(uid_user=uid_user).first()

    # If the user does not exist, create a new user in the user table
    if not user:
        user = User(
            uid_user=uid_user,
            plan="Basic",  # Set the appropriate default plan
            plan_started_time=datetime.utcnow(),  # Set the appropriate default plan start time
            plan_ended_time=datetime.utcnow(),  # Set the appropriate default plan end time
            credit=0  # Set the appropriate default credit
        )
        session.add(user)

    # Update the credit and plan for the user
    user.credit += invoice_amount
    user.plan = "Premium"  # Set the appropriate plan based on the payment
    user.plan_started_time = datetime.utcnow()  # Set the appropriate plan start time
    user.plan_ended_time = datetime.utcnow()  # Set the appropriate plan end time

    # Update the credit_transfer table
    new_credit_transfer = CreditTransfer(
        credit=invoice_amount,
        uid_user=uid_user,
        note=note
    )
    session.add(new_credit_transfer)

    # Commit the changes to the database
    session.commit()

