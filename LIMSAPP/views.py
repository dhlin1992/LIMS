from django.shortcuts import render, redirect
from pathlib import Path
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import Patient, Batch, MachineIds
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
def home(request):
	return render(request, 'home.html', {})
	#return render (request, 'req_patient_info.html', {})

def import_requisitions(request):
	today = date.today()
	date_today = today.strftime("%b-%d-%Y")
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/submittedReqExcel/" + date_today + "/"
	DirectoryExists (path_to_dir)
	try:
		if request.method == 'POST' and request.FILES:
			file = request.FILES['import_req_excel']
			file_name = default_storage.save(path_to_dir + file.name, file) #saves excel file in directory submittedReqExcel
			ImportRequisitionsExcel(path_to_dir + file.name, request)
			messages.success(request, ('Import Succesful! :]'))
			return redirect('search_req')
		else:
			return render(request, 'requisitions/import_requisitions.html',{})
	except Exception as e:
		messages.success(request, ('Import exception has occured: ' + str(e) + ' Please contact Admin.'))
		print(e)
		return render(request, 'requisitions/import_requisitions.html',{})

def download_req_excel (request):
	fl_path = '/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/RequisitionExcelTemplate'
	filename = 'Requisition_Sheet_Template.xlsx'
	fl = open(fl_path + '/' + filename, "rb")
	
	mime_type, _ = mimetypes.guess_type(fl_path)
	response = HttpResponse(fl, content_type= mime_type)
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response


def requisition_form(request):
	if request.method == 'POST':
		form = PatientForm(request.POST)
		if form.is_valid():
			if Patient.objects.filter(anpac_id= request.POST['anpac_id']).exists():
				messages.success(request, ('Requsition already exists :['))
				return redirect ('search_req')
			else:
				form.save()
				messages.success(request, ('Requsition Submitted Succesfully :]'))
				return redirect ('search_req')
		else:
			messages.success(request, ('Requsition exception has occured: ' + form.errors.as_data() + ' Please contact Admin.'))
			#print(form.errors.as_data()) # here you print errors to terminal
			return render(request, 'home.html', {})
	else:

		return render(request,'requisition.html',{})

def search_req(request):
	if request.method == 'POST':
		query = request.POST
		if query:
			patient_info = Patient.objects.filter(anpac_id=query['anpac_id'])
			if patient_info.exists():
				choices = IndividualTests(patient_info)
				return render (request, 'QC_edit_req_form.html', {"patient_info": patient_info, "choices": choices})
			else:
				search_param = query['anpac_id']
				messages.warning(request, (search_param + ' not found! Please try again.'))
				return redirect('search_req')
	else:
		all_items = Patient.objects.all
		return render(request, 'search_req.html', {"all_items":all_items})

def open_report(request, anpac_id):
	if request.method == 'POST':
		#create a form instance from POST data
		new_form = PatientForm(request.POST)
		if new_form.is_valid():
			old_form = Patient.objects.get(anpac_id=anpac_id)
			final_form = PatientForm(request.POST, instance=old_form)
			old_form.delete()
			final_form.save()
			update_test_status_fromQC(anpac_id)
			all_items = Patient.objects.all
			return render(request, 'search_req.html', {"all_items":all_items})
	else:
		#print(anpac_id)
		patient_info = Patient.objects.filter(anpac_id=anpac_id)
		choices = IndividualTests(patient_info)
		return render (request, 'QC_edit_req_form.html', {"patient_info":patient_info, "choices": choices})

def assay(request):
	cda_tab = ''
	cobas_tab = ''
	if request.method == 'POST':
		post_data = request.POST
		tab = update_test_status_batch(post_data)
		#test_status_update(post_data)
		all_patients = Patient.objects.all()
		all_batch = Batch.objects.all()
		cda_tab = ''
		cobas_tab = ''
		if tab == 'cobas':
			cobas_tab = 'active'
			cda_tab = ''
		else:
			cda_tab = 'active'
		return render(request, 'assay/assay.html', {"all_patients": all_patients, "all_batch": all_batch, "cda_tab": cda_tab, 'cobas_tab': cobas_tab})
	else:	
		all_patients = Patient.objects.all()
		all_batch = Batch.objects.all()
		cda_tab = 'active'
		return render(request, 'assay/assay.html', {"all_patients": all_patients, "all_batch": all_batch, "cda_tab": cda_tab, 'cobas_tab': cobas_tab})

def success(request):
	return render(request, 'successful.html', {})

def html_testing(request):
	form = Patient.objects.get(anpac_id="tester")
	choices = IndividualTests(form)
	return render(request, 'html_testing.html', {"patient_info": form, "choices": choices})

