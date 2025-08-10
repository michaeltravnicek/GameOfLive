
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

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

ENGINE = create_engine("postgresql+psycopg2://citizix_user:S3cret@localhost:5432/postgres")

def insert_event(sheet: dict):
    with Session(ENGINE) as session:
        stmt = text(
            "INSERT INTO event (sheet_id, place, date) VALUES (:sheet_id, :place, :date) RETURNING id"
        )
        session.execute(stmt.bindparams(sheet_id=sheet["id"], place="Brno", date=datetime.now())).first()


def handle_events(sheets: dict):
    for sheet in sheets["files"]:
        with Session(ENGINE) as session:
            stmt = text(
                "SELECT * FROM event WHERE event.sheet_id=:sheet_id"
            )
            result = session.execute(stmt.bindparams(sheet_id=sheet["id"])).first()
            if result is None:
                insert_event(sheet)   


def main():
    query = "mimeType='application/vnd.google-apps.spreadsheet'"
    
    sheets = service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name)"
    ).execute()

    handle_events(sheets)

    




if __name__ == "__main__":
    main()

