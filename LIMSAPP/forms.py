from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
	class Meta:
		model = Patient
		fields ='__all__'
		#fields = [ "sender_id", "last_name", "first_name", "middle_initial", "sex", 
	 	#"dob", "phone_no", "anpac_id", "email_address", "medicare_no", "or_physician", "or_physician_no", "or_physician_email",
		# "date_collected", "time_collected", "collected_by", "billing_address", "billing_state", "billing_zipcode",
		# "bill_to", "insurance_company", "ins_pol_sub_nam", "pat_rel_to_ins_pol_sub", "pat_rel_address", "pat_rel_state", "pat_rel_zip",
		# "subscriber_no", "group_no", "psa_choice", "afp_choice", "ca125_choice", "ca19_9_choice", "cea_choice", "cda_assay", "info_sub_by",
		# "status", "req_date_created", "updated_at", "edited_notes"
		# ]

class EditProfileForm(UserChangeForm):
	password = forms.CharField(label="", widget=forms.TextInput(attrs={'type':'hidden'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password',)
		#to exclude fields use below
		#exclude = ()

class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="Enter your Email Address", widget=forms.TextInput(attrs={'class':'form-control'}))
	first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
	last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['class'] = 'form-control'
	 