from django.shortcuts import render, redirect
from pathlib import Path
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import Patient, Batch, MachineIds, EmailAccounts
from .forms import PatientForm, SignUpForm, EditProfileForm
from django.contrib import messages
import json
import csv
import logging
import pdfrw
import pandas
import mimetypes
import datetime
from datetime import date
from django.http import FileResponse, Http404, HttpResponse
import smtplib
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'
cobas_list_models = ['E411.1', 'E411.2']
cda_list_models= ['CDA4.1', 'CDA3.2', 'CDA3.1', 'CDA2.1', 'CDA1.1']

# Create your views here.

def result_entry(request):
	today = date.today()
	date_today = today.strftime("%b-%d-%Y")
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/CSVFiles/" + date_today + "/"

	if request.method =='POST' and not request.FILES:
		patient_score_update(request.POST)
		return redirect('result_entry')

	elif request.method == 'POST' and request.FILES['csv_file_values']:
		DirectoryExists (path_to_dir)
		try:
			#print("File Detected")
			#print(request.FILES['csv_file_values'])
			file = request.FILES['csv_file_values']
			#file_name = default_storage.save(file.name, file)
			file_name = default_storage.save(path_to_dir + file.name, file)
			#print('File saved successfully')
			extracted_patient_values = readCSVFile(path_to_dir + file.name)
			updatePatientDatabase(extracted_patient_values)
			print(emailListCobas(extracted_patient_values))
			EmailNotification(emailListCobas(extracted_patient_values), 'dennis_lin@anpacbio.com')
			return redirect('result_entry')
		except Exception as e:
			#print('From Result_entry ******')
			#print(e)
			return redirect('result_entry')
	else:
		all_patients = Patient.objects.all
		return render(request, 'assay/assay_result_entry.html', {"all_patients": all_patients})


#################### Solely Functional that return no HTTPResponses Below ####################
###########																        ##############
###########	    	    	Only Pythony Things below						    ##############
###########																        ##############
###########																        ##############

