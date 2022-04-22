from __future__ import print_function
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import json

def get_secret(setting):
    with open(secret_file, 'r') as f:
        secrets = json.loads(f.read())
        try:
            return secrets[setting]
        except KeyError:
            error_msg = "Set the {} environment variable".format(setting)
            raise ImproperlyConfigured(error_msg)

secret_file = 'secrets.json'
gstokenpath = 'googlesheetstoken.json'
credspath = 'credentials.json'

SCOPES = []
SCOPES.append(get_secret("SPREADSHEETSCOPES"))
SAMPLE_SPREADSHEET_ID = get_secret("SPREADSHEETID")
SAMPLE_RANGE_NAME = get_secret("SPREADSHEETRANGE")

def main():
    creds = None
    if os.path.exists('googlesheetstoken.json'):
        creds = Credentials.from_authorized_user_file('googlesheetstoken.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('googlesheetstoken.json', 'w') as token:
            token.write(creds.to_json())
            print('success make token')

if __name__ == '__main__':
    main()