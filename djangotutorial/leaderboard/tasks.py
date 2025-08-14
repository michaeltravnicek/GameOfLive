from background_task import background
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

from leaderboard.models import Event, User, UserToEvent  # import modelů


from leaderboard.models import Event, User, UserToEvent

SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]
SERVICE_ACCOUNT_FILE = 'credentials.json'


def insert_event(sheet: dict):
    event, created = Event.objects.get_or_create(
        sheet_id=sheet["id"],
        points=50,
        defaults={"place": "Brno", "date": datetime.now()}
    )
    return event


def handle_events(sheets: dict):
    for sheet in sheets.get("files", []):
        insert_event(sheet)


def handle_new_user(rec: tuple) -> User:
    """
    rec[1] = number, rec[2] = name
    """
    user, created = User.objects.get_or_create(
        number=rec[1],
        defaults={"name": rec[2]}
    )
    if not created:
        print("USER FOUND", user)
    else:
        print(f"Inserted user ID: {user.id}")
    return user


def insert_rec(event: Event, rec: tuple):
    user = handle_new_user(rec)
    UserToEvent.objects.get_or_create(user=user, event=event)


def handle_attendance(sheet_id: str, records: list):
    try:
        event = Event.objects.get(sheet_id=sheet_id)
    except Event.DoesNotExist:
        return

    existing_count = UserToEvent.objects.filter(event=event).count()
    new_records = records[existing_count:] if existing_count < len(records) else []

    for rec in new_records[1:]:
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

    handle_events(sheets)

    for sheet_info in sheets.get("files", []):
        sheet_id = sheet_info["id"]

        service_sheets = build("sheets", "v4", credentials=creds)
        sheet = service_sheets.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=1  # Zautomatizovat podle potřeby
        ).execute()

        handle_attendance(sheet_id, result.get("values", []))


@background(schedule=300)
def run_google_sheet_sync():
    main()
    #run_google_sheet_sync(repeat=300)
