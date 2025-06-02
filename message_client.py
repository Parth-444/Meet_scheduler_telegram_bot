import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Any, Optional
from twilio.rest import Client
class Sender:
    def __init__(self):
        self.account_sid = os.getenv('twilio_sid')
        self.auth_token = os.getenv('twilio_auth_token')
        self.twilio_number = os.getenv('twilio_phone_number')
        self.to_number = os.getenv('my_phone_number')
        self.client = Client(self.account_sid, self.auth_token)

        self._validate_env_vars()

    def _validate_env_vars(self):
        missing = []
        for var in ['twilio_sid', 'twilio_auth_token', 'twilio_phone_number', 'my_phone_number']:
            if not os.getenv(var):
                missing.append(var)
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    def send_message(self, to: str, body: str) -> str:
        """
        Sends an SMS using Twilio.
        :param to: Recipient's phone number
        :param body: Message text
        :return: Message SID if successful
        """
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.twilio_number,
                to=to
            )
            print(f"✅ Message sent to {to} | SID: {message.sid}")
            return message.sid
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return ""


def get_llm():
    key = os.getenv('GOOGLE_API_KEY')
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=key)

if __name__ == "__main__":
    twilio_client = Sender()
    twilio_client.send_message(
        to=twilio_client.to_number,
        body="📱 This is a test message from your upgraded Python bot!"
    )