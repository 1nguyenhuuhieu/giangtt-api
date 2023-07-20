import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_html_email(receiver_email, subject, html_content):
    # Replace the following variables with your email and password
    sender_email = "1nguyenhuuhieu@gmail.com"
    sender_password = "qlwzbxcnfvceiwfb"

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
