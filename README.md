# mis-utomatizaciones
Scripts de automatización personal
# 🤖 Personal Automations

Automated personal workflows powered by AI, running 100% in the cloud via GitHub Actions — no local machine required.

Built by [Manuel Mesonero Medina](https://github.com/mmesonero)

---

## 📬 Gmail Auto-Labeler

Automatically classifies incoming emails into custom labels using GPT-4o-mini.

### How it works

1. Connects to Gmail via IMAP
2. Fetches the latest 50 emails from the inbox
3. Skips emails that already have a custom label
4. Sends subject, sender and body to GPT-4o-mini
5. GPT decides which label fits best based on custom descriptions
6. Applies the label directly in Gmail

### Labels

Labels and their descriptions are defined in `config.json` — fully editable without touching the code.

| Label | Description |
|---|---|
| ¡URGENTE! | Emails requiring immediate attention |
| BASURA | Spam and unwanted promotions |
| NEWSLETTER | Newsletters and marketing emails |
| NOTIFICACIONES | Automatic app and service notifications |
| FACTURAS | Invoices, receipts and financial documents |
| ALERTAS SEGURIDAD | Login alerts and security notifications |
| JOB ALERTS | Job offers, LinkedIn and recruitment |
| ¡CONTESTAR! | Personal emails requiring a reply |
| PKMN | Pokémon, Cardmarket, Wallapop and Vinted |
| PISOS | Real estate, Idealista and mortgages |
| OTHER | Emails that don't fit any other category |

### Stack

- **Python 3.11**
- **OpenAI API** — GPT-4o-mini for classification
- **Gmail IMAP** — for reading and labeling emails
- **GitHub Actions** — runs every 4 hours, no server needed

---

## ⚙️ Setup

### 1. Fork this repository

### 2. Add GitHub Secrets

Go to `Settings → Secrets and variables → Actions` and add:

| Secret | Description |
|---|---|
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_CREDENTIALS` | Gmail App Password (16 characters, no spaces) |
| `OPENAI_API_KEY` | Your OpenAI API key |

### 3. Enable Gmail App Password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Create a new app
