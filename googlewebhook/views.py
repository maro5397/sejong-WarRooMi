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
from googlewebhook.models import Forbid
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

weeks = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json')
gstokenpath = os.path.join(BASE_DIR, 'googlesheetstoken.json')
credspath = os.path.join(BASE_DIR, 'credentials.json')

@csrf_exempt
def googledrive(request):
    try:
        body = convertBytetoJson(request)
        utterance = body['userRequest']['utterance']
        command = utterance.split()
        admininfo = command[1]
        result, adminid, adminpw = getIDandPW(admininfo)
        if not result:
            return abnormalresponse
        ID = get_secret("ADMINID")
        PW = get_secret("ADMINPW")
        if not isAdmin(ID, PW, adminid, adminpw):
            return abnormalresponse
    except (IndexError, KeyError):
        print("No Key in json or Wrong index")
        return abnormalresponse

    creds = checkAuth()
    SPREADSHEET_ID = get_secret("ID")
    RANGE = get_secret("RANGE")
    forbidlist = {'timerange':[], 'timetable':{
        'mo': [],
        'tu': [],
        'we': [],
        'th': [],
        'fr': [],
        'sa': [],
        'su': []
    }}
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
                    forbidlist['timetable'][weeks[i]].append(1)
                else:
                    forbidlist['timetable'][weeks[i]].append(0)
        if updateForbidTimeTable(forbidlist):
            return normalresponse
        
    except HttpError as err:
        print(err)
        return abnormalresponse

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
    SCOPES = []
    SCOPES.append(get_secret("SPREADSHEETSCOPES"))
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

def isAdmin(ID, PW, inputID, inputPW):
    return ID == inputID and PW == inputPW

def getIDandPW(admininfo):
    try:
        admininfo = admininfo.split('/')
        inputID = admininfo[0]
        inputPW = admininfo[1]
        return True, inputID, inputPW
    except IndexError:
        print("input wrong data format")
        return False, "", ""

def convertBytetoJson(request):
    decodedata = request.body.decode('utf8').replace("'", '"')
    data = json.loads(decodedata)
    return data

def updateForbidTimeTable(forbidlist):
    try:
        forbidrecords = Forbid.objects.all()
        forbidrecords.delete()
        numofrow = len(forbidlist['timerange'])
        for dow in forbidlist['timetable']:
            i = 0
            while i < numofrow:
                if forbidlist['timetable'][dow][i] == 0:
                    stindex = i
                    etindex = numofrow - 1
                    while i < len(forbidlist['timerange']):
                        if forbidlist['timetable'][dow][i] == 1:
                            etindex = i - 1
                            break
                        i += 1
                    st_range = forbidlist['timerange'][stindex]
                    et_range = forbidlist['timerange'][etindex]
                    stlist = st_range.split('~')
                    etlist = et_range.split('~')
                    st = stlist[0]
                    et = etlist[1]
                    forbid = Forbid(st=st, et=et, dow=dow)
                    forbid.save()
                i += 1
        return True
    except:
        print("Error in Forbid data save")
        return False