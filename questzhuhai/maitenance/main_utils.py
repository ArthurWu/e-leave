import sys, os
from django.db import transaction
from models import *
from leave.models import *
from common.logger import log
import common.ad_utils as ad_utils
from common import report
from datetime import datetime, date, time
import resource
import settings
from common.logger import log

MONTH = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

def leave_report(year):
	res = []
	for i in range(1, 13):
		report_date_10 = datetime(year, i, settings.LEAVE_REPORT_FIRST_DAY)
		report_date_25 = datetime(year, i, settings.LEAVE_REPORT_SECEND_DAY)
		leave_record_satrt_date = report.get_lastest_month_period(report_date_25)
		
		report_full_path_10 = settings.REPORT_FILES + r"leavereport-%s.xls" % report_date_10.strftime('%Y-%m-%d')
		report_full_path_25 = settings.REPORT_FILES + r"leavereport-%s.xls" % report_date_25.strftime('%Y-%m-%d')
		leave_record_file_name = r"leaverecordreport-%s-%s.xls" % \
							  (leave_record_satrt_date.strftime('%Y_%m_%d'), report_date_25.strftime('%Y_%m_%d'))
		leave_record_full_path_25 = settings.REPORT_FILES + leave_record_file_name
		
		file_exist_10 = os.path.exists(report_full_path_10)
		file_exist_25 = os.path.exists(report_full_path_25)
		leave_record_file_exist_25 = os.path.exists(leave_record_full_path_25)
		#data_exist = AnnualLeaveReport.objects.filter(report_date = report_date_10)
		
		item = {
			'download_link': [],
			'generate_link': [],
		}
		if file_exist_10:
			item['download_link'].append({'link': '/main/reports/download/leavereport/%s' % report_date_10.strftime('%Y/%m/%d/'), 'actual_on': report_date_10})
		else:
			item['generate_link'].append({'link':'/main/reports/generate?type=leavereport&year=%s&month=%s&day=%s' %
				(report_date_10.year, report_date_10.month, report_date_10.day), 'actual_on': report_date_10})
		
		if file_exist_25:
			item['download_link'].append({'link': '/main/reports/download/leavereport/%s' % report_date_25.strftime('%Y/%m/%d/'), 'actual_on': report_date_25})
		else:
			item['generate_link'].append({'link':'/main/reports/generate?type=leavereport&year=%s&month=%s&day=%s' %
				(report_date_25.year, report_date_25.month, report_date_25.day), 'actual_on': report_date_25})
		
		if leave_record_file_exist_25:
			item['download_link'].append({
				'link': '/main/reports/download/leaverecord/%s/%s/' % (leave_record_satrt_date.strftime('%Y_%m_%d'), report_date_25.strftime('%Y_%m_%d')),
				'actual_on': report_date_25,
				'type': 'leave record'
			})
		else:
			item['generate_link'].append({
				'link':'/main/reports/generate?type=leaverecord&start=%s&end=%s&year=%s' %
				(leave_record_satrt_date.strftime('%Y-%m-%d'), report_date_25.strftime('%Y-%m-%d'), report_date_25.year),
				'actual_on': report_date_25,
				'type': 'leave record'
			})
			
		res.append({MONTH[i-1]: item})
		
	years = []
	cur_year = date.today().year
	for y in range(2005, cur_year+1):
		if LeaveRequest.objects.filter(create_date__year=y).count()>0:
			selected = False
			if y == year:
				selected = True
			years.append((y, selected))
	
	years.reverse()
	return res, years

def generate_reports(report_type, year, month , day=settings.LEAVE_REPORT_FIRST_DAY, start_date=None, end_date=None):
	employee_set = Employee.objects.all()
	
	if report_type == 'leavereport':
		report.generate_leave_report_file(employee_set, day, month, year)
	if report_type == 'leaverecord':
		report.generate_leave_record_report_file(employee_set, start_date, end_date)

def download_report(filename):
	log.Debug(filename)
	try:
		file = open(settings.REPORT_FILES + '/' + filename, 'rb')
		from django.http import HttpResponse
		response = HttpResponse(file.read(), mimetype='text/xls')
		file.close()
		response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
		return response
	except Exception, ex: 	
		log.Except(ex)
	
	from django.http import Http404
	raise Http404

@transaction.commit_on_success
def add_maitenance_log(who, operation):
	MaintenanceLog(who=who, operation=operation).save()
	
