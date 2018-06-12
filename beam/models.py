from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class configuration(models.Model):
	key_name=models.CharField(max_length = 128)
	key_value=models.CharField(max_length = 512)
	def __unicode__(self):
            return str(self.key_name)

class ssid_request(models.Model):
	ssid_name = models.CharField(max_length = 32)
	service_url = models.CharField(max_length = 128)
	location_id = models.IntegerField(default=0)
	location_name = models.CharField(max_length = 128)
	duration = models.IntegerField(default=24)
	status = models.IntegerField(default=0)
	active = models.IntegerField(default=0)
	requested_by = models.ForeignKey(User, related_name = 'requested_by')
	modified_by = models.ForeignKey(User,related_name = 'modified_by', null=True, blank=True, default = None)
	security = models.IntegerField(default=0)
	password = models.CharField(max_length = 128, null=True, blank=True, default = None )
	date = models.DateField(default=date.today)


	def __unicode__(self):
            return str(self.ssid_name)

	def status_value(self):
		if self.status == 0:
			return "Pending"
		elif self.status == 1:
			return "Approved"
		elif self.status == 2:
			return "Rejected"
		elif self.status == 3:
			return "Expired"
		return "N/A"
		
	def active_value(self):
		if self.active == 0:
			return "N"
		return "Y"

	def security_value(self):		
		if self.security == 1:
			return "WPA2 PSK"
		if self.security == 2:
			return "WPA2/WPA PSK"
		return "Open"





