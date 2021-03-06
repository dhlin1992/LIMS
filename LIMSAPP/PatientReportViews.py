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

def success(request):
	return render(request, 'successful.html', {})

def cda_assay_status_update(request, status, anpac_id):
	item = Patient.objects.get(anpac_id = anpac_id)
	item.cda_status = status
	item.save()
	return redirect('assay')

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
	return render(request, 'report/approval_sign_off.html', {'all_patients':all_patients, "cda_tab": cda_tab, 'cobas_tab': cobas_tab})

def approve_report_cobas(request, anpac_id):
	approved_patient = Patient.objects.get(anpac_id=anpac_id)
	approved_patient.cobas_status = 'ResultsApproved'
	approved_patient.save()
	all_patients = Patient.objects.all()
	cobas_tab = 'active'
	cda_tab = ''
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
		email_account = EmailAccounts.objects.get(account_name= 'EmailNotification')
		email = email_account.email_address
		password = email_account.email_password
		sender = email
		# get the password in the gmail (manage your google account, click on the avatar on the right)
		# then go to security (right) and app password (center)
		# insert the password and then choose mail and this computer and then generate
		# copy the password generated here
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
			ArchiveRequsition(anpac_id, 'cda')
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
			ArchiveRequsition(anpac_id, 'cobas')
		 
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


#################### Solely Functional that return no HTTPResponses Below ####################
###########																        ##############
###########	    	    	Only Pythony Things below						    ##############
###########																        ##############
###########																        ##############


#filter for searchs in archives
def QueryDB (key, search_param):
	if search_param == 'anpac_id':
		try:
			return Patient.objects.get(anpac_id=key)
		except Exception as e:
			return e
	elif search_param == 'batch_id':
		if key[0] == 'C':
			try:
				return Patient.objects.filter(batch_id_cda=key)
			except Exception as e:
				return e
		elif key[0] =='R':
			try:
				return Patient.objects.filter(batch_id_cobas=key)
			except Exception as e:
				return e
		else:
			return 'Not a valid Batch ID'
	elif search_param == 'client':
		try:
			return Patient.objects.filter(client_name=key)
		except Exception as e:
				return e

	return 'Key not found'


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

def DirectoryExists (path_to_dir):
	Path(path_to_dir).mkdir(parents=True, exist_ok=True)

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











