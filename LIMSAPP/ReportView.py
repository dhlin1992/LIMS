from django.shortcuts import render, redirect
from django.http import FileResponse, Http404, HttpResponse
import datetime
from datetime import date
from .models import Patient
from LIMSAPP.DirectoryFunctions import DirectoryExists
import pdfrw
import pandas
import mimetypes

def create_report(request):
	all_patients = Patient.objects.all()
	return render(request, 'report/create_report.html', {'all_patients': all_patients})

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
