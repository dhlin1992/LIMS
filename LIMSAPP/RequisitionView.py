from django.shortcuts import render, redirect
from pathlib import Path
from datetime import date
from LIMSAPP.DirectoryFunctions import DirectoryExists
from LIMSAPP.UpdateTestFunctions import update_test_status_fromQC, IndividualTests
from django.contrib import messages
from django.core.files.storage import default_storage
import pandas
from . models import Patient
from .forms import PatientForm
import mimetypes
from django.http import FileResponse, Http404, HttpResponse


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

		return render(request,'requisitions/requisition.html',{})

def download_req_excel (request):
	fl_path = '/Users/dennisl/Desktop/Engineering/SEPrograms/AnpacApps/ANPACLIMS/RequisitionExcelTemplate'
	filename = 'Requisition_Sheet_Template.xlsx'
	fl = open(fl_path + '/' + filename, "rb")
	
	mime_type, _ = mimetypes.guess_type(fl_path)
	response = HttpResponse(fl, content_type= mime_type)
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

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
		return render(request, 'requisitions/search_req.html', {"all_items":all_items})

def archive (request):
	if request.method == 'POST':
		data = request.POST
		search_param = data.get('search-param', '')
		if search_param == '':
			messages.warning(request, ('Please enter in a search term'))
			return render (request, 'report/archive.html', {})
		else:
			result = QueryDB(search_param,data['search-Filter'])
			if str(result) == 'Patient matching query does not exist.':
				messages.warning(request, ( search_param + ' not found. Please try again!'))
				result = ''
			return render (request, 'report/archive.html', {'result':result, 'search_param_found': data['search-Filter'], 'key': search_param})
	else:
		return render (request, 'report/archive.html', {})

def checkNan (string_check):
		if string_check == 'nan':
			return ''
		else:
			return string_check

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