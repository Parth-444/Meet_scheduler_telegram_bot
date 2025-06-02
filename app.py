import os
import json
from flask import Flask, request, session, jsonify, redirect
from flask_session import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from event_generator import CalendarEventGenerator
from message_client import Sender
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_FILE_DIR"] = "./.flask_session/"
Session(app)

CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRET_FILE")
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = 'token.json'

def get_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:5000/callback"
    )

@app.route('/login')
def login():
    user_id = request.args.get('user_id')
    flow = get_flow()
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    if not credentials or not credentials.token:
        return jsonify({"error": "Failed to retrieve access token"}), 400

    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    with open(TOKEN_FILE, 'w') as token_file:
        json.dump(credentials_data, token_file)

    return jsonify({"message": "Login successful. You can now call /schedule"})


def get_calendar_service():
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE, 'r') as token_file:
        credentials_dict = json.load(token_file)

    credentials = Credentials.from_authorized_user_info(credentials_dict)

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        with open(TOKEN_FILE, 'w') as token_file:
            json.dump({
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }, token_file)

    return build('calendar', 'v3', credentials=credentials)


@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.get_json()
    meet_text = data.get('meet_text')
    attendee_email = data.get('attendee_email', [])
    print(attendee_email)
    attendee_email = str(attendee_email).split(', ')
    if not meet_text:
        return jsonify({"error": "No meeting prompt provided!"}), 400
    if not attendee_email:
        return jsonify({"error": "No attendee email provided!"}), 400

    service = get_calendar_service()
    if service is None:
        return jsonify({"error": "User not authenticated. Please log in via /login"}), 401

    event_generator = CalendarEventGenerator()
    event = event_generator.generate_calendar_event(meet_text, attendee_email)
    print(event)
    created_event = service.events().insert(
        calendarId='primary',
        sendNotifications=True,
        sendUpdates='all',
        conferenceDataVersion=0,
        body=event,

    ).execute()

    return jsonify({
        "status": "success",
        "event_link": created_event.get('htmlLink'),
        "event_id": created_event.get('id'),
        "attendee": attendee_email
    })
@app.route('/send_text', methods=['POST'])
def send():
    data = request.get_json()
    message = data.get("message")
    number = data.get("phone")

    sender = Sender()
    return sender.send_message(to=number, body=message)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
