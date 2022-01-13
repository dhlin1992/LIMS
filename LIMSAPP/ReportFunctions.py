from .models import Patient
import datetime
from datetime import date
from LIMSAPP.DirectoryFunctions import DirectoryExists
import pdfrw
from django.core.files.storage import default_storage

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