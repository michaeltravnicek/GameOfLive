
from __future__ import annotations
from typing import List
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

ENGINE = create_engine("postgresql+psycopg2://citizix_user:S3cret@localhost:5432/postgres")

def insert_event(sheet: dict):
    with Session(ENGINE) as session:
        stmt = text(
            "INSERT INTO event (sheet_id, place, date) VALUES (:sheet_id, :place, :date) RETURNING id"
        )
        session.execute(stmt.bindparams(sheet_id=sheet["id"], place="Brno", date=datetime.now())).first()
        session.commit()



def handle_events(sheets: dict):
    for sheet in sheets["files"]:
        with Session(ENGINE) as session:
            stmt = text(
                "SELECT * FROM event WHERE event.sheet_id=:sheet_id"
            )
            result = session.execute(stmt.bindparams(sheet_id=sheet["id"])).first()
            if result is None:
                insert_event(sheet)   


def get_event_by_sheet_id(sheet_id: str):
    with Session(ENGINE) as session:
        stmt = text(
           "SELECT * FROM event WHERE sheet_id=:sheet_id"
        )
        result = session.execute(stmt.bindparams(sheet_id=sheet_id)).first()
        return result


def handle_new_user(rec: tuple) -> int:
    with Session(ENGINE) as session:
        stmt = text(
            'SELECT * FROM "user" WHERE number=:user_number'
        )
        user = session.execute(stmt.bindparams(user_number=rec[1])).first()
        if user is not None:
            print("USER FOUND", user)
            return user[0]

        stmt = text(
            'INSERT INTO "user" (name, number) VALUES (:name, :number) RETURNING ID'
        )
        result = session.execute(stmt.bindparams(name=rec[2], number=rec[1]))
        session.commit()
        new_id = result.scalar()

        print(f"Inserted user ID: {new_id}")
        return new_id



def insert_rec(event_id: int, rec: tuple):
    user_id = handle_new_user(rec)
    with Session(ENGINE) as session:
        stmt = text(
            "INSERT INTO user_to_event VALUES (:user_id, :event_id)"
        )
        session.execute(stmt.bindparams(user_id=user_id, event_id=event_id))
        session.commit()


def handle_attendance(sheet_id: int, records: list):
    event = get_event_by_sheet_id(sheet_id)
    event_id = event[0]
    with Session(ENGINE) as session:
        stmt = text(
            "SELECT * FROM user_to_event WHERE event_id=:event_id"
        )
        database_records = session.execute(stmt.bindparams(event_id=event_id)).all()

    len_diff = len(database_records) - len(records) + 1
    if len_diff == 0:
        return

    for rec in records[len_diff:]:
        insert_rec(event_id, rec)



def main():
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
    for sheet_info in sheets["files"]:
        sheet_id = sheet_info["id"]

        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=1 # Zautomatizovat
        ).execute()
        handle_attendance(sheet_id, result["values"])



if __name__ == "__main__":
    main()