def patient_score_update(request):
	data = request
	filtered_data = {k: v for k, v in data.items() if v}
	result_entered_patients = []
	for stuff in filtered_data:
		#cda score update
		if stuff[0:4] == 'cda_':
			patient = Patient.objects.get(anpac_id=stuff[4:])
			patient.cda_score = data.getlist(stuff)[0]
			patient.cda_status = 'ReportReady'
			patient.save()
			result_entered_patients.append(stuff[4:])
		#psa update
		elif stuff[0:4] == 'psa_':
			patient_obj = Patient.objects.get(anpac_id=stuff[4:])
			patient_obj.psa_score = data.getlist(stuff)[0]
			patient_obj.psa_status = 'ReportReady'
			test_to_check = []
			if patient_obj.psa_choice:
				test_to_check.append('psa')
			if patient_obj.afp_choice:
				test_to_check.append('afp')
			if patient_obj.ca125_choice:
				test_to_check.append('ca125')
			if patient_obj.ca19_9_choice:
				test_to_check.append('ca199')
			if patient_obj.cea_choice:
				test_to_check.append('cea')
			test_length = len(test_to_check)
			for test in test_to_check:
				if test == 'psa':
					if patient_obj.psa_status =='ReportReady':
						test_length -= 1
				elif test =='afp':
					if patient_obj.afp_status =='ReportReady':
						test_length -= 1
				elif test =='ca125':
					if patient_obj.ca125_status =='ReportReady':
						test_length -= 1
				elif test =='ca199':
					if patient_obj.ca19_9_status =='ReportReady':
						test_length -= 1
				elif test =='cea':
					if patient_obj.cea_status =='ReportReady':
						test_length -= 1
			if test_length == 0:
				patient_obj.cobas_status = 'ReportReady'
				result_entered_patients.append(stuff[4:])
			patient_obj.save()
		#afp update
		elif stuff[0:4] == 'afp_':
			patient_obj = Patient.objects.get(anpac_id=stuff[4:])
			patient_obj.afp_score = data.getlist(stuff)[0]
			patient_obj.afp_status = 'ReportReady'
			test_to_check = []
			if patient_obj.psa_choice:
				test_to_check.append('psa')
			if patient_obj.afp_choice:
				test_to_check.append('afp')
			if patient_obj.ca125_choice:
				test_to_check.append('ca125')
			if patient_obj.ca19_9_choice:
				test_to_check.append('ca199')
			if patient_obj.cea_choice:
				test_to_check.append('cea')
			test_length = len(test_to_check)
			for test in test_to_check:
				if test == 'psa':
					if patient_obj.psa_status =='ReportReady':
						test_length -= 1
				elif test =='afp':
					if patient_obj.afp_status =='ReportReady':
						test_length -= 1
				elif test =='ca125':
					if patient_obj.ca125_status =='ReportReady':
						test_length -= 1
				elif test =='ca199':
					if patient_obj.ca19_9_status =='ReportReady':
						test_length -= 1
				elif test =='cea':
					if patient_obj.cea_status =='ReportReady':
						test_length -= 1
			if test_length == 0:
				patient_obj.cobas_status = 'ReportReady'
				result_entered_patients.append(stuff[4:])
			patient_obj.save()
		#cea update
		elif stuff[0:4] == 'cea_':
			patient_obj = Patient.objects.get(anpac_id=stuff[4:])
			patient_obj.cea_score = data.getlist(stuff)[0]
			patient_obj.cea_status = 'ReportReady'
			test_to_check = []
			if patient_obj.psa_choice:
				test_to_check.append('psa')
			if patient_obj.afp_choice:
				test_to_check.append('afp')
			if patient_obj.ca125_choice:
				test_to_check.append('ca125')
			if patient_obj.ca19_9_choice:
				test_to_check.append('ca199')
			if patient_obj.cea_choice:
				test_to_check.append('cea')
			test_length = len(test_to_check)
			for test in test_to_check:
				if test == 'psa':
					if patient_obj.psa_status =='ReportReady':
						test_length -= 1
						#print('test_length: ')
						#print(test_length)
				elif test =='afp':
					if patient_obj.afp_status =='ReportReady':
						test_length -= 1
						#print('test_length: ')
						#print(test_length)
				elif test =='ca125':
					if patient_obj.ca125_status =='ReportReady':
						test_length -= 1
						#print('test_length: ')
						#print(test_length)
				elif test =='ca199':
					if patient_obj.ca19_9_status =='ReportReady':
						test_length -= 1
						#print('test_length: ')
						#print(test_length)
				elif test =='cea':
					if patient_obj.cea_status =='ReportReady':
						test_length -= 1
						#print('test_length: ')
						#print(test_length)
			if test_length == 0:
				patient_obj.cobas_status = 'ReportReady'
				result_entered_patients.append(stuff[4:])
				#print(patient_obj.anpac_id + 'is ReportReady')
			patient_obj.save()
			
		#ca19-9 update
		elif stuff[0:4] == 'ca19':
			patient_obj = Patient.objects.get(anpac_id=stuff[4:])
			patient_obj.ca19_9_score = data.getlist(stuff)[0]
			patient_obj.ca19_9_status = 'ReportReady'
			test_to_check = []
			if patient_obj.psa_choice:
				test_to_check.append('psa')
			if patient_obj.afp_choice:
				test_to_check.append('afp')
			if patient_obj.ca125_choice:
				test_to_check.append('ca125')
			if patient_obj.ca19_9_choice:
				test_to_check.append('ca199')
			if patient_obj.cea_choice:
				test_to_check.append('cea')
			test_length = len(test_to_check)
			for test in test_to_check:
				if test == 'psa':
					if patient_obj.psa_status =='ReportReady':
						test_length -= 1
				elif test =='afp':
					if patient_obj.afp_status =='ReportReady':
						test_length -= 1
				elif test =='ca125':
					if patient_obj.ca125_status =='ReportReady':
						test_length -= 1
				elif test =='ca199':
					if patient_obj.ca19_9_status =='ReportReady':
						test_length -= 1
				elif test =='cea':
					if patient_obj.cea_status =='ReportReady':
						test_length -= 1
			if test_length == 0:
				patient_obj.cobas_status = 'ReportReady'
				result_entered_patients.append(stuff[4:])
			patient_obj.save()
			
		#ca125 update
		elif stuff[0:4] == 'ca12':
			patient_obj = Patient.objects.get(anpac_id=stuff[4:])
			patient_obj.ca125_score = data.getlist(stuff)[0]
			patient_obj.ca125_status = 'ReportReady'
			test_to_check = []
			if patient_obj.psa_choice:
				test_to_check.append('psa')
			if patient_obj.afp_choice:
				test_to_check.append('afp')
			if patient_obj.ca125_choice:
				test_to_check.append('ca125')
			if patient_obj.ca19_9_choice:
				test_to_check.append('ca199')
			if patient_obj.cea_choice:
				test_to_check.append('cea')
			test_length = len(test_to_check)
			for test in test_to_check:
				if test == 'psa':
					if patient_obj.psa_status =='ReportReady':
						test_length -= 1
				elif test =='afp':
					if patient_obj.afp_status =='ReportReady':
						test_length -= 1
				elif test =='ca125':
					if patient_obj.ca125_status =='ReportReady':
						test_length -= 1
				elif test =='ca199':
					if patient_obj.ca19_9_status =='ReportReady':
						test_length -= 1
				elif test =='cea':
					if patient_obj.cea_status =='ReportReady':
						test_length -= 1
			if test_length == 0:
				patient_obj.cobas_status = 'ReportReady'
				result_entered_patients.append(stuff[4:])
			patient_obj.save()
	EmailNotification(result_entered_patients, 'dennis_lin@anpacbio.com')

