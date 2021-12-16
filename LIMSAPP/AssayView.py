from django.shortcuts import render, redirect
from pathlib import Path
from . models import Patient, MachineIds, Batch
from django.contrib import messages
import datetime
from datetime import date

cobas_list_models = ['E411.1', 'E411.2']
cda_list_models= ['CDA4.1', 'CDA3.2', 'CDA3.1', 'CDA2.1', 'CDA1.1']

def op_machine_assignment (request):
	if request.method == 'POST':
		data = request.POST
		try:
			#Need to check that user made a selection for Machine
			machine_model_cda = request.POST.get('cda_machine_num', '')
			machine_model_cobas = request.POST.get('cobas_machine_num', '')
			cda_requsitions = extractRequisitionAnpacIDCDA(data)
			cobas_requsitions = extractRequisitionAnpacIDCobas(data)

			# Cobas 28 max samples

			# CDA 40 not including controls
			if cda_requsitions:
				if machine_model_cda:
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
			file = request.FILES['csv_file_values']
			file_name = default_storage.save(path_to_dir + file.name, file)
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
	return str(CobasOrCda) + str(InstrumentNum) + str(Year) + str(batch_num)

def UpdateRequsitionBatchOPMachineModelCDA (cda_requsitions, batch_id, cda_machine_model, operator_name):
	inc_batch = Batch(batch_id= batch_id, batch_type= 'CDA')
	inc_batch.save()
	for req in cda_requsitions:
		op_req = Patient.objects.get(anpac_id=req)
		op_req.batch_id_cda = batch_id
		op_req.cda_model_assigned = cda_machine_model
		op_req.cda_test_operator = operator_name
		op_req.save()

def UpdateRequsitionBatchOPMachineModelCobas (cobas_requsitions, batch_id, cobas_machine_model, operator_name):
	inc_batch = Batch(batch_id= batch_id, batch_type= 'COBAS')
	inc_batch.save()
	for req in cobas_requsitions:
		op_req = Patient.objects.get(anpac_id=req)
		op_req.batch_id_cobas = batch_id
		op_req.cobas_model_assigned = cobas_machine_model
		op_req.cobas_test_operator = operator_name
		op_req.save()

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

def update_test_status_batch(request):
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
