from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def keyboard(request):
    return JsonResponse({
        'type':'buttons',
        'buttons':['예약','안내']
    })

@csrf_exempt
def answer(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    datacontent = received_json_data['content']

    if datacontent == '예약':
        reservation = "예약"
        return JsonResponse({
                'message': {
                    'text': reservation
                },
                'keyboard': {
                    'type':'buttons',
                    'buttons':['예약','안내']
                }
            })

    elif datacontent == '안내':
        guideline = "안내 사항"
        return JsonResponse({
                'message': {
                    'text': guideline
                },
                'keyboard': {
                    'type':'buttons',
                    'buttons':['예약','안내']
                }
            })
