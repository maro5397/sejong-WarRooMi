from __future__ import print_function
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from pathlib import Path
import os.path
import json
import logging

normalresponse = JsonResponse({
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": "정상 처리됐어!"
                                }
                            }
                        ]
                    }
                })

abnormalresponse = JsonResponse({
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": "처리중 오류가 발생했어"
                                }
                            }
                        ]
                    }
                })

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json')
gstokenpath = os.path.join(BASE_DIR, 'googlesheetstoken.json')
credspath = os.path.join(BASE_DIR, 'credentials.json')

@csrf_exempt
def googledrive(request):
    SCOPES = get_secret("SCOPES")
    SPREADSHEET_ID = get_secret("SPREADSHEETID")
    RANGE = get_secret("SPREADSHEETRANGE")

    creds = checkAuth()

    forbidlist = {'timerange':[], 'timetable':[[], [], [], [], [], [], []]}
    try:
        service = build('sheets', 'v4', credentials=creds)
        request = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, ranges=RANGE, includeGridData=True)
        response = request.execute()
        rowDatas = response['sheets'][0]['data'][0]['rowData']
        for rowData in rowDatas:
            values = rowData['values']
            forbidlist['timerange'].append(values[0]['formattedValue'])
            for i in range(0, 7):
                color = values[i+1]['effectiveFormat']['backgroundColor']
                if isWhite(color):
                    forbidlist['timetable'][i].append(1)
                else:
                    forbidlist['timetable'][i].append(0)

        print(forbidlist['timerange'])
        for forbidtimelist in forbidlist['timetable']:
            print(forbidtimelist)
        
    except HttpError as err:
        print(err)
        return abnormalresponse
    
    return normalresponse

def printJson(data):
    jsonbody = json.dumps(data, indent=4, sort_keys=True)
    print(jsonbody)

def isWhite(color):
    if len(color) == 3:
        if color['red'] == 1 and color['green'] == 1 and color['blue'] == 1:
            return True
        else:
            return False
    else:
        return False

def get_secret(setting):
    with open(secret_file, 'r') as f:
        secrets = json.loads(f.read())
        try:
            return secrets[setting]
        except KeyError:
            error_msg = "Set the {} environment variable".format(setting)
            raise ImproperlyConfigured(error_msg)

def checkAuth():
    creds = None
    if os.path.exists(gstokenpath):
        creds = Credentials.from_authorized_user_file(gstokenpath, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credspath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(gstokenpath, 'w') as token:
            token.write(creds.to_json())
    return creds