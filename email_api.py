import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os

sender_email = "1nguyenhuuhieu@gmail.com"  # Replace with your sender email address
sender_password = "qlwzbxcnfvceiwfb"  # Replace with your sender email password


def send_html_email(receiver_email, subject, html_content):


    # Create a multipart message and set the headers
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the HTML content to the message
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    # Create a secure SSL connection to the email server
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

        # Close the connection to the server
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)

# Function to generate the HTML content for the email
def generate_html_content(payment_link):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tazapay Transaction Guide</title>
        <style>
            /* Add your CSS styles here to design the email template */
            /* ... */
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Guide for Tazapay Transaction</div>
            <div class="content">
                <p>Dear Customer,</p>
                <p>Thank you for choosing Tazapay for your transaction.</p>
                <p>Please follow the steps below to complete your transaction:</p>
                <ol>
                    <li>Click the button below to access the Tazapay payment link.</li>
                    <li>Complete the payment process on the Tazapay website.</li>
                    <li>Once the payment is successful, you will receive a confirmation email.</li>
                </ol>
                <p>If you have any questions or need further assistance, please don't hesitate to contact us.</p>
                <a class="button" href="{payment_link}">Access Tazapay Payment Link</a>
            </div>
            <div class="footer">This email is for informational purposes only. Do not reply to this email.</div>
        </div>
    </body>
    </html>
    """


def send_email(receiver_email, subject, message):

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [receiver_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

def send_email2(receiver_email, subject, template_file, context):
    # SMTP email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Load the template file
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template(template_file)

    # Render the template with the provided context
    email_body = template.render(context)

    # Prepare the email content
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(email_body, "html"))

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False