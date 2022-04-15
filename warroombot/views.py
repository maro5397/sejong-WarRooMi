from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from warroombot.models import Booking
from googlewebhook.models import Forbid
from email.mime.text import MIMEText
from pathlib import Path
from . import sj_auth
import os.path
import json
import logging
import datetime
import smtplib


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

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json')

requestlist = ['내용', '신청자']
roomid = "센B208"
max_nos = 40
weeks = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']

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
    
    userData = body['userRequest']['utterance'].strip()

    try:
        paramJson = json.loads(body['action']['params']['sys_number_ordinal'])
        deleteIdx = paramJson['amount']
    except:
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "전송된 데이터에서 삭제하려는 번호를 확인하지 못했습니다.\n"
                                    "'삭제 ?번 id/pw'형태가 맞는지 확인해주세요."
                        }
                    }
                ]
            }
        })

    try:
        userData = userData.split(" ")[-1].split("/")
        userID = userData[0]
        userPW = userData[1]
    except:
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "전송된 데이터에서 id와 pw를 확인하지 못했습니다.\n"
                                    "'삭제 ?번 id/pw'형태가 맞는지 확인해주세요."
                        }
                    }
                ]
            }
        })

    # login
    result = sj_auth.dosejong_api(userID, userPW)
    result1 = result['result']

    if result1 != True:
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "로그인에 실패했습니다.\n"
                                    "id 또는 pw를 확인해주세요."
                        }
                    }
                ]
            }
        })

    name = result['name']
    studentid = result['id']
    major = result['major']

    if not isInformation(major):
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "정보보호학과생만 신청이 가능합니다."
                        }
                    }
                ]
            }
        })
    
    # Database
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
    bookingList = bookingList.order_by('date', 'st')

    try:
        obj = bookingList[deleteIdx-1]
        output = f"{name}님께서 예약하신\n"
        output += f"[{obj.date}일 {obj.st}~{obj.et}]\n일정을 삭제했습니다."
        obj.delete()
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
    except:
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "삭제과정에서 오류가 발생했습니다.\n"
                                    "다시 시도해주세요"
                        }
                    }
                ]
            }
        })

@csrf_exempt
def retrieve(request):
    body = convertBytetoJson(request)

    userData = body['userRequest']['utterance'].strip()
    
    try:
        userData = userData.split(" ")[-1].split("/")
        userID = userData[0]
        userPW = userData[1]
    except:
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "전송된 데이터에서 id와 pw를 확인하지 못했습니다.\n"
                                    "'조회 id/pw'형태가 맞는지 확인해주세요."
                        }
                    }
                ]
            }
        })
        
    # login
    result = sj_auth.dosejong_api(userID, userPW)
    result1 = result['result']

    if result1 != True:
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "로그인에 실패했습니다.\n"
                                    "id 또는 pw를 확인해주세요."
                        }
                    }
                ]
            }
        })

    name = result['name']
    studentid = result['id']
    major = result['major']

    if not isInformation(major):
        return JsonResponse({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "정보보호학과생만 신청이 가능합니다."
                        }
                    }
                ]
            }
        })
    
    # Database
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
    bookingList = bookingList.order_by('date', 'st')

    output = f"현재 {name}님의 예약 상황입니다.\n"
    for idx, obj in enumerate(bookingList, start=1):
        output +=  f"[{idx}번] {obj.date} {obj.st}~{obj.et}\n"

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
        result2, ct = getContent(dictionary['내용'])
        result3, nos = getNOS(body['action']['detailParams']['nos'])
        result4, date, st, et = getDateTime(body['action']['detailParams']['datetime'])
        if result1 and result2 and result3 and result4:
            if not sendEmail(st, et, date, nos, ct, name, studentid, roomid):
                return False
            booking = Booking(studentid=studentid, st=st, et=et, date=date, nos=nos, name=name, ct=ct, roomid=roomid)
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
            if isInformation(result['major']):
                print('name:', result['name'])
                print('id:', result['id'])
                return True, result['name'], result['id']
            else:
                print("not infosec student")
                return False, "", ""
        else:
            print("there is no user in sejong univ.")
            return False, "", ""
    except (IndexError, KeyError):
        print("there is no \"/\" in userdata or no key data in sejong api result")
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
        if isForbidTime(st, et, date):
            print("input forbid time or already reserved")
            return False, "", "", ""
        print('date:', date)
        print('st:', st)
        print('et:', et)
        return True, date, st, et
    except KeyError as e:
        print("please input right DOW", e)
        return False, "", "", ""
    except (ValueError, TypeError) as e:
        print("please input right Date data", e)
        return False, "", "", ""

def isForbidTime(st, et, date):
    sttime = datetime.datetime.strptime(st, '%H:%M:%S').time()
    ettime = datetime.datetime.strptime(et, '%H:%M:%S').time()
    datetype = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    bookingdate = Booking.objects.filter(date__exact = datetype)
    dow = changeDatetoDOW(date)
    forbiddate = Forbid.objects.filter(dow__exact = dow)
    return isInvaildRange(sttime, ettime, bookingdate) or isInvaildRange(sttime, ettime, forbiddate)

def isInvaildRange(sttime, ettime, dates):
    if dates.exists():
        forbidsttime = dates.filter(st__range=[sttime, ettime])
        forbidettime = dates.filter(et__range=[sttime, ettime])
        if forbidsttime.exists() or forbidettime.exists():
            return True
        else:
            for date in dates:
                if date.st < sttime and ettime < date.et:
                    return True
    return False

def changeDatetoDOW(date):
    datetype = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    dow = datetype.weekday()
    return weeks[dow]

def isInformation(major):
    return major == "정보보호학과"

def get_secret(setting):
    with open(secret_file, 'r') as f:
        secrets = json.loads(f.read())
        try:
            return secrets[setting]
        except KeyError:
            error_msg = "Set the {} environment variable".format(setting)
            raise ImproperlyConfigured(error_msg)

def sendEmail(st, et, date, nos, ct, name, studentid, roomid):
    try:
        emailid = get_secret("EMAILID")
        emailpw = get_secret("EMAILPW")
        manager = get_secret("MANAGER")
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(emailid, emailpw)
        msg_subject = "[세종대학교 사이버워룸] 사용 내역 관련"
        msg_content = f"""안녕하십니까 워루미입니다.
예약 신청 내역 정보를 송신합니다.

위치: {roomid}
시간: {date} {st} ~ {et}
인원: {nos}명
내용: {ct}
신청자: {name}({studentid})

메일 확인해주셔서 감사합니다."""
        msg = MIMEText(msg_content.encode('utf-8'), _charset='utf-8')   
        msg['Subject'] = msg_subject
        s.sendmail(emailid, [manager], msg.as_string())
        s.quit()
        return True
    except:
        s.quit()
        print("there is something wrong in email send func")
        return False