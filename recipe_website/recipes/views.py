from django.shortcuts import render
from django.http import HttpResponse, FileResponse


def index(request):
    return HttpResponse(open('aloha_chicken.pdf', 'rb').read(), content_type='application/pdf')
