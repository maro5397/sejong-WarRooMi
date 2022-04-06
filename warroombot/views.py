from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def create(request):
    return JsonResponse({
        'ans':'test create',
    })

def delete(request):
    return JsonResponse({
        'ans':'test delete',
    })

def retrieve(request):
    return JsonResponse({
        'ans':'test retrieve',
    })