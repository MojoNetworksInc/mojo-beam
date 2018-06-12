from django.contrib import admin
from beam.models import configuration
# Register your models here.

class SearchConfiguration(admin.ModelAdmin):
	search_fields = ['key_name','key_value',]
	model = configuration
	list_display= ('id', 'key_name', 'key_value',)
	

admin.site.register(configuration, SearchConfiguration)