def user_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ('You have been Logged In!'))
			return redirect('home')
		else:
			messages.success(request, ('Error Logging In - Please Try Again...'))
			return redirect('login')
	else:
		return render(request, 'authenticate/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ('You have been logged out...'))
	return redirect ('home')


def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ('Register Successful...'))
			return redirect('home')

	else:
		form = SignUpForm()
	context = {'form': form}
	return render(request, 'authenticate/register.html', context)

def edit_profile(request):
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, ('Edit Successful...'))
			return redirect('home')

	else:
		form = EditProfileForm(instance=request.user)
	context = {'form': form}
	return render(request, 'authenticate/edit_profile.html', context)

def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(data=request.POST, user=request.user)
		if form.is_valid():
			form.save()
			#Save session so users don't have to re log in but might not want to put it in so users can remember their password by relogging in
			#update_session_auth_hash(request, form.user)
			messages.success(request, ('Password Change Successful...'))
			return redirect('home')

	else:
		form = PasswordChangeForm(user=request.user)
	context = {'form': form}
	return render(request, 'authenticate/change_password.html', context)
	

def cda_assay_status_update(request, status, anpac_id):
	item = Patient.objects.get(anpac_id = anpac_id)
	item.cda_status = status
	item.save()
	return redirect('assay')

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

def create_report(request):
	all_patients = Patient.objects.all()
	return render(request, 'report/create_report.html', {'all_patients': all_patients})