@transaction.commit_manually
def add_object(objType, data):
	error = ''
	obj = objType()
	def setobjattr(k):
		if type(data[k]) == dict:
			for rk in data[k].keys():
				robj = rk.objects.get(id=data[k][rk])
				setattr(obj, k, robj)
		else:
			setattr(obj, k, data[k])

	try:	
		map(setobjattr, data.keys())
		obj.save()
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_add_object % objType.__name__
		obj = None
		transaction.rollback()
	else:
		transaction.commit()
		
	return {"error":error, "data":obj}
	
@transaction.commit_manually
def delete_object(objType, id):
	error = ''
	obj = None
	try:
		obj = objType.objects.get(id=id)
		obj.delete()
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_delete_object % objType.__name__
		transaction.rollback()
	else:
		transaction.commit()
	return {'error': error, 'data' : obj}
	
#######################Administrators Maintenance Methods##################

def get_all_admins():
	error = ''
	admins = None
	try:
		admins = Admin.objects.all()
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_get_object % Admin.__name__
		admins = None
	return {'error':error, 'data': admins}

def add_admin(name, operator):
	user, sid = ad_utils.GetADObject(name)
	if sid:
		res	= add_object(Admin,{"sid":sid,'name':name})
		if not res['error']: add_maitenance_log(operator, 'added %s as Administrator' % user.DisplayName)
		return res
	else:
		return {'error': resource.user_not_exist % name, 'data': None}

def delete_admin(id, operator):
	res = delete_object(Admin, id)
	if not res['error']: add_maitenance_log(operator, 'deleted %s' % res['data'].name)
	return res
	
	
#######################Leave Types Maintenance Methods##################

def get_all_leave_types():
	error = ''
	leaveTypes = None
	try:
		leaveTypes = LeaveType.objects.all()
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_get_object % LeaveType.__name__
		leaveTypes = None
	return {'error':error, 'data': leaveTypes}
	
def add_leave_type(name, operator):
	res = add_object(LeaveType,{'name':name})
	if not res['error']: add_maitenance_log(operator, 'added a new Leave Type %s ' % name)
	return res
	
@transaction.commit_manually
def update_leave_type(id, notifyAdmin, operator):
	error = ''
	leaveType = None
	try:
		leaveType = LeaveType.objects.get(id=id)
		leaveType.notifyadmin = notifyAdmin
		leaveType.save()
		add_maitenance_log(operator, 'made Leave Type %s %s notify admin' % (leaveType.name , '' if notifyAdmin else 'not'))
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_update_object % LeaveType.__name__
		leaveType = None
		transaction.rollback()
	else:
		transaction.commit()
		
	return {'error': error, 'data': leaveType}
	
def delete_leave_type(id, operator):
	res = delete_object(LeaveType, id)
	if not res['error']: add_maitenance_log(operator, 'deleted Leave Type %s' % res['data'].name)
	return res
	
#######################Departments & Team Maintenance Methods##################

def get_all_departments():
	error = ''
	dep = None
	try:
		dep = Department.objects.all()
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_get_object % Department.__name__
		dep = None
	return {'error':error, 'data': dep}
	
def add_department(name, operator):
	res = add_object(Department,{'name':name})
	if not res['error']: add_maitenance_log(operator, 'added a new Department %s ' % name)
	return res
	

def delete_department(id, operator):
	res = delete_object(Department, id)
	if not res['error']: add_maitenance_log(operator, 'deleted department %s' % res['data'].name)
	return res
	
def get_teams_by_department(depid):
	error = ''
	team = None
	try:
		dep = Department.objects.get(id=depid)
		team = Team.objects.filter(department=dep)
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_get_object % Team.__name__
		team = None
	return {'error':error, 'data': team}
	
def add_team(depid, name, operator):
	res = add_object(Team,{'name':name,'department':{Department: depid}})
	if not res['error']: add_maitenance_log(operator, 'added a new Team %s ' % name)
	return res

def delete_team(id, operator):
	res = delete_object(Team, id)
	if not res['error']: add_maitenance_log(operator, 'deleted team %s' % res['data'].name)
	return res

