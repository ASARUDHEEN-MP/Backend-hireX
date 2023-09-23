import ssl
import smtplib
from email.mime.text import MIMEText
from django.template.loader import render_to_string


def send_mail(subject, message, from_email, recipient_list):
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = 'hirexjobs66@gmail.com'
    smtp_password = 'jylswpghjznvnyvo'
    email_body = f"{message}\n\nThank you for applying the job!"
    msg = MIMEText(email_body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(recipient_list)

    try:
        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=ssl_context)
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, recipient_list, msg.as_string())
        return True, 'Email sent successfully.'
    except Exception as e:
        # Handle any exceptions or errors here
        print(f"Error sending email: {e}")
        return False, f"Failed to send email: {e}"