def DirectoryExists (path_to_dir):
	Path(path_to_dir).mkdir(parents=True, exist_ok=True)

def readCSVFile (csv_file):
	# open the file in universal line ending mode 
	with open(csv_file, 'rU') as infile:
		# read the file as a dictionary for each row ({header : value})
		reader = csv.DictReader(infile)
		data = {}
		patient_ids = ()
		for row in reader:
			for header, value in row.items():
				try:
					data[header].append(value)
				except KeyError:
					data[header] = [value]
	#
	with open(csv_file, 'r') as f:
		str_list = [row[6] for row in csv.reader(f)]
		patient_ids = str_list[2:]

	
	
	#print('data:' + str(data))

	Assigned_Patient_Values = AssignPatientValues(patient_ids, data)
	return Assigned_Patient_Values

def AssignPatientValues (patient_ids, raw_data):
	# extract the variables you want
	CA19_9_Values = raw_data['351'] #CA19-9
	CA19_9_Values.pop(0)
	CA125_Values = raw_data['341'] #CA125
	CA125_Values.pop(0)
	CEA_Values = raw_data['301'] #CEA
	CEA_Values.pop(0)
	AFP_Values = raw_data['311'] ##AFP
	AFP_Values.pop(0)
	PSA_Values = raw_data['2120'] #PSA NEW
	PSA_Values.pop(0)
	patient_assigned_values = {}
	#[psa_value, afp_value, cea_value, ca125_value, ca19_9_value]
	for index, elem in enumerate (patient_ids):
		#print(elem + " | anpac id: " + patient_ids[index] + " | cea: " + CEA_Values[index] + " | ca19-9: " + CA19_9_Values[index] + " | ca125: " 
		#	+ CA125_Values[index] + " | afp: " + AFP_Values[index] + " | psa: " + PSA_Values[index])
		temp_value = [PSA_Values[index], AFP_Values[index], CEA_Values[index], CA125_Values[index], CA19_9_Values[index]]
		#print(temp_value)
		patient_assigned_values[elem] = temp_value
	return patient_assigned_values

