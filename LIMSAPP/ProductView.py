from django.shortcuts import render, redirect
from .models import MachineIds

def devices (request):
	all_devices = MachineIds.objects.all()
	cda_status = 'active'
	cobas_status = ''
	return render (request, 'product/devices.html', {'all_devices': all_devices, 'cda_status': cda_status})

def ResetBatchAmount(request, machine_identifier):
	status = ResetDeviceBatchAmount(machine_identifier)
	cda_status = ''
	cobas_status = ''
	all_devices = MachineIds.objects.all()
	if status == 'cda':
		cda_status = 'active'
	else:
		cobas_status = 'active'
	return render (request, 'product/devices.html', {'all_devices': all_devices, 'cda_status': cda_status, 'cobas_status': cobas_status})

def ResetDeviceBatchAmount (machine_identifier):
	try:
		reset_device = MachineIds.objects.get(machine_identifier=machine_identifier)
		reset_device.batch_amount = '0001'
		reset_device.save()
		return reset_device.machine_type
	except Exception as e:
		return e