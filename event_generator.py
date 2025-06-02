import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import pytz
from typing import Dict, List, Any, Optional

def get_llm():
    key = os.getenv('GOOGLE_API_KEY')
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=key)


class Attendee(BaseModel):
    email: EmailStr
    responseStatus: Optional[str] = None
class CalendarEvent(BaseModel):
    summary: str = Field(..., description="Title or summary of the event.")
    start: Dict[str, str] = Field(..., description="Start time details with 'dateTime' and 'timeZone'.")
    end: Dict[str, str] = Field(..., description="End time details with 'dateTime' and 'timeZone'.")
    attendees: List[Attendee] = []
    reminders: Dict[str, Any] = Field(..., description="Reminder settings, including default usage and overrides.")
    sendUpdates: str = Field(default="all", description="'all' sends reminders to attendees")


class CalendarEventGenerator:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=CalendarEvent)

    def get_prompt(self):
        return PromptTemplate(
            template="""Current time in Kolkata: {current_time}

    Convert this meeting request into a Google Calendar event:
    "{user_input}"

    Attendee Email: {attendee_email}

    {format_instructions}

    **Requirements:**
    - Timezone: Asia/Kolkata (IST)
    - Duration: 1 hour if not specified  
    - Location: "Google Meet Link"
    - Description: Include AI/tech context when relevant
    - Reminders: 
      * Email (30 mins before) to ALL participants
      * Popup (10 mins before) for organizer
    - Attendee status: Pre-set as "accepted"
    - DateTime format: 2025-04-03T10:00:00+05:30""",
            input_variables=["user_input", "attendee_email"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions(),
                "current_time": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
            }
)

    def generate_calendar_event(self, user_input, attendee_email):
        prompt = self.get_prompt()
        chain = prompt | self.llm | self.parser
        event_obj = chain.invoke({'user_input': user_input, 'attendee_email': attendee_email})

        event_dict = event_obj.model_dump()

        if not event_dict.get('attendees'):
            # event_dict['attendees'] = [{
            #     "email": attendee_email,
            #     "responseStatus": "accepted"
            # }]
            event_dict["attendees"] = [{"email": email} for email in attendee_email]
        else:
            # event_dict['attendees'] = [
            #     {"email": attendee_email, "responseStatus": "accepted"}
            # ]
            event_dict["attendees"] = [{"email": email} for email in attendee_email]

        return event_dict

#
# if __name__ == "__main__":
#     generator = CalendarEventGenerator()
#     user_input = 'Meet today at 1:15 PM'
#     attendee_email = 'parthokazaki@gmail.com'
#     final_result = generator.generate_calendar_event(user_input, attendee_email)
#     print(final_result)
