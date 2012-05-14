from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render_to_response, redirect
from django.template.loader import get_template
from django.template import Context, RequestContext
import main_utils
import common.utils as utils
from common.logger import log
import simplejson as json
import settings

def admin_require(view_func):
	def is_admin(request, *args, **kwargs):
		if not request.employee.is_administrative_staff:
			return render_to_response('auth_error.html', RequestContext(request, {}))
		return view_func(request, *args, **kwargs)
	return is_admin

@admin_require
def reports(request):
	from datetime import date
	year = int(request.GET.get('year', date.today().year))
	
	year_reports, years = main_utils.leave_report(year)
	
	return render_to_response('maitenance/report.html', RequestContext(request, {'reports': year_reports, 'years': years, 'nav': 'reports'}))
	
@admin_require
def generate_report(request):
	from datetime import date, datetime
	today = date.today()
	start_date = end_date = None
	
	report_type = request.GET.get('type', 'leavereport')
	if report_type == 'leavereport':
		year = request.GET.get('year', today.year)
		month = request.GET.get('month', today.month)
		
		day = request.GET.get('day', settings.LEAVE_REPORT_FIRST_DAY)
		start_date = datetime(int(year), 1, 1)
		end_date = datetime(int(year), int(month), int(day))
		main_utils.generate_reports(report_type, int(year), int(month), int(day))
		
		subject = "Monthly leave report %s" % end_date.strftime('%Y-%m-%d')
		type = 'leave report'
		
	if report_type == 'leaverecord':
		start = request.GET.get('start')
		end = request.GET.get('end')
		
		start_date = datetime.strptime(start, "%Y-%m-%d")
		end_date = datetime.strptime(end + ' 17:30', "%Y-%m-%d %H:%M")
		main_utils.generate_reports(report_type, year = today.year, month = today.month, start_date = start_date, end_date = end_date)
	
		subject = "Monthly leave record report(%s~%s)" % (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
		type = 'leave record'
		
	from common.utils import send_email_to_admin
	send_email_to_admin('report_notification.txt', subject, end_date, start_date, type)
	
	return redirect('/eleave/main/reports/')

@admin_require
def download_report(request, report_type, year, month, day):
	filename = '%s-%s-%s-%s.xls' % (report_type, year, month, day)
	if request.GET.get('export', 0): filename = 'export_' + filename
	return main_utils.download_report(filename)
	
@admin_require
def download_leave_record_report(request, report_type, start_date, end_date):
	filename = 'leaverecordreport-%s-%s.xls' % (start_date, end_date)
	if request.GET.get('export', 0): filename = 'export_' + filename
	return main_utils.download_report(filename)

@admin_require
def index(request):
	return render_to_response('maitenance/index.html', RequestContext(request,{}))

@admin_require
def maitenance(request):
	admins = main_utils.get_all_admins()
	leavetypes = main_utils.get_all_leave_types()
	departments = main_utils.get_all_departments()
	cycle = utils.read(utils.resfile(), 'Default', 'email.alert.cycle')
	return render_to_response('maitenance/maitenance.html',RequestContext(request, {
		'admins': admins, 
		'leavetypes': leavetypes,
		'departments': departments,
		'nav': 'settings',
		'cycle': cycle})
	)
	
@admin_require
def setcycle(request):
	if request.method == 'POST':
		cycle = request.POST.get('cycle')
		utils.write(utils.resfile(), 'Default', 'email.alert.cycle', cycle)
	return redirect('/eleave/main/settings')
	
@admin_require
def action_logs(request):
	actions = main_utils.get_all_maitenancelogs()
	return render_to_response('maitenance/action_logs.html',
							  RequestContext(request, {'actions': actions, 'nav': 'action_logs'}))

def add_object(request, model):
	pass

#######################Administrators Maintenance Interfaces##################	
@admin_require
@never_cache
def add_admin(request):
	domain_id = request.GET.get('name', '').lower()
	current_user = request.META['REMOTE_USER']
	res = main_utils.add_admin(domain_id, current_user)
	row_html = ''
	if res['data']:
		row_html = rend_row(Context({'admin': res['data']}), 'maitenance/row_admin.html')
	return HttpResponse(json.dumps({'error': res['error'], 'html': row_html, 'data': res['data'].sid if res['data'] else ''}))
	
def rend_row(data, template_name):
	template = get_template(template_name)
	return template.render(data)
	
@admin_require
@never_cache
def delete_admin(request):
	domain_id = request.GET.get('name', '').lower()
	current_user = request.META['REMOTE_USER']
	res = main_utils.delete_admin(domain_id, current_user)
	
	return HttpResponse(json.dumps({'error': res['error']}))

#######################Leave Type Maintenance Interfaces##################	

@admin_require
@never_cache
def add_leave_type(request):
	name = request.GET.get('name', '')
	current_user = request.META['REMOTE_USER']
	res = main_utils.add_leave_type(name, current_user)
	row_html = ''
	if res['data']:
		row_html = rend_row(Context({'leavetype': res['data']}), 'maitenance/row_leavetype.html')
	return HttpResponse(json.dumps({'error': res['error'], 'html': row_html, 'data': res['data'].id if res['data'] else ''}))
	
@admin_require
@never_cache
def delete_leave_type(request):
	leavetype_id = request.GET.get('id', '').lower()
	current_user = request.META['REMOTE_USER']
	res = main_utils.delete_leave_type(leavetype_id, current_user)
	
	return HttpResponse(json.dumps({'error': res['error']}))

def set_notify_admin(request):
	id = request.GET.get('id', '')
	notify_admin_str = request.GET.get('notify_admin', 'false')
	notify_admin = True if notify_admin_str == 'true' else False
	current_user = request.META['REMOTE_USER']
	
	res = main_utils.update_leave_type(id, notify_admin, current_user)
	
	return HttpResponse(json.dumps({'error': res['error']}))

@admin_require
@never_cache
def deps_and_teams(request):
	departments = main_utils.get_all_departments()
	return render_to_response('maitenance/department.html', {
		'departments': departments
	})
	
@admin_require
def add_department_view(request):
	from forms import DepartmentForm
	form = None
	if request.method == 'POST':
		form = DepartmentForm(request.POST)
		if form.is_valid():
			form.save()
	else:
		form = DepartmentForm()
		
	deps = main_utils.get_all_departments()
	
	from django.template import RequestContext

	return render_to_response('maitenance/department.html', RequestContext(request, {'form': form, 'deps': deps}))

@admin_require
@never_cache
def add_department(request):
	name = request.GET.get('name', '')
	current_user = request.META['REMOTE_USER']
	res = main_utils.add_department(name, current_user)
	row_html = ''
	if res['data']:
		row_html = rend_row(Context({'dep': res['data']}), 'maitenance/row_dep.html')
	return HttpResponse(json.dumps({'error': res['error'], 'html': row_html, 'data': res['data'].id if res['data'] else ''}))

@admin_require
@never_cache	
def delete_department(request):
	dep_id = request.GET.get('id', '')
	current_user = request.META['REMOTE_USER']
	res = main_utils.delete_department(dep_id, current_user)
	
	return HttpResponse(json.dumps({'error': res['error']}))

@admin_require
@never_cache
def add_team(request):
	dep_id = request.GET.get('dep_id', '')
	name = request.GET.get('name', '')
	current_user = request.META['REMOTE_USER']
	res = main_utils.add_team(dep_id, name, current_user)
	row_html = ''
	if res['data']:
		row_html = rend_row(Context({'team': res['data']}), 'maitenance/row_team.html')
	return HttpResponse(json.dumps({'error': res['error'], 'html': row_html, 'data': res['data'].id if res['data'] else ''}))
	
@admin_require
@never_cache	
def delete_team(request):
	id = request.GET.get('id', '')
	current_user = request.META['REMOTE_USER']
	res = main_utils.delete_team(id, current_user)
	
	return HttpResponse(json.dumps({'error': res['error']}))
	
@admin_require
def get_teams_by_department(request):
	dep_id =  request.GET.get('dep_id', '')
	res = main_utils.get_teams_by_department(int(dep_id))
	html = '<option value="" selected="selected">---------</option>'
	if res['error'] == '' and res['data']:
		for team in res['data']:
			html += '<option value="%d">%s</option>' % (team.id, team.name)
			
	return HttpResponse(json.dumps({'error': res['error'], 'html': html}))
	

from django import forms

class UploadFileForm(forms.Form):
	title = forms.CharField(max_length=150)
	file  = forms.FileField()

from django.shortcuts import redirect
@admin_require
def import_employees(request):
	error = ''
	res = {}
	current_user = request.META['REMOTE_USER']
	
	if request.method == 'POST':
		try:
			form = forms.Form(request.POST, request.FILES)
			if form.is_valid():
				file = request.FILES['file']
				main_utils.handle_uploaded_file(file)
				res = main_utils.add_employees('employees.xls', current_user)
		except BaseException,e:
			import sys
			log.Except(sys.exc_info()[1].__str__())
			error = 'Internal error while importing the employees info.'
		if error:
			res['ERROR'] = error
	return render_to_response('maitenance/employees_import_result.html', RequestContext(request, {'errors': res, 'nav': 'employees'}))