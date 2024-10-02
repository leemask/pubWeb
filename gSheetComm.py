
from googleapiclient.discovery import build
from numpy import imag
from google.oauth2.service_account import Credentials
import os
import pandas as pd
import ast

SERVICE_ACCOUNT_FILE = 'gsheetAccount.json'        
platform = {
    'baemin': '1iy2KQgdmbzjZ5Uz-ysjQF4s5B94nO_ql9BJ9QUVu4MU',
    'coupang': '1G-HTMj0qzkoFA-fAMvW4fUYjhpZgg5CfeDOWcYyvOKo',
    'yogi': '1SPoWID6pLPqC4LT4Ojxo7TrCH2ZdOBu5tScmEbtLwV8'
}

class gSheetComm:
    def __init__(self, site_name):
        global service
        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        credentials = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.file_id = platform[site_name]
        service = build('sheets', 'v4', credentials=credentials)
    
    # 데이터를 한 번에 한 행씩 기록하는 함수
    def append_row(self, row, range_name='Sheet1'):
        body = {
            'values': [row]
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=self.file_id, range=range_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        print('{0} cells appended.'.format(result \
                                            .get('updates') \
                                            .get('updatedCells')))

    def add_new_sheet(self, sheet_name = 'Sheet1'):
        body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": sheet_name,
                            'gridProperties': {'rowCount': 20,
                                'columnCount': 12
                            }
                        }
                    }
                }
            ]
        }
        try : 
            response = service.spreadsheets().batchUpdate(
                spreadsheetId=self.file_id,
                body=body
            ).execute()
        except Exception as e:
            print(f"Add sheet : An error occurred: {e}")
            return None
        print(f"Added new sheet: {sheet_name}") 
        # Get the new sheet ID
        new_sheet_id = response['replies'][0]['addSheet']['properties']['sheetId'] 
        return new_sheet_id

    def update_sheet(self, sheet_name = 'Sheet1', start_line=1, values = []):

        data = {
            'range': f"{sheet_name}!A{start_line}",  # Specify the range where you want to insert data
            'majorDimension': 'ROWS',
            'values': values
        }
        try :
            # Use update to put values in the specified range
            result = service.spreadsheets().values().update(
                spreadsheetId=self.file_id,
                range=data['range'],
                valueInputOption='RAW',  # Use 'RAW' to input data as-is, or 'USER_ENTERED' for user interpretation
                body=data
            ).execute()
        except Exception as e:
            print(f"update_sheet: {e}")
            return None
        print(f"{result.get('updatedCells')} cells updated in '{sheet_name}'.")
        
    def get_sheet_names(self):
        try:
            # Request to get spreadsheet metadata
            spreadsheet = service.spreadsheets().get(spreadsheetId=self.file_id).execute()
            # Extract the sheet names
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            return sheet_names
        except Exception as e:    
            print(f"An error occurred: {e}")
            return None
    def delete_sheet(self, sheet_name_to_delete='Sheet1'):
        # Request to get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=self.file_id).execute()
        # Find the sheet ID based on the sheet name
        sheet_id_to_delete = None
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == sheet_name_to_delete:
                sheet_id_to_delete = sheet['properties']['sheetId']
                break
        # Extract the sheet names
        if sheet_id_to_delete is None:
            print(f"Sheet '{sheet_name_to_delete}' not found.")
 
        else:
            # Define the batch update request to delete the sheet
            batch_update_spreadsheet_request_body = {
                'requests': [
                    {
                        'deleteSheet': {
                            'sheetId': sheet_id_to_delete
                        }
                    }
                ]
            }

            # Call the Sheets API to execute the batch update
            try:
                response = service.spreadsheets().batchUpdate(
                    spreadsheetId=self.file_id,
                    body=batch_update_spreadsheet_request_body
                ).execute()
                print(f"Sheet '{sheet_name_to_delete}' deleted successfully.")
            except Exception as e:
                print(f"An error occurred: {e}")                
    
    def get_lines(self, range_name ):        
        # Retrieve the first 20 rows of the specified sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=self.file_id,
            range=range_name
        ).execute()

        # Get the values
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return None
        return values
    
    def create_fun(self, id, params):
        self.sheet_name = f"{id}"
        #self.delete_sheet(ID_NEW, self.sheet_name) #delete the previous run
        sheets = self.get_sheet_names()
        if(self.sheet_name not in sheets):
            self.sheet_name = self.add_new_sheet(self.sheet_name)  
        values = [            
            ["date", "event", "info", "log"],
            ['start','caller',f'{str(params)}', 'End']            
        ]
        print(values)
        self.update_sheet(self.sheet_name, 1, values)
        
        
    def stop_fun(self):
        print(self.sheet_name)
        if self.sheet_name:
            self.delete_sheet(self.sheet_name)

    def get_content_fun(self, range_name = 'Sheet1' ):        
        
        try:
            # Retrieve the data from the spreadsheet
            result = service.spreadsheets().values().get(spreadsheetId=self.file_id, range=range_name).execute()
            values = result.get('values', [])
            #print(values)
        except Exception as e:
            print(f"get_content_fun An error occurred:{self.file_id} {e}")
            return None
        return values

    def clear(self):
        existing_sheets = self.spreadsheet.worksheets()
        for sheet in existing_sheets:
            if sheet.title.startswith(id):
                self.spreadsheet.del_worksheet(sheet)

if __name__ == '__main__':
    gSheet = gSheetComm(platform['coupang'])
    gSheet.start_fun('test')
    gSheet.get_content_fun()

