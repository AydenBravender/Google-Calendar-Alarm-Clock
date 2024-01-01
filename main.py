import multiprocessing
from playsound import playsound
import random
import tkinter as tk

import os.path
import datetime as dt
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def randomString():
    length = random.randint(5, 12)
    passwd = []
    for i in range(length):
        num = random.randint(65, 90)
        letter = chr(num)
        passwd.append(letter)
    random_string = ''.join(passwd)
    return random_string.lower()

def start_alarm():
    y = randomString()
    p = multiprocessing.Process(target=playsound, args=('test1.mp3',))
    p.start()

    root = tk.Tk()
    Header = root.title('Alarm Clock')

    my_canvas = tk.Canvas(root, bg="black", height=300, width=600)
    my_canvas.pack()

    label = tk.Label(root, text=f'Enter {y} to end Alarm: ')
    label.config(font=('helvetica', 14), fg='white', bg='black')
    my_canvas.create_window(300, 100, window=label)

    pass_code = tk.Entry(root)
    my_canvas.create_window(300, 150, height=30, width=400, window=pass_code)

    button = tk.Button(
        root,
        text="End Alarm",
        width=25,
        height=3,
        bg="black",
        fg="white",
        font=('helvetica', 10, 'bold'),
        command=lambda: Alarm(pass_code, p, y, root)
    )
    my_canvas.create_window(300, 250, height=40, width=150, window=button)

    root.mainloop()

def Alarm(pass_code, p, y, root):
    entered_password = pass_code.get()
    if entered_password == y:
        p.terminate()
        root.destroy()
        time.sleep(70)
        print("hii")
        main()
    else:
        # Password incorrect, clear the entry field for re-entry
        pass_code.delete(0, 'end')

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
                        start_alarm()
                        time.sleep(70)

            # Wait for one minute before checking again
            time.sleep(60)

    except HttpError as error:
        print("An error occurred:", error)

if __name__ == "__main__":
    main()
