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