def updatePatientDatabase (extracted_patient_values):
	for element in extracted_patient_values:
		try:
			Cobas_update_patient = Patient.objects.get(anpac_id=element)
			temp_list = extracted_patient_values[element]
			#print(temp_list)
			#print('Patient: ' + element)
			Cobas_update_patient.psa_score = temp_list[0]
			#print('Cobas_update_patient.psa_score: ' + Cobas_update_patient.psa_score)
			if Cobas_update_patient.psa_choice:
				#print('PSA for Patient: ' + element + ' Complete')
				Cobas_update_patient.psa_status = 'ReportReady'
			

			Cobas_update_patient.afp_score = temp_list[1]
			#print('Cobas_update_patient.afp_score: ' + Cobas_update_patient.afp_score)
			if Cobas_update_patient.afp_choice:
				#print('AFP for Patient: ' + element + ' Complete')
				Cobas_update_patient.afp_status = 'ReportReady'
			

			Cobas_update_patient.cea_score = temp_list[2]
			#print('Cobas_update_patient.cea_score: ' + Cobas_update_patient.cea_score)
			if Cobas_update_patient.cea_choice:
				#print('CEA for patient: ' + element + ' Complete')
				Cobas_update_patient.cea_status = 'ReportReady'
			

			Cobas_update_patient.ca125_score = temp_list[3]
			#print('Cobas_update_patient.ca125_score: ' + Cobas_update_patient.ca125_score)
			if Cobas_update_patient.ca125_choice:
				#print('CA125 for Patient: ' + element + ' Complete')
				Cobas_update_patient.ca125_status = 'ReportReady'
			

			Cobas_update_patient.ca19_9_score = temp_list[4]
			#print('Cobas_update_patient.ca19_9_score: ' + Cobas_update_patient.ca19_9_score)
			if Cobas_update_patient.ca19_9_choice:
				#print('CA19-9 for Patient: ' + element + ' complete')
				Cobas_update_patient.ca19_9_status = 'ReportReady'
			test_to_check = []
			if Cobas_update_patient.psa_choice:
				test_to_check.append('psa')
			if Cobas_update_patient.afp_choice:
				test_to_check.append('afp')
			if Cobas_update_patient.ca125_choice:
				test_to_check.append('ca125')
			if Cobas_update_patient.ca19_9_choice:
				test_to_check.append('ca199')
			if Cobas_update_patient.cea_choice:
				test_to_check.append('cea')
			#print('test_to_check: ' + str(test_to_check))
			test_length = len(test_to_check)
			for test in test_to_check:
				if test == 'psa':
					if Cobas_update_patient.psa_status =='ReportReady':
						test_length -= 1
				elif test =='afp':
					if Cobas_update_patient.afp_status =='ReportReady':
						test_length -= 1
				elif test =='ca125':
					if Cobas_update_patient.ca125_status =='ReportReady':
						test_length -= 1
				elif test =='ca199':
					if Cobas_update_patient.ca19_9_status =='ReportReady':
						test_length -= 1
				elif test =='cea':
					if Cobas_update_patient.cea_status =='ReportReady':
						test_length -= 1
			if test_length == 0:
				Cobas_update_patient.cobas_status = 'ReportReady'
			Cobas_update_patient.save()
			#If score has been entered, change that status to ReportReady
		except Exception as e:
  			print(e)

#Email Notification

def emailListCobas (extracted_patient_values):
	patient_list = []
	for element in extracted_patient_values:
		try:
			Cobas_update_patient = Patient.objects.get(anpac_id=element)
			if Cobas_update_patient.cobas_status == 'ReportReady':
				patient_list.append(element)
		except Exception as e:
			print(e)
	return patient_list

def EmailNotification (anpac_id_list, reciever_email):
	email_account = EmailAccounts.objects.get(account_name= 'EmailNotification')
	email = email_account.email_address
	password = email_account.email_password
	smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
	smtp_object.ehlo()
	smtp_object.starttls()
	smtp_object.login(email,password)
	from_address = email
	#later to be assigned
	to_address = reciever_email
	subject = 'Reports Awaiting Approval [From AnPacLIMS]'
	# input message here for batch ID and Anpac Reports
	message = EmailNotificationBody(anpac_id_list)
	msg = "Subject: " + subject + '\n' + message
	smtp_object.sendmail(from_address,to_address,msg)
	smtp_object.quit()

def EmailNotificationBody (anpac_id_list):
	try:
		body = 'Reports have been completed and need approval. \n'
	except Exception as e:
		print('EmailNotificationBody: ' + e)
	return body

def ArchiveRequsition (anpac_id, cobasorcda):
	archive_patient = Patient.objects.get(anpac_id=anpac_id)
	#check if CDA has been selected
	if cobasorcda == 'cobas':
		if archive_patient.cda_status == 'ResultsApproved' or archive_patient.cda_status == 'Not-Selected':
			archive_patient.cda_status = 'Archived'
			archive_patient.save()
	if cobasorcda == 'cda':
		if archive_patient.cobas_status =='ResultsApproved' or archive_patient.cobas_status == 'Not-Selected':
			archive_patient.cobas_status = 'Archived'
			archive_patient.save()











