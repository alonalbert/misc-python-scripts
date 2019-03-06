import sys

import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SECRET_FILE = os.path.expanduser('~/.duolingo-tracker-client.json')
RANGE_NAME = 'Log!A1:D4'

if __name__ == '__main__':
    credentials = service_account.Credentials.from_service_account_file(SECRET_FILE, scopes=SCOPES)
    service = discovery.build('sheets', 'v4', credentials=credentials)

    sheet = service.spreadsheets()

    spreadsheetId = sys.argv[1]

    result = sheet.values().get(spreadsheetId=spreadsheetId, range=RANGE_NAME).execute()
    values = result.get('values', [])
    print(values)