from django.db import models
from django.utils import timezone

# Create your models here.
class Patient(models.Model):
	#ArbitraryRequisitionDetails
	req_date_created = models.CharField(max_length = 50, null=True, blank=True)
	updated_at = models.CharField(max_length = 50, null=True, blank=True)

	#PatientInfo
	last_name = models.CharField(max_length = 50, null=True, blank=True)
	first_name = models.CharField(max_length = 50, null=True, blank=True)
	middle_initial = models.CharField(max_length = 10, null=True, blank=True)
	patient_id = models.CharField(max_length = 50, null=True, blank=True)
	sex = models.CharField(max_length = 10, null=True, blank=True)
	dob = models.CharField(max_length = 50) #make this required
	phone_no = models.CharField(max_length = 50, null=True, blank=True)
	email_address = models.CharField(max_length = 50, null=True, blank=True)
	mrn_no = models.CharField(max_length = 50, null=True, blank=True)#medical record Number
	patient_clinical_history = models.CharField(max_length = 400, null=True, blank=True)

	#billing Information
	billing_address = models.CharField(max_length = 50, null=True, blank=True)
	billing_state = models.CharField(max_length = 50, null=True, blank=True)
	billing_zipcode = models.CharField(max_length = 50, null=True, blank=True)
	bill_to = models.CharField(max_length = 50, null=True, blank=True)
	insurance_company = models.CharField(max_length = 50, null=True, blank=True)
	ins_pol_sub_nam = models.CharField(max_length = 50, null=True, blank=True)
	pat_rel_to_ins_pol_sub = models.CharField(max_length = 50, null=True, blank=True)
	pat_rel_address = models.CharField(max_length = 50, null=True, blank=True)
	pat_rel_state = models.CharField(max_length = 50, null=True, blank=True)
	pat_rel_zip = models.CharField(max_length = 50, null=True, blank=True)
	subscriber_no = models.CharField(max_length = 50, null=True, blank=True)
	group_no = models.CharField(max_length = 50, null=True, blank=True)
	medicare_no = models.CharField(max_length = 50, null=True, blank=True)

	#Sample Information
	client_name = models.CharField(max_length = 50, null=True, blank=True) 
	anpac_id = models.CharField(max_length = 50, null=True, blank=True)
	sender_id = models.CharField(max_length = 50, null=True, blank=True)#specimen ID
	or_physician = models.CharField(max_length = 50, null=True, blank=True)
	or_physician_no = models.CharField(max_length = 50, null=True, blank=True)
	or_physician_email = models.CharField(max_length = 50, null=True, blank=True)
	date_collected = models.CharField(max_length = 50, null=True, blank=True)
	time_collected = models.CharField(max_length = 50, null=True, blank=True)
	collected_by = models.CharField(max_length = 50, null=True, blank=True)

	req_status = models.CharField(max_length = 50, null=True, blank=True, default='Pending') #Set to default since its only set when created. Pending, Rejected or Approved
	
	# For now inserting individual tests with true or false
	#ind_tests = models.CharField(max_length = 50)

	psa_choice = models.BooleanField(default = False)
	afp_choice = models.BooleanField(default = False)
	ca125_choice = models.BooleanField(default = False)
	ca19_9_choice = models.BooleanField(default = False)
	cea_choice = models.BooleanField(default = False)
	cda_assay = models.BooleanField(default = False)

	#Info for Edit/QC Requisition
	edited_notes = models.CharField(max_length = 200, null=True, blank=True)
	info_sub_by = models.CharField(max_length = 50, null=True, blank=True)
	info_qc_by = models.CharField(max_length = 50, null=True, blank=True)

	##need to be able to input assay Score for Entry Results Page
	psa_score = models.CharField(max_length = 50, null=True, blank=True)
	afp_score = models.CharField(max_length = 50, null=True, blank=True)
	ca125_score = models.CharField(max_length = 50, null=True, blank=True)
	ca19_9_score = models.CharField(max_length = 50, null=True, blank=True)
	cea_score = models.CharField(max_length = 50, null=True, blank=True)
	cda_score = models.CharField(max_length = 50, null=True, blank=True)

	##need to know where this sample is stored: inuse, minus80, minus20, preparing (processing?)
	storage_location = models.CharField(max_length = 50, null=True, blank=True)

	#need to know status of each assay that is offered: waiting, running, complete, rejected
	psa_status = models.CharField(max_length = 50, null=True, blank=True)
	afp_status = models.CharField(max_length = 50, null=True, blank=True)
	ca125_status = models.CharField(max_length = 50, null=True, blank=True)
	ca19_9_status = models.CharField(max_length = 50, null=True, blank=True)
	cea_status = models.CharField(max_length = 50, null=True, blank=True)
	cda_status = models.CharField(max_length = 50, null=True, blank=True)
	cobas_status = models.CharField(max_length = 50, null=True, blank=True)

	#need to know which operator has been assigned to run the samples
	cobas_test_operator = models.CharField(max_length = 50, null=True, blank=True)
	cda_test_operator = models.CharField(max_length = 50, null=True, blank=True)

	#need to know which specific machine it has been run on
	cda_model_assigned = models.CharField(max_length = 50, null=True, blank=True) #CDA2.X, CDA3.X, or CDA4.X
	cobas_model_assigned = models.CharField(max_length = 50, null=True, blank=True) #need to ask the model scheme for this

	#batch assignment
	batch_id_cobas = models.CharField(max_length = 50, null=True, blank=True) #Cobas Batch ID
	batch_id_cda = models.CharField(max_length = 50, null=True, blank=True) # CDA Batch ID

	#need to know how much volume was received?
	vol_amount = models.CharField(max_length = 50, null=True, blank=True)
	sample_type = models.CharField(max_length = 50, null=True, blank=True)

	#lab notes
	cobas_test_notes = models.CharField(max_length = 200, null=True, blank=True)#External Report Notes
	cda_test_notes = models.CharField(max_length = 200, null=True, blank=True)#External Report Notes
	cobas_internal_notes = models.CharField(max_length = 200, null=True, blank=True)#Internal Notes (does not show up on report)
	cda_internal_notes = models.CharField(max_length = 200, null=True, blank=True)#Internal Notes (does not show up on report)

        
	def __str__(self):
		return self.anpac_id

class Batch(models.Model):
	batch_type = models.CharField(max_length = 10, null=True, blank=True) # cda or cobas
	batch_id = models.CharField(max_length = 50, null=True, blank=True)
	batch_status = models.CharField(max_length = 10, null=True, blank=True, default='Waiting') #Waiting or Complete

	def __str__(self):
		return self.batch_id

class MachineIds(models.Model):
	machine_identifier = models.CharField(max_length = 10, null=True, blank=True) #CDA4.1, E411.1 or whatever
	#machine_type = models.CharField(max_length = 10, null=True, blank=True) #cda or cobas
	#machine_generation = models.CharField(max_length = 10, null=True, blank=True) #relevant for CDA as of 11/04/2021 '1' - '4'
	batch_amount = models.CharField(max_length = 4, null=True, blank=True) #too lazy to figure out incrementing int, keeping stuff as String for now just convert while incrementing

	def __str__(self):
		return self.machine_identifier

class EmailAccounts(models.Model):
	account_name = models.CharField(max_length = 50, null=True, blank=True)
	email_address = models.CharField(max_length = 50, null=True, blank=True)
	email_password = models.CharField(max_length = 50, null=True, blank=True)

	def __str__(self):
		return self.account_name


	