#######################Employee Branch Maintenance Methods##################
def add_employee(domain_id, chinese_name, department, team, join_date, start_fiscal_date, balanced_forward, al_entitlement, sl_entitlement, approvers, cc_to, isadmin, is_active, balanced_days, errors):	

	def create_employee(cc_to):
		try:
			jd = datetime(*join_date)
			sfd = datetime(*start_fiscal_date)
		except ValueError:
			try:
				jd = datetime.strptime(join_date, "%d/%m/%Y")
				sfd = datetime.strptime(start_fiscal_date, "%d/%m/%Y")
			except:
				errors[domain_id] = resource.log_prefix + "the date format is not match to 'day/month/year' or 'year/month/day'"
				return
		

		deps = Department.objects.filter(name=department)
		if not deps and department.strip():
			dep = Department(name=department)
			dep.save()
		else:
			dep = deps and deps[0] or None
		
		teams = Team.objects.filter(department=dep, name=team)
		if not teams and team.strip():
			myteam = Team(department=dep, name=team)
			myteam.save()
		else:
			myteam = teams and teams[0] or None
		
		if cc_to.strip():
			cc_to = cc_to.rstrip(';')+';'
		emp = Employee(sid=sid, domain_id=domain_id, chinese_name=chinese_name,
					display_name=display_name,
					title=title, email=email, department=dep,
					team=myteam, join_date=jd, start_fiscal_date=sfd,
					balanced_forward=balanced_forward, al_entitlement=al_entitlement,
					sl_entitlement=sl_entitlement, balanced_days=balanced_days,
					approvers=approvers.strip(';')+';',
					cc_to=cc_to, 
					is_administrative_staff=isadmin, 
					is_active=is_active)
		log.Info(emp.__dict__)
		emp.save()
	
	exist_emp = Employee.objects.filter(domain_id=domain_id)
	if not exist_emp:
		user, sid = ad_utils.GetADObject(domain_id)
		log.Info('sid================:' + str(sid))
		
		if user:
			display_name=user.DisplayName
			title = user.Title or ''
			email=user.mail or ''
		else:
			display_name = title = email = ''
		
		if sid:
			try:
				create_employee(cc_to)
			except:
				log.Info(resource.log_prefix + sys.exc_info()[1].__str__())
				if errors.has_key(domain_id):
					errors[domain_id] += ', ' + resource.log_prefix + sys.exc_info()[1].__str__()
				else:
					errors[domain_id] = resource.log_prefix + sys.exc_info()[1].__str__()
		elif settings.DEBUG:
			# create test employee which does not in the domain
			sid = ''
			create_employee(cc_to)
		else:
			errors[domain_id] = resource.user_not_exist % domain_id
	else:
		log.Info("=======Warring======= %s has exist." % domain_id)

@transaction.commit_manually		
def add_employees(filename, operator):
	from xlrd import open_workbook, xldate_as_tuple
	import settings
	book = open_workbook(settings.UPLOADDIR + filename)
	sheet = book.sheet_by_index(0)
	errors = {}
	try:
		for row_index in range(1,sheet.nrows):
			try:
				join_date = xldate_as_tuple(sheet.cell(row_index,4).value, 0)
				start_fiscal_date = xldate_as_tuple(sheet.cell(row_index,5).value, 0)
			except:
				join_date = sheet.cell(row_index,4).value
				start_fiscal_date = sheet.cell(row_index,5).value

			res = add_employee(
				sheet.cell(row_index,0).value,
				sheet.cell(row_index,1).value,
				sheet.cell(row_index,2).value,
				sheet.cell(row_index,3).value,
				join_date,
				start_fiscal_date,
				sheet.cell(row_index,6).value,
				sheet.cell(row_index,7).value,
				sheet.cell(row_index,8).value,
				sheet.cell(row_index,9).value,
				sheet.cell(row_index,10).value,
				sheet.cell(row_index,11).value,
				sheet.cell(row_index,12).value,
				sheet.cell(row_index,13).value,
				errors)
		
		if errors:
			raise ErrorInAddEmployee("Employee Error: Can't create an employee infomation.")
		add_maitenance_log(operator, 'imported employees ')	
	except:
		log.Info(sys.exc_info()[1].__str__())
		log.Except(sys.exc_info()[1].__str__())
		errors['ERROR'] = resource.failed_to_add_object % Employee.__name__
		transaction.rollback()
	else:
		transaction.commit()

	return errors
	
class ErrorInAddEmployee(Exception):
	pass
	
def handle_uploaded_file(file):
	import settings
	log.Info(settings.UPLOADDIR + 'employees.xls')
	destination = open(settings.UPLOADDIR + 'employees.xls', 'wb+')
	for chunk in file.chunks():
		destination.write(chunk)
	destination.close()

def get_all_maitenancelogs():
	error = ''
	actions = None
	try:
		actions = MaintenanceLog.objects.all().order_by('-when')
	except:
		log.Except(resource.log_prefix + sys.exc_info()[1].__str__())
		error = resource.failed_to_get_object % MaintenanceLog.__name__
		actions = None
	return {'error':error, 'data': actions}
	
from django.db.models.signals import post_save
from django.dispatch import receiver
def add_action_log(sender, **kwargs):
	pass