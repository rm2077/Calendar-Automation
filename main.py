import os
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

API_KEY = "YOUR_API_KEY"
def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

    ### Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)
        # with open(os.path.join(working_dir, token_dir, token_file), 'rb') as token:
        #   cred = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None


CLIENT_SECRET_FILE = "credentials.json"
API_NAME = "calendar"
API_VERSION = "v3"
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
calendar_list = service.calendarList().list(pageToken=None).execute()
calendar_id = calendar_list["items"][0]["id"]
def add_events():
    while True:
        summary = input("Give a summary about the event: ")
        loc = input("Location: ")
        description = input("Add on what the event will be about: ")
        start_time = str(input("When will the event start? (yyyy-mm-dd) "))
        end_time = str(input("When will the event end? (yyyy-mm-dd) "))
        event = {
        'summary': summary,
        'location': loc,
        'description': description,
        'start': {
            'date': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'date': end_time,
            'timeZone': 'America/Los_Angeles',
        }
        }
        service.events().insert(calendarId=calendar_id, body=event).execute()
        print("Your event has been added")
        inp = input("Do you want to continue? (y, n)").lower()
        if inp == "n" or inp == "no":
            break
        
        


def delete_events():
    while True:
    
        calendar_book = get_events_list()
        for key in calendar_book.keys():
            print(key)
        inp = input("Which event do you want to delete?")
        if inp == "break":
            break
        event_id = calendar_book[inp]
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        del calendar_book[inp]
        print("Your event has been deleted.")
    

def get_events_list():
    calendar_book = {}
    events = service.events().list(calendarId=calendar_id).execute()
    for event in events["items"]:
        event_id = event["id"]
        event_summary = event.get("summary")
        calendar_book[event_summary] = event_id
    return calendar_book


def main():
    print("Welcome!")
    while True:
        print("1. Adding events to calendar")
        print("2. Deleting events from calendar")
        try:
            inp = input("Enter a number")
            if inp == "1":
                add_events()
            if inp == "2":
                delete_events()
            if inp == "break":
                print("See you later!")
                break
        except Exception as e:
            print("Error occured. Try again", e)
            

if __name__ == "__main__":
    main()