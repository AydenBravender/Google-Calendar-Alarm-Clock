import os.path
import datetime as dt
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def is_within_one_minute(now, end_time):
    one_minute_delta = dt.timedelta(minutes=1)
    return now >= (end_time - one_minute_delta) and now <= end_time

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        while True:
            now_utc = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
            now_minus_7_hours = now_utc - dt.timedelta(hours=7)

            event_result = service.events().list(
                calendarId="primary",
                q='Sleep',
                maxResults=1,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found!")
            else:
                for event in events:
                    end_time_utc_str = event['end'].get('dateTime', event['end'].get('date'))
                    end_time_utc = dt.datetime.fromisoformat(end_time_utc_str).replace(tzinfo=dt.timezone.utc)

                    print("Current UTC time:", now_minus_7_hours)
                    print("Event end time UTC:", end_time_utc)

                    if is_within_one_minute(now_minus_7_hours, end_time_utc):
                        print("Event is ending within one minute!")

            # Wait for one minute before checking again
            time.sleep(5)

    except HttpError as error:
        print("An error occurred:", error)

if __name__ == "__main__":
    main()
