from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging

# Create your views here.
@csrf_exempt
def googledrive(request):
    #print(request.body)
    return ""

def printJson(data):
    jsonbody = json.dumps(data, indent=4, sort_keys=True)
    print(jsonbody)