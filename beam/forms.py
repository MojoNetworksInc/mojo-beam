import datetime
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django.db.models.query_utils import Q
from django.forms.forms import Form
from django.forms.models import ModelForm
from beam.models import ssid_request
from django.forms import ModelChoiceField
from django.contrib.auth.models import User
import uuid
import string
import random

class ssid_requestForm(forms.ModelForm):	
	class Meta:
		model = ssid_request
		fields = ['ssid_name', 'duration', 'security', 'password']
		exclude = ['location_name'] 

	def __init__(self, request, *args, **kwargs):
		super(ssid_requestForm, self).__init__(*args, **kwargs)		
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control'
			for field_name, field in self.fields.items():
				if field_name !='password':
					field.widget.attrs['class'] = 'form-control'
					field.widget.attrs['required'] = True 			
	 
	def clean_password(self):
		password_value = self.cleaned_data.get('password', '')
		security = self.cleaned_data.get('security', 0)  
		if security != 0:
			print "password_value" , password_value
			if password_value in [None, '']:
				self.add_error('password', "Password required")
		if security == 0:
			return ''
		return password_value

	def clean(self):
		cleaned_data=super(ssid_requestForm, self).clean()	
		return cleaned_data
	
