import re
from background_task import background
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

from leaderboard.models import Event, User, UserToEvent  # import modelů
from django.core.cache import cache

from leaderboard.models import Event, User, UserToEvent

SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]
SERVICE_ACCOUNT_FILE = '../credentials.json'

RUN_ALL = False


def parse_phone_number(raw_number: str) -> str:
    if not raw_number:
        return None

    clean_number = re.sub(r"\D", "", raw_number)
    return clean_number
    #if len(clean_number) == 9:
    #    return clean_number
    #else:
    #    return None


def insert_event(sheet_id: str, sheet: dict):
    sheet_list_id = str(sheet["properties"]["sheetId"]) 
    sheet_name = sheet["properties"]["title"]

    event, created = Event.objects.get_or_create(
        sheet_id=sheet_id,
        sheet_list_id=sheet_list_id,
        defaults={
            "name": sheet_name,
            "points": 50,
            "place": "Brno",
            "date": datetime.now(),
        }
    )
    return event


def handle_events(sheets: dict):
    for sheet in sheets.get("sheets", []):
        print("insert: ", sheet["name"])
        insert_event(sheet)


def handle_new_user(rec: tuple) -> User | None:
    """
    rec[1] = number, rec[2] = name
    """
    number = parse_phone_number(rec[1])
    if number is None:
        print("Invalid Number!")
        return

    user, created = User.objects.get_or_create(
        number=number,
        defaults={"name": rec[2]}
    )
    if not created:
        print("USER FOUND", user)
    else:
        print(f"Inserted user ID: {user.id}")
    return user


def insert_rec(event: Event, rec: tuple):
    user = handle_new_user(rec)
    if user is None:
        return

    if len(rec) > 3:  # Cas, Telefon, Jmeno, ..., Body
        points = rec[-1]
    else:
        points = event.points

    ute, created = UserToEvent.objects.get_or_create(
        user=user,
        event=event,
        defaults={"points": points},
    )

    if not created and ute.points != points:
        ute.points = points
        ute.save(update_fields=["points"])




def handle_attendance(sheet_id: str, sheet_list_id: str, records: list):
    try:
        event = Event.objects.get(sheet_id=sheet_id, sheet_list_id=sheet_list_id)
    except Event.DoesNotExist:
        return

    existing_count = UserToEvent.objects.filter(event=event).count()
    if cache.get("last_update"):
        new_records = records[1:] 
    else:
        new_records = records[1+existing_count:] if existing_count < len(records) else []
    
    for rec in new_records:
        insert_rec(event, rec)


def main():
    print("Running")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=creds)
    query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed = false"

    sheets = service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name)"
    ).execute()


    for sheet_info in sheets.get("files", []):
        sheet_id = sheet_info["id"]

        service_sheets = build("sheets", "v4", credentials=creds)
        spreadsheet = service_sheets.spreadsheets().get(
            spreadsheetId=sheet_id
        ).execute()

        #handle_events(sheet_info)

        for sheet_meta in spreadsheet.get("sheets", []):
            title = sheet_meta["properties"]["title"]
            print(f"Processing sheet: {title}")
            insert_event(sheet_id, sheet_meta)
            
            result = service_sheets.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=title
            ).execute()

            sheet_list_id = str(sheet_meta["properties"]["sheetId"]) 
            handle_attendance(sheet_id, sheet_list_id, result.get("values", []))


@background(schedule=60)
def run_google_sheet_sync():
    main()
    #run_google_sheet_sync()
