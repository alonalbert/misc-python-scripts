import datetime
import os
import pprint
import re

from apiclient import discovery
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SECRET_FILE = os.path.expanduser('~/.duolingo-tracker-client.json')
RANGE = 'Sheet1'

PP = pprint.PrettyPrinter(indent=2, depth=15)

CELL_REGEX = re.compile(r'([A-Z]\$?)([\d+])')


def update_sheet(spreadsheet_id):
  credentials = service_account.Credentials.from_service_account_file(SECRET_FILE, scopes=SCOPES)
  spreadsheets = discovery.build('sheets', 'v4', credentials=credentials).spreadsheets()

  values = spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=RANGE, valueRenderOption='FORMULA').execute()['values']
  row = len(values)
  col = len(values[row - 1])

  request = {
    "requests": [
      {
        "copyPaste": {
          "source": {
            "sheetId": 0,
            "startRowIndex": 1,
            "endRowIndex": row,
            "startColumnIndex": 0,
            "endColumnIndex": col,
          },
          "destination": {
            "sheetId": 0,
            "startRowIndex": 2,
            "endRowIndex": 3,
            "startColumnIndex": 0,
            "endColumnIndex": col,
          },
          "pasteOrientation": "NORMAL",
          "pasteType": "PASTE_NORMAL"
        },
      },
      {
        "updateCells": {
          "rows": [
            {
              "values": [
                {
                  "userEnteredValue": {
                    "numberValue": row
                  }
                }
              ]
            }
          ],
          "start": {
            "sheetId": 0,
            "rowIndex": 1,
            "columnIndex": 0,
          },
          "fields": "*"
        }

      }
    ]
  }
  spreadsheets.batchUpdate(spreadsheetId=spreadsheet_id, body=request).execute()



if __name__ == '__main__':
  update_sheet('1msg2268HrBDSv2E57T6hnYsIQC-KSQPkpK5z1bXkDO4')
