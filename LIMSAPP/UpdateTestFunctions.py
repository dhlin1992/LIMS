from .models import Patient

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