from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from warroombot.models import Booking, Forbid
import json
import logging
import datetime
import re
from . import sj_auth


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
                                    "text": "처리 중 오류가 발생했어"
                                }
                            }
                        ]
                    }
                })

requestlist = ['내용', '신청자']
roomid = "B208"
max_nos = 40

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

    userData = body['userRequest']['utterance'].strip()
    print(f"userData : {userData}")
    
    matchRule = re.compile("조회.*[: ](\d{3,15})\/(.*)")
    accountInformation = matchRule.fullmatch(userData)
    if accountInformation == None:
        print("입력 포맷이 잘못 되었음")
        return JsonResponse({
            'ans':'입력 잘못됨'
        })

    userID = accountInformation.group(1)
    userPW = accountInformation.group(2)

    result = sj_auth.dosejong_api(userID, userPW)
    result1 = result['result']

    if result1 != True:
        return JsonResponse({
            'ans':'로그인 실패함'
        })

    name = result['name']
    studentid = result['id']
    major = result['major']

    if not isInformation(major):
        return JsonResponse({
            'ans':'정보보호학과가 아님'
        })
    
    print(f"result type : {type(result)}\nresult : {result}")

    # db조회
    curTime = datetime.datetime.now()

    curDate = curTime.strftime("%Y-%m-%d")
    curst = curTime.strftime("%H:%M:%S")

    bookingList = Booking.objects.filter(
        studentid=studentid,
        date__gt=curDate
    ) | Booking.objects.filter(
        date=curDate,
        st__gte=curst
    )

    output = ""
    for idx, obj in enumerate(bookingList):
        output +=  f"{idx} {obj.date} {obj.st}~{obj.et} {obj.name}\n"
        print(f"{obj.date} {obj.st}~{obj.et} {obj.name}\n")

    print(output)
    # matchRule = re.compile("조회.*[: ](.*)")
    # accountInformation = matchRule.fullmatch(userData)
    # userData = accountInformation.group(1)
    # result = getUser(userData)
    # print(f"result : {result}")

    return JsonResponse({
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": output
                                }
                            }
                        ]
                    }
                })

@csrf_exempt
def getforbid(request):
    body = convertBytetoJson(request)
    print(body)
    return JsonResponse({
        'return': 0,
    })

def convertBytetoJson(request):
    decodedata = request.body.decode('utf8').replace("'", '"')
    data = json.loads(decodedata)
    return data

def printJson(data):
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
            if keyvalue[0] in requestlist:
                key = keyvalue[0]
                value = keyvalue[1]
                dictionary[key] = value
        result1, name, studentid = getUser(dictionary['신청자'])
        result2, content = getContent(dictionary['내용'])
        result3, nos = getNOS(body['action']['detailParams']['nos'])
        result4, date, st, et = getDateTime(body['action']['detailParams']['datetime'])
        if result1 and result2 and result3 and result4:
            booking = Booking(studentid=studentid, st=st, et=et, date=date, nos=nos, name=name, ct=content, roomid=roomid)
            booking.save()
            return True
        else:
            return False
    except IndexError:
        print('no \":\" or \"\\n\" letter')
        return False

def getUser(userdata):
    try:
        userdata = userdata.split('/')
        result = sj_auth.dosejong_api(userdata[0], userdata[1])
        if result['result']:
            print('name:', result['name'])
            print('id:', result['id'])
            return True, result['name'], result['id']
        else:
            print("there is no user in sejong univ.")
            return False, "", ""
    except IndexError:
        print("there is no \"/\" in userdata")
        return False, "", ""

def getContent(ct):
    print('ct:', ct)
    return True, ct

def getNOS(nos):
    try:
        nosdict = json.loads(nos['value'])
        print('nos:', nosdict['amount'])
        if nosdict['amount'] > max_nos:
            print("please input under", max_nos)
            return False, ""
        return True, nosdict['amount']
    except KeyError:
        print("please input right nos")
        return False, ""

def getDateTime(dt):
    try:
        dtdict = json.loads(dt['value'])
        fromdate = dtdict["from"]["date"]
        todate = dtdict["to"]["date"]
        fromtime = dtdict["from"]["time"]
        totime = dtdict["to"]["time"]
        if fromdate != todate:
            print("you can reserve only one day", fromdate, todate)
            return False, "", "", ""
        if fromtime >= totime:
            print("you have to input to time after from time")
            return False, "", "", ""
        today = datetime.datetime.now()
        reserve = datetime.datetime.strptime(fromdate+' '+fromtime, '%Y-%m-%d %H:%M:%S')
        if today >= reserve:
            print("you have to input reserve day or time after today or now")
            return False, "", "", ""
        if int(dtdict['from']['minute']) % 30 != 0 or int(dtdict['to']['minute']) % 30 != 0:
            print("you have to input reserve minute for 30")
            return False, "", "", ""
        st = dtdict["from"]["time"]
        et = dtdict["to"]["time"]
        date = fromdate
        print('date:', date)
        print('st:', st)
        print('et:', et)
        return True, date, st, et
    except KeyError:
        print("please input right DOW")
        return False, "", "", ""
    except (ValueError, TypeError):
        print("please input right Date data")
        return False, "", "", ""

#신청 불가능한 시간에 사용 금지(xlsx 파일 긁어오기)
def isForbidTime():
    return False

def isInformation(major):
    return major == "정보보호학과"