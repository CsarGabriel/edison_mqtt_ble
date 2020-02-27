# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#base
import json, time

#Django
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

#Custom
from .models import Device, Log
from django.template.loader import render_to_string

# Create your views here.
def index(request):
    log_registers = Log.objects.order_by('timestamp')[:5]
    out = ", ".join( lg.event for lg in log_registers )
    template = render_to_string('blelog/index.html', {'log_events': log_registers})
    #context = RequestContext(request, {
    #  'log_events': log_registers
    #})
    return HttpResponse(template)


def devices(request):
    """
    log_registers = Log.objects.order_by('timestamp')[:5]
    out = ", ".join( lg.event for lg in log_registers )
    template = render_to_string('blelog/index.html', {'log_events': log_registers})
    """
    devices_lst = Device.objects.order_by('id')
    template = render_to_string('blelog/devices.html', {'devices_lst':devices_lst})
    #context = RequestContext(request, {
    #  'log_events': log_registers
    #})
    return HttpResponse(template)


def registers(request, dev_id):
    log_registers = Log.objects.filter(device__pk=dev_id).order_by('timestamp')[:100]
    dev = Device.objects.get(pk=dev_id)
    #out = ", ".join( lg.event for lg in log_registers )
    template = render_to_string('blelog/registers.html', {'log_events': log_registers, 'dev':dev})
    #context = RequestContext(request, {
    #  'log_events': log_registers
    #})
    return HttpResponse(template)


@csrf_exempt
def api_log_save(request):
    status = False
    new_id = 0
    response = {}

    if request.method=='POST':
            #print str(request)
            json_in_data=json.loads(request.body)

            #check device
            devs = Device.objects.filter(mac=json_in_data['mac_address'], name=json_in_data['ble_name'])
            num_devs = devs.count()
            if num_devs >= 1:
                found_dev = devs.first()
                
                #check if is active
                if found_dev.status:
                    #new Log Register
                    log = Log()
                    log.timestamp = int(time.time())
                    log.event = json_in_data['event']
                    log.device = devs.first()
                    log.save()
                    new_id = log.pk
                    status = True           

            # {'mac_address':json_in_data['mac_address'], 'ble_name':json_in_data['ble_name'] }
            # response = json_in_data

    data = {
        'api':'register in log',
        'insert_id':new_id,
        'status': status,
        'data': response,
    }
    #log_registers = Log.objects.filter(device__pk=dev_id)[:100]
    #dev = Device.objects.get(pk=dev_id)
    #out = ", ".join( lg.event for lg in log_registers )
    #template = render_to_string('blelog/registers.html', {'log_events': log_registers, 'dev':dev})
    #context = RequestContext(request, {
    #  'log_events': log_registers
    #})
    #return HttpResponse(template)
    return JsonResponse(data)

@csrf_exempt
def api_devices(request):
    devs = ()
    devices_lst = Device.objects.filter(status=True)
    cont = 0
    for dev in devices_lst:
        devs = devs + ({"ble_name": dev.name, "mac_address":dev.mac.upper()},)
        cont = cont + 1
    
    data = {
        "api":"read devices",
        "devices":devs,
        "status":True,
        "num_devices":cont,
    }

    return JsonResponse(data)

