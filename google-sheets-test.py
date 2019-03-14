import datetime
import os
import pprint
import re

from apiclient import discovery
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SECRET_FILE = os.path.expanduser('~/.duolingo-tracker-client.json')
DAY_ZERO = datetime.datetime(1899, 12, 30)
RANGE = 'Sheet1'

PP = pprint.PrettyPrinter(indent=2, width=40)

CELL_REGEX=re.compile(r'([A-Z]\$?)([\d+])')

def update_formulas(values):
  for (i, row) in enumerate(values[2:]):
    for (j, cell) in enumerate(row):
      if isinstance(cell, str) and cell.startswith('='):
        row[j] = CELL_REGEX.sub(lambda m: m.group(1) + str(int(m.group(2)) + 1), cell)


def update_sheet(spreadsheet_id):
  credentials = service_account.Credentials.from_service_account_file(SECRET_FILE, scopes=SCOPES)
  service = discovery.build('sheets', 'v4', credentials=credentials)
  values_api = service.spreadsheets().values()
  request = values_api.get(spreadsheetId=spreadsheet_id, range=RANGE, valueRenderOption='FORMULA')
  response = request.execute()
  values = response['values']

  values.insert(1, values[1].copy())

  PP.pprint(values)
  update_formulas(values)

  PP.pprint(values)



if __name__ == '__main__':
  update_sheet('1msg2268HrBDSv2E57T6hnYsIQC-KSQPkpK5z1bXkDO4')
