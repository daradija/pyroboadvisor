from email.message import EmailMessage
import ssl
import smtplib
import requests

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


def send_telegram(bot_token, chat_ids, message):
    
    if not bot_token or not bot_token.strip() or not chat_ids or not message or not message.strip():
        return False
    
    if isinstance(chat_ids, str):
        if not chat_ids.strip():
            return False
        chat_ids = [chat_ids]
    elif isinstance(chat_ids, list):
        if len(chat_ids) == 0:
            return False
        if not all(chat_id and str(chat_id).strip() for chat_id in chat_ids):
            return False
    else:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        for chat_id in chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            response = requests.post(url, json=payload)
            if not response.ok:
                print(f"Error al enviar mensaje de Telegram a {chat_id}: {response.text}")
                return False
    except Exception as e:
        print(f"Error al enviar mensaje de Telegram: {e}")
        return False
    
    return True

def send_discord(webhook_url, message):
    
    if not webhook_url or not webhook_url.strip() or not message or not message.strip():
        return False
    
    try:
        payload = {
            "content": message
        }
        response = requests.post(webhook_url, json=payload)
        if not response.ok:
            print(f"Error al enviar mensaje de Discord: {response.text}")
            return False
    except Exception as e:
        print(f"Error al enviar mensaje de Discord: {e}")
        return False
    
    return True
