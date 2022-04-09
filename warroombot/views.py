from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from sj_auth import dosejong_api

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
                                    "text": "처리 중 오류가 발생했어..."
                                }
                            }
                        ]
                    }
                })

@csrf_exempt
def create(request):
    try:
        body = convertBytetoJson(request)
        if checkData(body, 'createBooking', '사이버워룸 예약 생성') and getCreateItem(body):
            return normalresponse
        else:
            return abnormalresponse
    except KeyError:
        print("No Key in json")
        return abnormalresponse


@csrf_exempt
def delete(request):
    body = convertBytetoJson(request)
    print(body)
    return JsonResponse({
        'ans':'test delete',
    })

@csrf_exempt
def retrieve(request):
    body = convertBytetoJson(request)
    print(body)
    return JsonResponse({
        'ans':'test retrieve',
    })

@csrf_exempt
def getCalendar(request):
    body = convertBytetoJson(request)
    print(body)
    return JsonResponse({
        'ans':'test getCalendar',
    })

def convertBytetoJson(request):
    decodedata = request.body.decode('utf8').replace("'", '"')
    data = json.loads(decodedata)
    return data

def printJson(jsondata):
    jsonbody = json.dumps(data, indent=4, sort_keys=True)
    print(jsonbody)

def checkData(body, actionname, intentname):
    try:
        if body['action']['name'] == actionname and body['bot']['name'] == '워루미' and body['intent']['name'] == intentname:
            return True
        else:
            return False
    except KeyError:
        print("No Key in json")
        return False

def getCreateItem(body):
    try:
        dictionary = {}
        utterance = body['userRequest']['utterance']
        nonspace = utterance.replace(" ", "")
        reservation = nonspace.split('\n')
        for content in reservation:
            keyvalue = content.split(':')
            key = keyvalue[0]
            value = keyvalue[1]
            dictionary[key] = value
        print(dictionary)
        # get table data
    except IndexError:
        print('no \":\" or \"\\n\" letter')
        return False
        
def getDOW(dow): #get date
    dow = dow.replace("요일", "")
    if dow == "월":
        return "mon"
    elif dow == "화":
        return "tue"
    elif dow == "수":
        return "wed"
    elif dow == "목":
        return "thu"
    elif dow == "금":
        return "fri"
    elif dow == "토":
        return "sat"
    elif dow == "일":
        return "sun"
    else:
        return "err"

def getTime(time):
    time = time.split("~")
    # 시작 시간, 끝 시간

def getNOS(nos):
    try:
        nos = nos.replace("명", "")
        if nos == "":
            return "err"
        else:
            return int(nos)
    except ValueError:
        print("please input num in nos")
        return "err"

def getUser(userdata):
    try:
        userdata = userdata.split('/')
        result = dosejong_api(userdata[0], userdata[1])
        if result['result']:
            return result['name'], result['id']
        else:
            print("there is no user in sejong univ.")
            return "err", ""
    except IndexError:
        print("there is no \"/\" in userdata")
        return "err", ""