import os
import sys
import datetime

from apiclient import discovery
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SECRET_FILE = os.path.expanduser('~/.duolingo-tracker-client.json')
DAY_ZERO = datetime.datetime(1899, 12, 30)

RANGE = 'Log!A1:D1'


def update_sheet(spreadsheet_id):
    credentials = service_account.Credentials.from_service_account_file(SECRET_FILE, scopes=SCOPES)
    service = discovery.build('sheets', 'v4', credentials=credentials)
    values_api = service.spreadsheets().values()
    request = values_api.get(spreadsheetId=spreadsheet_id, range='Log!A:D')
    response = request.execute()
    values = response['values']
    date = datetime.datetime.now() - DAY_ZERO
    print(date)
    values.insert(1, [date.days, 11, 12, 13])
    body = {
        'values': values
    }
    request = values_api.update(spreadsheetId=spreadsheet_id, range='Log!A:D',
                               valueInputOption='USER_ENTERED', body=body)
    request.execute()


if __name__ == '__main__':
    update_sheet(sys.argv[1])
