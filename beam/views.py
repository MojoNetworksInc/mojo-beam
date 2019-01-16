from django.shortcuts import render
from beam.models import ssid_request
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from beam.forms import ssid_requestForm
import json
import ast
from beam import locations
from beam.mwm import manager
from beam.mwm.manager import *
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models.query_utils import Q



@login_required
def _logout(request):
	logout(request)
	return render(request, 'registration/login.html')

def _login(request):
	print "login request"
	if not request.user.is_authenticated():
		if request.method == 'POST':
			username = request.POST["username"]
			password = request.POST["password"]
			user = authenticate( username=username, password=password)
			if user is not None:
				login(request, user)
				print "login successfull"
				return HttpResponseRedirect(settings.HOME_URL)
			else:
				print "login failure"
				return render(request, 'registration/login.html')
		else:
			return render(request, 'registration/login.html')
	else:
		print "user is  authenticated", request.method
		return HttpResponseRedirect(settings.HOME_URL)

@login_required
def ssids_modify(request, id=None):
    if id:
        ssid_request_obj=get_object_or_404(ssid_request,pk=id)
    else:
        ssid_request_obj=ssid_request()
    if request.POST:
    	#print "user id", request.user
        form=ssid_requestForm(request, request.POST,instance=ssid_request_obj)
        if  form.is_valid():
            post = form.save(commit=False)
            #print "form is valid -->", request.POST.get("location")
            #print json.dumps(request.POST.get("location"))
            #json_data = ast.literal_eval(request.POST.get("location"))
            json_data_new = request.POST.get("location_id")
            location_new  = json.loads(json_data_new)
            #location = json.dumps(json_data)
            #data= json.loads(location)
            data = location_new

            post.service_url=data["url"]
            post.location_id=data["location_id"]
            post.location_name=data["text"]

            post.requested_by = request.user
            post.save()
            return HttpResponseRedirect(settings.HOME_URL)
        else:
            print "ssid_requestForm is invalid", form.errors, form.non_field_errors
    else:
        #form=MemberForm({"instance":member,"studio":request.user.studiouser.studio_id})
        form=ssid_requestForm(request, instance=ssid_request_obj)
        #form.studio = request.user.studiouser.studio_id
    location_data = locations.load_data()
    tree_data = json.dumps(locations.load_tree_data())
    return render(request, 'beam/ssids_modify.html', {'form': form, 'tree_data':tree_data , 'location_data':location_data , 'id':ssid_request_obj.id}, context_instance=RequestContext(request))

@login_required
def approve_ssid_request(request, id=None):
	redirect_path = request.GET.get('next', settings.HOME_URL)
	if id:
		ssid_request_obj=get_object_or_404(ssid_request,pk=id)
		ssid_request_obj.status=1
		ssid_request_obj.modified_by=request.user
		ssid_request_obj.save()
		return HttpResponseRedirect(redirect_path)
	else:
		return HttpResponseRedirect(redirect_path)

@login_required
def reject_ssid_request(request, id=None):
	redirect_path = request.GET.get('next', settings.HOME_URL)
	if id:
		ssid_request_obj=get_object_or_404(ssid_request,pk=id)
		ssid_request_obj.status=2
		ssid_request_obj.modified_by=request.user
		ssid_request_obj.save()
		return HttpResponseRedirect(redirect_path)
	else:
		# throw exception
		return HttpResponseRedirect(redirect_path)

@login_required
def on_ssid_request(request, id=None):
	redirect_path = request.GET.get('next', settings.HOME_URL)
	if id:
		ssid_request_obj=get_object_or_404(ssid_request,pk=id)
		success = manager.approve_and_create_ssid(ssid_request_obj)
		print "success abc ", success
		if success:
			ssid_request_obj.active=1
			ssid_request_obj.save()
		'''
		 1 Check policy status
		 2 if inherit,
		  	2.1 Change the location policy to cuztomize
		  	2.2 create a device template and ssid
		  	2.3 make created device template as default template for given location

		 3 if customize
		 	3.1 Fetch the current applied device template
		 	3.2 Create a ssid for a location and add this ssid profile to current device template

		'''
		return HttpResponseRedirect(redirect_path)
	else:
		# throw exception
		return HttpResponseRedirect(redirect_path)

@login_required
def off_ssid_request(request, id=None):
	redirect_path = request.GET.get('next', settings.HOME_URL)
	if id:
		ssid_request_obj=get_object_or_404(ssid_request,pk=id)
		success = manager.delete_ssid_profile(ssid_request_obj)
		if success:
			ssid_request_obj.active=0
			ssid_request_obj.save()
		return HttpResponseRedirect(redirect_path)
	else:
		# throw exception
		return HttpResponseRedirect(redirect_path)


def filter_data(request, status_value):
	if request.user.is_superuser:
		return ssid_request.objects.filter(Q(status=status_value))
	else:
		return ssid_request.objects.filter(Q(status=status_value) & Q(requested_by=request.user) )

def set_expire(data):
	data.extra(select={"expired":"SELECT abs(extract(epoch from current_timestamp - created_date)/3600) from beam_ssid_request"})

@login_required
def list_ssid(request, name):
	is_superuser = False
	if request.user.is_superuser:
		is_superuser=True

	status = -1
	if name=="approved":
		#print "approved"
		status = 1
	if name =="rejected":
		#print "rejected"
		status = 2
	if name=="expired":
		#print "expired"
		status = 3
	if name=="pending":
		#print "expired"
		status = 0

	ssids =None
	if status == -1:
		if request.user.is_superuser:
			ssids = ssid_request.objects.all()
		else:
			ssids = ssid_request.objects.filter(Q(requested_by=request.user))
	else:
		ssids = filter_data(request, status)
	count = ssids.count
	paginator = Paginator(ssids, 5,0,True) # Show 10 ssid per page
	page = request.GET.get('page')
	try:
		ssids = paginator.page(page)
	except PageNotAnInteger:
		ssids = paginator.page(1)
	except EmptyPage:
		ssids = paginator.page(paginator.num_pages)
	context_dict = {'ssids': ssids, 'count' : count, 'is_superuser':is_superuser,'name':name}
	return render(request, 'beam/ssids.html', context_dict)

