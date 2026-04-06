import os
import json
import base64
import imaplib
import email
from email.header import decode_header
from openai import OpenAI

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_gmail_connection():
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_CREDENTIALS"]
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(gmail_user, gmail_password)
    return mail

def get_unread_emails(mail):
    mail.select("inbox")
    _, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    return email_ids[-20:] if len(email_ids) > 20 else email_ids

def get_email_details(mail, email_id):
    _, msg_data = mail.fetch(email_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])

    # Asunto
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    # Remitente
    sender = msg.get("From", "Desconocido")

    # Body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

    body = ' '.join(body.split()[:300])
    return subject, sender, body

def build_prompt(subject, sender, body, labels):
    etiquetas = "\n".join(
        f"- {l['nombre']}: {l['descripcion']}" for l in labels
    )
    return f"""Eres un asistente que clasifica emails en etiquetas.

Estas son las etiquetas disponibles y su descripción:
{etiquetas}

Email a clasificar:
- Remitente: {sender}
- Asunto: {subject}
- Contenido: {body}

Responde ÚNICAMENTE con el nombre exacto de una etiqueta de la lista, sin explicaciones."""

def decide_label(subject, sender, body, labels):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = build_prompt(subject, sender, body, labels)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()

def apply_label(mail, email_id, label_name):
    # Convertir nombre de etiqueta a formato IMAP de Gmail
    label_imap = label_name.replace(" ", "-")
    try:
        mail.store(email_id, "+X-GM-LABELS", f'"{label_name}"')
        print(f"✅ Etiqueta aplicada: {label_name}")
    except Exception as e:
        print(f"⚠️ No se pudo aplicar etiqueta {label_name}: {e}")

def main():
    config = load_config()
    labels = config['labels']
    mail = get_gmail_connection()
    email_ids = get_unread_emails(mail)

    if not email_ids:
        print("No hay emails sin leer")
        return

    for email_id in email_ids:
        subject, sender, body = get_email_details(mail, email_id)
        label = decide_label(subject, sender, body, labels)
        label_names = [l['nombre'] for l in labels]
        if label in label_names:
            apply_label(mail, email_id, label)
            print(f"✅ {subject[:50]} → {label}")
        else:
            print(f"⚠️ {subject[:50]} → etiqueta no reconocida: {label}")

    mail.logout()

if __name__ == "__main__":
    main()
