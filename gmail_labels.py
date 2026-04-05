import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_gmail_service():
    creds_data = json.loads(os.environ["GMAIL_CREDENTIALS"])
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(service):
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=20
    ).execute()
    return results.get('messages', [])

def get_email_details(service, msg_id):
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='metadata',
        metadataHeaders=['Subject', 'From']
    ).execute()
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
    return subject, sender

def build_prompt(subject, sender, labels):
    etiquetas = "\n".join(
        f"- {l['nombre']}: {l['descripcion']}" for l in labels
    )
    return f"""Eres un asistente que clasifica emails en etiquetas.

Estas son las etiquetas disponibles y su descripción:
{etiquetas}

Email a clasificar:
- Remitente: {sender}
- Asunto: {subject}

Responde ÚNICAMENTE con el nombre exacto de una etiqueta de la lista, sin explicaciones."""

def decide_label(subject, sender, labels):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = build_prompt(subject, sender, labels)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()

def apply_label(service, msg_id, label_name):
    all_labels = service.users().labels().list(userId='me').execute()
    label_id = next(
        (l['id'] for l in all_labels['labels'] if l['name'] == label_name),
        None
    )
    if label_id:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'addLabelIds': [label_id]}
        ).execute()

def main():
    config = load_config()
    labels = config['labels']
    service = get_gmail_service()
    emails = get_unread_emails(service)

    for email in emails:
        subject, sender = get_email_details(service, email['id'])
        label = decide_label(subject, sender, labels)
        label_names = [l['nombre'] for l in labels]
        if label in label_names:
            apply_label(service, email['id'], label)
            print(f"✅ {subject[:50]} → {label}")
        else:
            print(f"⚠️ {subject[:50]} → etiqueta no reconocida: {label}")

if __name__ == "__main__":
    main()
