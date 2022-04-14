from __future__ import print_function
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path


def main():
    SCOPES = get_secret("DRIVESCOPES")
    FI = get_secret("ID")
    #CI = random char 64 byte data save
    #CA = input URL where get notification
    #RI = have to get watch_channel

    creds = checkAuth()
    try:
        service = build('drive', 'v3', credentials=creds)
        # watch = watch_channel(service, FI, CI, CA)
        # print(watch)
        # stop = stop_channel(service, CI, RI)
        # print(stop)
    except HttpError as error:
        print(f'An error occurred: {error}')


def watch_channel(service, file_id, channel_id, channel_address, channel_type='web_hook'):
    body = {
        'id': channel_id,
        'type': channel_type,
        'address': channel_address
    }
    try:
        return service.files().watch(fileId=file_id, body=body).execute()
    except HttpError as error:
        print('An error occurred: %s' % error)
    return None


def stop_channel(service, channel_id, resource_id):
    body = {
        'id': channel_id,
        'resourceId': resource_id
    }
    try:
        return service.channels().stop(body=body).execute()
    except HttpError as error:
        print('An error occurred: %s' % error)


def checkAuth():
    creds = None
    if os.path.exists('googledrivetoken.json'):
        creds = Credentials.from_authorized_user_file('googledrivetoken.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('googledrivetoken.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_secret(setting):
    with open('secrets.json', 'r') as f:
        secrets = json.loads(f.read())
        try:
            return secrets[setting]
        except KeyError:
            error_msg = "Set the {} environment variable".format(setting)
            print(error_msg)
            return None


if __name__ == '__main__':
    main()
    