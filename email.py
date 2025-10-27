from email.message import EmailMessage
import ssl
import smtplib

def send_email(sender, recipients, subject, body, email_app_password, smtp_server="smtp.gmail.com", smtp_port=465):

    if not sender  or not sender.strip() or not recipients or not subject or not subject.strip() or not body or not body.strip() or not email_app_password or not email_app_password.strip():
        return False
    if isinstance(recipients, str):
        if not recipients.strip():
            return False
        recipients_str = recipients
    elif isinstance(recipients, list):
        if len(recipients) == 0:
            return False
        if not all(email and email.strip() for email in recipients):
            return False
        recipients_str = ", ".join(recipients)
    else:
        return False
    
    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = recipients_str
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as smtp:
            smtp.login(sender, email_app_password)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error al enviar el mail: {e}")
        return False
    
    return True
