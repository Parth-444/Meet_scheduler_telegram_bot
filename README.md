## 📅 Telegram Meeting Scheduler Bot
This is a Telegram bot built with Python that helps users schedule Google Meet meetings and send SMS reminders directly from chat.
It uses a Flask backend to handle authentication and API calls, while the Telegram bot provides a simple conversational interface.

## 🚀 Features
🔐 Google Sign-In for first-time users via OAuth (only once).

## 📅 Schedule Google Meet meetings by providing:

- Meeting topic

- Attendee email

## 📩 Send SMS/text reminders by entering:

- Message content

- Recipient's phone number

- 🔗 Returns the generated Google Meet link directly in Telegram.

## 🧰 Tech Stack
### Component	Tech Used
- Bot Framework	python-telegram-bot
- Backend	Flask
- OAuth	Google OAuth 2.0 (Service Accounts / OAuth Login)
- API	Google Calendar API, SMS API (e.g., Twilio)
- Environment	Python 3.10+, .env file for secrets

## 📦 Setup Instructions
1. Clone this repo
``` bash
git clone https://github.com/your-username/telegram-meeting-scheduler.git
cd telegram-meeting-scheduler
```
2. Install dependencies
bash
```
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
3. Environment Variables
Create a .env file in the project root:

bash
```
telegram_bot_token=YOUR_TELEGRAM_BOT_TOKEN
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service_account.json
```
Note: The GOOGLE_APPLICATION_CREDENTIALS should point to your Google service account JSON file.

4. Run the Flask Backend
This handles scheduling and user login via /login and /schedule:

bash
```
python flask_server.py
Ensure it runs on http://localhost:5000.
```
5. Run the Telegram Bot
In a separate terminal:

bash
```
python telegram_bot.py
```
## 💬 How to Use
- Start the bot

Type /start

- Click the login link and sign in with your Google account

- Schedule a meeting

Type /schedule

- Enter meeting description and attendee email

- Get back the Google Meet link

- Send a text reminder

Type /send_text

- Enter message and recipient phone number

-   Confirmation of successful message delivery

## 🛡️ Security Tips
- Avoid hardcoding credentials. Use environment variables.

- Never commit service_account.json to GitHub.

- Use HTTPS in production instead of localhost.

## 📁 Project Structure
bash
```
├── telegram_bot.py          # Main Telegram bot logic
├── flask_server.py          # Flask API for Google Meet & SMS
├── .env                     # Stores secrets (not committed)
├── service_account.json     # Google credentials (add to .gitignore)
└── requirements.txt         # Dependencies
```
## 🧪 Example
Telegram Bot Conversation:

bash
``
/start
``
- ➡ Click login link

/schedule
- ➡ What is the meeting about?
📩 Weekly Sync

- ➡ Attendee email?
👤 example@gmail.com

✅ Meeting scheduled!
📎 Link: https://meet.google.com/abc-defg-hij