def patient_cobas_results(request, anpac_id):
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/" #save path
	PDFCreateReport(anpac_id, '_cobas', FillDataCobasReport(anpac_id, request.user))
	try:
		return FileResponse(open(path_to_dir + anpac_id + '_cobas' +'.PDF', 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()

def patient_cda_results(request,anpac_id):
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/"
	PDFCreateReport(anpac_id, '_cda', FillDataCDAReport(anpac_id, request.user))
	try:
		return FileResponse(open(path_to_dir + anpac_id + '_cda' +'.PDF', 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()
	return

def patient_view_results(request, anpac_id):
	if request.method == 'POST':
		#current_user = request.user.first_name + ' ' + request.user.last_name + ': '
		data = request.POST
		result_patient = Patient.objects.get(anpac_id=anpac_id)
		if result_patient.cda_status == 'ReportReady':
			if data['cda_test_notes'] != 'None':
				result_patient.cda_test_notes = data['cda_test_notes']
			if data['cda_internal_notes'] != 'None':
				result_patient.cda_internal_notes = data['cda_internal_notes']
		if result_patient.cobas_status == 'ReportReady':
			if data['cobas_test_notes'] != 'None':
				result_patient.cobas_test_notes = data['cobas_test_notes']
			if data['cobas_internal_notes'] != 'None':
				result_patient.cobas_internal_notes = data['cobas_internal_notes']
		#change CDA score if overwrite detected
		if result_patient.cda_status == 'ReportReady' and not result_patient.cda_score == data['cda_score']:
			result_patient.cda_score = data['cda_score']
		if result_patient.cobas_status == 'ReportReady':
			if result_patient.psa_choice == True and not result_patient.psa_score == data['psa_score']:
				result_patient.psa_score = data['psa_score']
			if result_patient.afp_choice == True and not result_patient.afp_score == data['afp_score']:
				result_patient.afp_score = data['afp_score']
			if result_patient.ca125_choice == True and not result_patient.ca125_score == data['ca125_score']:
				result_patient.ca125_score = data['ca125_score']
			if result_patient.ca19_9_choice == True and not result_patient.ca19_9_score == data['ca19_9_score']:
				result_patient.ca19_9_score = data['ca19_9_score']
			if result_patient.cea_choice == True and not result_patient.cea_score == data['cea_score']:
				result_patient.cea_score = data['cea_score']

		result_patient.save()
		return redirect('create_report')

	else:
		result_patient = Patient.objects.filter(anpac_id=anpac_id)
		return render(request, 'report/patient_view_results.html',{'result_patient':result_patient})

def op_machine_assignment (request):
	if request.method == 'POST':
		data = request.POST
		try:
			#if Batch.objects.filter(batch_id=data['batch_id_cda']).exists() or Batch.objects.filter(batch_id=data['batch_id_cobas']).exists():
			#	messages.success(request, ('Batch ID already entered, please enter a new Batch ID'))
			#else:

			#Need to check that user made a selection for Machine
			machine_model_cda = request.POST.get('cda_machine_num', '')
			machine_model_cobas = request.POST.get('cobas_machine_num', '')
			cda_requsitions = extractRequisitionAnpacIDCDA(data)
			cobas_requsitions = extractRequisitionAnpacIDCobas(data)

			# Cobas 28 max samples

			# CDA 40 not including controls
			if cda_requsitions:
				if machine_model_cda:
					#print(BatchIDCreate(CobasOrCDA(machine_model_cda, cobas_list_models, cda_list_models), MachineNumberCDA(machine_model_cda), BatchYear(), getbatchnum(machine_model_cda)))
					batch_name = BatchIDCreate(CobasOrCDA(machine_model_cda, cobas_list_models, cda_list_models), MachineNumberCDA(machine_model_cda), BatchYear(), getbatchnum(machine_model_cda))
					UpdateRequsitionBatchOPMachineModelCDA(cda_requsitions, batch_name, machine_model_cda, data['operator_name'])
					messages.success(request, ('Batch ' + batch_name + ' created successfully.'))
					return redirect('op_machine_assignment')
				else:
					messages.success(request, ('Please select a CDA Machine below.'))
					return redirect('op_machine_assignment')
			if cobas_requsitions:
				if machine_model_cobas:
					batch_name = BatchIDCreate(CobasOrCDA(machine_model_cobas, cobas_list_models, cda_list_models), MachineNumberCobas(machine_model_cobas), BatchYear(), getbatchnum(machine_model_cobas))
					UpdateRequsitionBatchOPMachineModelCobas(cobas_requsitions, batch_name, machine_model_cobas, data['operator_name'])
					messages.success(request, ('Batch ' + batch_name + ' created successfully.'))
					return redirect('op_machine_assignment')
				else:
					messages.success(request, ('Please select a Cobas Machine below.'))
					return redirect('op_machine_assignment')
		except Exception as e:
			print(e)
		return redirect ('op_machine_assignment')
	else:
		all_patients = Patient.objects.all()
		return render(request, 'assay/op_machine_assignment.html', {'all_patients':all_patients})

def approval_sign_off(request):
	cda_tab = 'active'
	all_patients = Patient.objects.all()
	return render(request, 'report/approval_sign_off.html', {'all_patients':all_patients, "cda_tab": cda_tab})

def approve_report_cda(request, anpac_id):
	approved_patient = Patient.objects.get(anpac_id=anpac_id)
	approved_patient.cda_status = 'ResultsApproved'
	approved_patient.save()
	all_patients = Patient.objects.all()
	cda_tab = 'active'
	cobas_tab = ''
	#ArchiveRequsition(anpac_id, 'cda')
	return render(request, 'report/approval_sign_off.html', {'all_patients':all_patients, "cda_tab": cda_tab, 'cobas_tab': cobas_tab})

def approve_report_cobas(request, anpac_id):
	approved_patient = Patient.objects.get(anpac_id=anpac_id)
	approved_patient.cobas_status = 'ResultsApproved'
	approved_patient.save()
	all_patients = Patient.objects.all()
	cobas_tab = 'active'
	cda_tab = ''
	#ArchiveRequsition(anpac_id, 'cobas')
	return render(request, 'report/approval_sign_off.html', {'all_patients':all_patients, "cda_tab": cda_tab, 'cobas_tab': cobas_tab})
	#return redirect ('approval_sign_off')

def final_reports(request):
	all_batch = Batch.objects.all()
	all_patients = Patient.objects.all()
	return render(request,'report/final_reports.html', {'all_batch': all_batch, 'all_patients': all_patients})

def approved_cda_results(request, anpac_id):
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/approved/"
	PDFCreateFinalReport(anpac_id, '_cda_Approved', FillDataCDAReport(anpac_id, request.user))
	try:
		return FileResponse(open(path_to_dir + anpac_id + '_cda_Approved' +'.PDF', 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()
	return

def final_cobas_results(request, anpac_id):
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/approved/"
	PDFCreateFinalReport(anpac_id, '_cobas_Approved', FillDataCobasReport(anpac_id, request.user))
	try:
		return FileResponse(open(path_to_dir + anpac_id + '_cobas_Approved' +'.PDF', 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()
	return

def email_final_report(request, anpac_id):

	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/approved/"
	if request.method == 'POST':
		data = request.POST

		#Check to make sure final reports directory exists
		DirectoryExists(path_to_dir)

		#Check to make sure PDF report of approved results exists, if not create and fill under AnpacID/approved directory
		cda_report_select = data.get('cda_report', '')
		cobas_report_select = data.get('cobas_report', '')
		destination_email = ''
		 
		body = data.get('email_body', 'Sent by AnPac Bio')
		# put your email here
		sender = 'dennis_lin@anpacbio.com'
		# get the password in the gmail (manage your google account, click on the avatar on the right)
		# then go to security (right) and app password (center)
		# insert the password and then choose mail and this computer and then generate
		# copy the password generated here
		password = 'dwcepnbrmrnnfckg'
		# put the email of the receiver here
		physician_destination_selected = data.get('email_physician', '')
		if physician_destination_selected == 'True':
			patient_info = Patient.objects.get(anpac_id=anpac_id)
			destination_email = patient_info.or_physician_email
		else:
			destination_email = data.get('receiever_email_address', sender)
		receiver = destination_email
		 
		#Setup the MIME
		message = MIMEMultipart()
		message['From'] = sender
		message['To'] = receiver
		message['Subject'] = data.get('email_topic', anpac_id + 'Report')
		 
		message.attach(MIMEText(body, 'plain'))

		if cda_report_select == 'True':
			if FinalReportExists(path_to_dir, '_cda_Approved', anpac_id):
				print('CDA Report already created')
			else:
				PDFCreateFinalReport(anpac_id, '_cda_Approved', FillDataCDAReport(anpac_id, request.user))
				#print('CDA Report successfully created')
			pdfname = path_to_dir + anpac_id + '_cda_Approved.pdf'
			
			# open the file in bynary
			binary_pdf = open(pdfname, 'rb')
			 
			payload = MIMEBase('application', 'octate-stream', Name=(anpac_id + '_cda_report.pdf'))
			# payload = MIMEBase('application', 'pdf', Name=pdfname)
			payload.set_payload((binary_pdf).read())
			 
			# enconding the binary into base64
			encoders.encode_base64(payload)
			 
			# add header with pdf name
			payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
			message.attach(payload)
		if cobas_report_select == 'True':
			if FinalReportExists(path_to_dir, '_cobas_Approved', anpac_id):
				print('Cobas Report already created')
			else:
				PDFCreateFinalReport(anpac_id, '_cobas_Approved', FillDataCobasReport(anpac_id, request.user))
				#print('Cobas Report successfully created')
			pdfname = path_to_dir + anpac_id + '_cobas_Approved.pdf'
			 
			# open the file in bynary
			binary_pdf = open(pdfname, 'rb')
			 
			payload = MIMEBase('application', 'octate-stream', Name=(anpac_id + '_cobas_report.pdf'))
			# payload = MIMEBase('application', 'pdf', Name=pdfname)
			payload.set_payload((binary_pdf).read())
			 
			# enconding the binary into base64
			encoders.encode_base64(payload)
			 
			# add header with pdf name
			payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
			message.attach(payload)
		 
		#use gmail with port
		session = smtplib.SMTP('smtp.gmail.com', 587)
		 
		#enable security
		session.starttls()
		 
		#login with mail_id and password
		session.login(sender, password)
		 
		text = message.as_string()
		session.sendmail(sender, receiver, text)
		session.quit()
		#print('Mail Sent')
		return render (request, 'successful.html', {})
	else:
		email_patient = Patient.objects.get(anpac_id=anpac_id)
		return render (request, 'report/email_final_reports.html', {'email_patient': email_patient})

def archive (request):
	return render (request, 'report/archive.html', {})


#################### Solely Functional that return no HTTPResponses Below ####################
###########																        ##############
###########	    	    	Only Pythony Things below						    ##############
###########																        ##############
###########																        ##############

def FinalReportExists (path_to_file, CobasOrCDA, anpac_id):
	import os.path
	file_exists = os.path.exists(path_to_file + anpac_id + CobasOrCDA + '.pdf')
	return file_exists


def printDataFromPost (data):
	for key, value in data.items():
		print(key)
		print(value)
		print('*******')

def extractRequisitionAnpacIDCDA(data):
	cda_anpac_ids = []
	for key, value in data.items():
		if key[0:4] == 'cda:':
			cda_anpac_ids.append(value)
	return cda_anpac_ids

def extractRequisitionAnpacIDCobas(data):
	cobas_anpac_ids = []
	for key, value in data.items():
		if key[0:4] == 'cob:':
			cobas_anpac_ids.append(value)
	return cobas_anpac_ids

def UpdateRequsitionBatchOPMachineModelCDA (cda_requsitions, batch_id, cda_machine_model, operator_name):
	#print('##############')
	#print(cda_requsitions)
	#print(batch_id)
	#print(cda_machine_model)
	#print(operator_name)
	#print('##############')
	inc_batch = Batch(batch_id= batch_id, batch_type= 'CDA')
	inc_batch.save()
	for req in cda_requsitions:
		op_req = Patient.objects.get(anpac_id=req)
		op_req.batch_id_cda = batch_id
		op_req.cda_model_assigned = cda_machine_model
		op_req.cda_test_operator = operator_name
		op_req.save()

def UpdateRequsitionBatchOPMachineModelCobas (cobas_requsitions, batch_id, cobas_machine_model, operator_name):
	#print('##############')
	#print(cobas_requsitions)
	#print(batch_id)
	#print(cobas_machine_model)
	#print(operator_name)
	#print('##############')
	inc_batch = Batch(batch_id= batch_id, batch_type= 'COBAS')
	inc_batch.save()
	for req in cobas_requsitions:
		op_req = Patient.objects.get(anpac_id=req)
		op_req.batch_id_cobas = batch_id
		op_req.cobas_model_assigned = cobas_machine_model
		op_req.cobas_test_operator = operator_name
		op_req.save()

def update_test_status_fromQC(anpac_id):
	#print(anpac_id)
	patient_info = Patient.objects.filter(anpac_id=anpac_id)
	choices = IndividualTests(patient_info)
	patient = Patient.objects.get(anpac_id=anpac_id)
	if choices['psa_choice'] == 'checked':
		patient.psa_status = 'Waiting'
	else:
		patient.psa_status = 'Not-Selected'
	if choices['afp_choice'] == 'checked':
		patient.afp_status = 'Waiting'
	else:
		patient.afp_status = 'Not-Selected'
	if choices['ca125_choice'] == 'checked':
		patient.ca125_status = 'Waiting'
	else:
		patient.ca125_status = 'Not-Selected'
	if choices['ca19_9_choice'] == 'checked':
		patient.ca19_9_status = 'Waiting'
	else:
		patient.ca19_9_status = 'Not-Selected'
	if choices['cea_choice'] == 'checked':
		patient.cea_status = 'Waiting'
	else:
		patient.cea_status = 'Not-Selected'
	if choices['cda_status'] == 'Waiting':
		patient.cda_status = 'Waiting'
	else:
		patient.cda_status = 'Not-Selected'
	if choices['cobas_status'] == 'Waiting':
		patient.cobas_status = 'Waiting'
	patient.save()
	return

def IndividualTests (patient_info):
	if patient_info.exists():
		choices = {
			"psa_choice": "",
			"afp_choice": "",
			"ca125_choice": "",
			"ca19_9_choice": "",
			"cea_choice": "",
			"cda_assay": "",
			"cobas_status":"",
			"cda_status":"",
		}
		
		if patient_info[0].psa_choice:
			choices["psa_choice"] = "checked"
			choices['cobas_status']= 'Waiting'

		if patient_info[0].afp_choice:
			choices["afp_choice"] = "checked"
			choices['cobas_status']= 'Waiting'

		if patient_info[0].ca125_choice:
			choices["ca125_choice"] = "checked"
			choices['cobas_status']= 'Waiting'

		if patient_info[0].ca19_9_choice:
			choices["ca19_9_choice"] = "checked"
			choices['cobas_status']= 'Waiting'

		if patient_info[0].cea_choice:
			choices["cea_choice"] = "checked"
			choices['cobas_status']= 'Waiting'

		if patient_info[0].cda_assay:
			choices["cda_assay"] = "checked"
			choices['cda_status']= 'Waiting'
	return choices

def update_test_status_batch(request):
	#print(request)
	#print('***************')
	try:
		cda_batch_status = request['cda_batch_complete']
		if not cda_batch_status == '':
			batch_req = Patient.objects.filter(batch_id_cda=cda_batch_status)
			#print(batch_req)
			for patient in batch_req:
				patient = Patient.objects.get(anpac_id=patient.anpac_id)
				patient.cda_status = 'Complete'
				patient.save()
			batch_update = Batch.objects.get(batch_id=cda_batch_status)
			batch_update.batch_status = 'Complete'
			batch_update.save()
	except Exception as e:
		cobas_batch_status = request['cobas_batch_complete']
		if not cobas_batch_status == '':
			batch_req = Patient.objects.filter(batch_id_cobas=cobas_batch_status)
			for bat_patient in batch_req:
				patient = Patient.objects.get(anpac_id=bat_patient)
				if (patient.psa_choice):
					patient.psa_status = 'Complete'
				if (patient.afp_choice):
					patient.afp_status = 'Complete'
				if (patient.ca125_choice):
					patient.ca125_status = 'Complete'
				if (patient.ca19_9_choice):
					patient.ca19_9_status = 'Complete'
				if (patient.cea_choice):
					patient.cea_status = 'Complete'
				patient.cobas_status = 'Complete'
				patient.save()
			batch_update = Batch.objects.get(batch_id=cobas_batch_status)
			batch_update.batch_status = 'Complete'
			batch_update.save()
			return 'cobas'
			#print(batch_req)

	


def test_status_update(request):
	data = request
	for stuff in data:
		if stuff[0:4] == 'cda:':
			#print(stuff[0:4])
			#print(stuff[5:])
			#print(data.getlist(stuff))
			patient = Patient.objects.get(anpac_id=stuff[4:])
			patient.cda_status = 'Complete'
			patient.save()
			#print('CDA Status Updated')
		elif stuff[0:6] == 'cobas:':
			#print(stuff[0:6])
			#print(stuff[6:])
			#print(data.getlist(stuff))
			patient = Patient.objects.get(anpac_id=stuff[6:])
			if (patient.psa_choice):
				patient.psa_status = 'Complete'
			if (patient.afp_choice):
				patient.afp_status = 'Complete'
			if (patient.ca125_choice):
				patient.ca125_status = 'Complete'
			if (patient.ca19_9_choice):
				patient.ca19_9_status = 'Complete'
			if (patient.cea_choice):
				patient.cea_status = 'Complete'
			patient.cobas_status = 'Complete'
			patient.save()
			#print('Cobas tests saved')
		else:
			print('Something is not right in test_status_update')

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

def ImportRequisitionsExcel (Path_excel_file, request):
	df = pandas.read_excel(Path_excel_file, header=1)
	df.to_dict('index')
	approve_all = request.POST.get('excel_qc_approved', '')
	location = request.POST.get('storage_location', '')
	#print(location)
	#print(df.keys())
	for index, elem in enumerate (df['AnPac Bio ID (Required)']):
		if Patient.objects.filter(anpac_id = df['AnPac Bio ID (Required)'][index]).exists():
			print(df['AnPac Bio ID (Required)'][index] + ' already entered, skipping...')
		else:
			incoming_patient = Patient(anpac_id = df['AnPac Bio ID (Required)'][index])
			incoming_patient.last_name = checkNan(df['Last Name'][index])
			incoming_patient.first_name = checkNan(df['First Name'][index])
			incoming_patient.middle_initial = checkNan(df['Middle Initial'][index])
			incoming_patient.patient_id = df['Patient ID'][index]
			incoming_patient.sex = df['Sex (Male/Female)'][index]
			incoming_patient.dob = df['Date of birth (MM/DD/YYYY)'][index].date()
			incoming_patient.phone_no = df['Phone No. \n(888 888 888)'][index]
			incoming_patient.email_address = df['Email Address'][index]
			incoming_patient.mrn_no = df['Medical Record No. (MRN)'][index]
			incoming_patient.patient_clinical_history = df['Clinical History'][index]
			incoming_patient.billing_address = df['Address'][index]
			incoming_patient.billing_state = df['State'][index]
			incoming_patient.billing_zipcode = df['Zipcode'][index]
			incoming_patient.bill_to = df['Bill To: \n(Client, Patient, Insurance, Medicare, Cash/Check)'][index]
			incoming_patient.insurance_company = df['Insurance Provider'][index]
			incoming_patient.ins_pol_sub_nam = df['Insurance Policy Subscriber Name'][index]
			incoming_patient.pat_rel_to_ins_pol_sub = df[ 'Patient Relationship To Insurance Policy Subscriber:\n(Self, Sponse, Child, Other)'][index]
			incoming_patient.pat_rel_address = df['Billing Address'][index]
			incoming_patient.pat_rel_state = df['State.1'][index]
			incoming_patient.pat_rel_zip = df['Zipcode.1'][index]
			incoming_patient.subscriber_no = df['Subscriber No.'][index]
			incoming_patient.group_no = df['Group No.'][index]
			incoming_patient.medicare_no = df['Medicare No.'][index]
			incoming_patient.client_name = df['Client (Required)'][index]
			incoming_patient.sender_id = df['Specimen ID (required)'][index]
			incoming_patient.or_physician = df['Ordering/Treating Physician'][index]
			incoming_patient.or_physician_no = df['Ordering/Treating Physician Phone No. (888 888 8888)'][index]
			incoming_patient.or_physician_email = df['Ordering/Treating Physician Email Address'][index]
			incoming_patient.date_collected = df['Date Collected (MM/DD/YYYY)'][index].date()
			incoming_patient.time_collected = df['Time Collected (HH:MM AM or PM) '][index]
			incoming_patient.collected_by = df['Collected By'][index]
			incoming_patient.sample_type = df['Sample Type (Serum or Whole Blood)'][index]
			incoming_patient.vol_amount = df['Sample Volume (ml)'][index]
			incoming_patient.storage_location = location
			if df['PSA, Total (Y or leave blank if not applicable)'][index] == 'Y' or df['PSA, Total (Y or leave blank if not applicable)'][index] == 'y':
				incoming_patient.psa_choice = True
			else:
				incoming_patient.psa_choice = False
			if df['AFP \n(Y or leave blank if not applicable)'][index] == 'Y' or df['AFP \n(Y or leave blank if not applicable)'][index] == 'y':
				incoming_patient.afp_choice = True
			else:
				incoming_patient.afp_choice = False
			if df['CA125 \n(Y or leave blank if not applicable)'][index] =='Y' or df['CA125 \n(Y or leave blank if not applicable)'][index] =='y':
				incoming_patient.ca125_choice = True
			else:
				incoming_patient.ca125_choice = False
			if df['CA19-9 \n(Y or leave blank if not applicable)'][index] == 'Y' or df['CA19-9 \n(Y or leave blank if not applicable)'][index] == 'y':
				incoming_patient.ca19_9_choice = True
			else:
				incoming_patient.ca19_9_choice = False
			if df['CEA \n(Y or leave blank if not applicable)'][index] == 'Y' or df['CEA \n(Y or leave blank if not applicable)'][index] == 'y':
				incoming_patient.cea_choice = True
			else:
				incoming_patient.cea_choice = False
			if df[ 'CDA Assay (Y or leave blank if not applicable)'][index] == 'Y' or df[ 'CDA Assay (Y or leave blank if not applicable)'][index] == 'y':
				incoming_patient.cda_assay = True
			else:
				incoming_patient.cda_assay = False

			if approve_all == 'approve_all':
				incoming_patient.req_status = 'Approved'
			else:
				incoming_patient.req_status = 'Pending'
			today = date.today()
			date_today = today.strftime("%Y-%m-%d %H:%M:%S")
			incoming_patient.req_date_created = date_today
			incoming_patient.info_sub_by = request.user.first_name + ' ' + request.user.last_name
			if approve_all == 'approve_all':
				incoming_patient.updated_at = date_today
			incoming_patient.save()
			if approve_all == 'approve_all':
				update_test_status_fromQC(df['AnPac Bio ID (Required)'][index])
	return

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



def PDFCreateReport (anpac_id, assay, FillDataType):
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/"
	pdf_template = ''
	if assay == '_cda':
		pdf_template = "ReportTemplates/CDA_Report_Template.pdf"
	else:
		pdf_template = "ReportTemplates/Cobas_Report_Form_Template.pdf"
	DirectoryExists (path_to_dir)
	#print(assay + pdf_template)
	fill_pdf(pdf_template, path_to_dir + anpac_id + assay + ".PDF", FillDataType)

def PDFCreateFinalReport (anpac_id, assay, FillDataType):
	path_to_dir = "/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/finalreports/" + anpac_id + "/approved/"
	pdf_template = ''
	if assay == '_cda_Approved':
		pdf_template = "ReportTemplates/CDA_Report_Template-SIGNED.pdf"
	else:
		pdf_template = "ReportTemplates/Cobas_Report_Form_Template-SIGNED.pdf"
	DirectoryExists (path_to_dir)
	#print(assay + pdf_template)
	fill_pdf(pdf_template, path_to_dir + anpac_id + assay + ".PDF", FillDataType)

def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        for annotation in annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    if key in data_dict.keys():
                        if type(data_dict[key]) == bool:
                            if data_dict[key] == True:
                                annotation.update(pdfrw.PdfDict(
                                    AS=pdfrw.PdfName('Yes')))
                        else:
                            annotation.update(
                                pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                            )
                            annotation.update(pdfrw.PdfDict(AP=''))
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)
#filling PDF report CDA
def FillDataCDAReport (anpac_id, current_user):
	#print('FillDataCDAReport Invoked: ')
	patient_report = Patient.objects.get(anpac_id=anpac_id)
	today = date.today()
	data = {}
	data['report_date'] = today.strftime("%b-%d-%Y")
	data['mrn_no'] = patient_report.mrn_no
	data['patient_name'] = patient_report.last_name + ', ' + patient_report.first_name + ' ' + patient_report.middle_initial
	data['date_of_birth'] = patient_report.dob
	data['gender'] = patient_report.sex
	data['patient_id'] = patient_report.patient_id
	data['specimen_type'] = patient_report.sample_type
	data['recieved_date'] = patient_report.req_date_created[0:13] #have to put req creation date, no field for "recieved sample date"
	data['specimen_id'] = patient_report.sender_id
	data['collection_date'] = patient_report.date_collected[0:13]
	data['footer'] = patient_report.last_name + ', ' + patient_report.first_name + ' ' + patient_report.middle_initial
	data['time_date_approved'] = today.strftime("%b-%d-%Y")
	data['ordering_physician_info'] = patient_report.or_physician + '\n' + patient_report.or_physician_no + '\n' + patient_report.or_physician_email
	data['approved_by'] = current_user.first_name +' '+ current_user.last_name
	data['lab_notes'] = patient_report.cda_test_notes
	data['Sample_ID_1'] = patient_report.anpac_id # CDA score is Hardcoded until more CDA1, CDA2 tests are added
	data['test_1'] = 'CDA Assay'
	data['result_1'] = patient_report.cda_score
	data['reference_value_1'] = '0.00 - 42.00'
	return data
#Filling COBAS pdf report
def FillDataCobasReport (anpac_id, current_user):
	patient_report = Patient.objects.get(anpac_id=anpac_id)
	today = date.today()
	data = {}
	data['report_date'] = today.strftime("%b-%d-%Y")
	data['mrn_no'] = patient_report.mrn_no
	data['patient_name'] = patient_report.last_name + ', ' + patient_report.first_name + ' ' + patient_report.middle_initial
	data['date_of_birth'] = patient_report.dob
	data['gender'] = patient_report.sex
	data['patient_id'] = patient_report.patient_id
	data['specimen_type'] = patient_report.sample_type
	data['recieved_date'] = patient_report.req_date_created[0:13] #have to put req creation date, no field for "recieved sample date"
	data['specimen_id'] = patient_report.sender_id
	data['collection_date'] = patient_report.date_collected[0:13]
	data['footer'] = patient_report.last_name + ', ' + patient_report.first_name + ' ' + patient_report.middle_initial
	data['time_date_approved'] = today.strftime("%b-%d-%Y")
	data['ordering_physician_info'] = patient_report.or_physician + '\n' + patient_report.or_physician_no + '\n' + patient_report.or_physician_email
	data['approved_by'] = current_user.first_name +' '+ current_user.last_name
	data['lab_notes'] = patient_report.cobas_test_notes
	test_to_check = []
	if patient_report.psa_choice:
		test_to_check.append('psa')
	if patient_report.afp_choice:
		test_to_check.append('afp')
	if patient_report.ca125_choice:
		test_to_check.append('ca125')
	if patient_report.ca19_9_choice:
		test_to_check.append('ca199')
	if patient_report.cea_choice:
		test_to_check.append('cea')
	test_length = len(test_to_check)
	test_row = 1
	for test in test_to_check:
		if test == 'psa':
			data['Sample_ID_' + str(test_row)] = patient_report.anpac_id
			data['test_' + str(test_row)] = 'Total, PSA'
			data['result_'+ str(test_row)] = patient_report.psa_score + ' ng/mL'
			data['reference_value_' + str(test_row)] = '0.00 - 4.00 ng/mL'
			test_row +=1
		elif test =='afp':
			data['Sample_ID_' + str(test_row)] = patient_report.anpac_id
			data['test_' + str(test_row)] = 'AFP'
			data['result_'+ str(test_row)] = patient_report.afp_score + ' IU/mL'
			data['reference_value_' + str(test_row)] = '0.00 - 5.80 IU/mL'
			test_row +=1
		elif test =='ca125':
			data['Sample_ID_' + str(test_row)] = patient_report.anpac_id
			data['test_' + str(test_row)] = "CA125"
			data['result_'+ str(test_row)] = patient_report.ca125_score + ' U/mL'
			data['reference_value_' + str(test_row)] = '0.00 - 35.00 U/mL'
			test_row +=1
		elif test =='ca199':
			data['Sample_ID_' + str(test_row)] = patient_report.anpac_id
			data['test_' + str(test_row)] = 'CA19-9'
			data['result_'+ str(test_row)] = patient_report.ca19_9_score + ' U/mL'
			data['reference_value_' + str(test_row)] = '0.00 - 39.00 U/mL'
			test_row +=1
		elif test =='cea':
			data['Sample_ID_' + str(test_row)] = patient_report.anpac_id
			data['test_' + str(test_row)] = 'CEA'
			data['result_'+ str(test_row)] = patient_report.cea_score + ' ng/mL'
			data['reference_value_' + str(test_row)] = '0.00 - 4.70 ng/mL'
			test_row +=1
	return data

def checkNan (string_check):
	if string_check == 'nan':
		return ''
	else:
		return string_check

#BATCH ID CREATION STUFF
#Naming Scheme may change so for future purposes will have to enter in search parameters in method
def CobasOrCDA (machine_model, cobas_list_models, cda_list_models):
	if machine_model in cda_list_models:
		return 'C' 
	elif machine_model in cobas_list_models:
		return 'R'

def MachineNumberCDA (machine_model):
	return machine_model[3]

def MachineNumberCobas (machine_model):
	return machine_model[len(machine_model) - 1]

def BatchYear ():
	import time
	currentYear = time.strftime("%y", time.localtime())
	return str(currentYear)

def incrementRequsitionAmount (machine_identifier):
	try:
		inuse_machine = MachineIds.objects.get(machine_identifier=machine_identifier)
		inuse_machine.batch_amount = str(int(inuse_machine.batch_amount) + 1).zfill(len(inuse_machine.batch_amount))
		inuse_machine.save()
	except Exception as e:
		print(e)

def getbatchnum (machine_identifier):
	inuse_machine = MachineIds.objects.get(machine_identifier=machine_identifier)
	required_batch_id = inuse_machine.batch_amount
	incrementRequsitionAmount(machine_identifier) #need to increment for future batches
	return required_batch_id


def BatchIDCreate(CobasOrCda, InstrumentNum, Year, batch_num):
	#print('Cobas or Cda: '+ str(CobasOrCDA))
	#print('InstrumentNumber: ' + str(InstrumentNum))
	#print('Year: ' + str(Year))
	#print('batch_num: ' + str(batch_num))
	return str(CobasOrCda) + str(InstrumentNum) + str(Year) + str(batch_num)

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
	email = 'dennis_lin@anpacbio.com'
	password = 'dwcepnbrmrnnfckg'
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
			archive_patient.req_status = 'Archive'
			archive_patient.save()
	if cobasorcda == 'cda':
		if archive_patient.cobas_status =='ResultsApproved' or archive_patient.cobas_status == 'Not-Selected':
			archive_patient.req_status = 'Archive'
			archive_patient.save()











