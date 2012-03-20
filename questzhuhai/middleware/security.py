import win32com, win32com.client, pythoncom
import win32security
from django.contrib.auth.models import User
from maitenance.models import Employee
from django.shortcuts import render_to_response
from common.logger import log

class RequestHandlerMiddleware(object):
	def process_request(self, request):
		return self.make_auth(request)
	
	def make_auth(self, request):
		self.set_admin_or_default(request)
		emp = self.set_employee(request)
		if not emp:
			return render_to_response("user_not_exist.html")
		
	def set_employee(self, request):
		current_user = request.META['REMOTE_USER']
		emp = Employee.objects.filter(domain_id=current_user)
		if len(emp) > 0:
			request.employee = emp[0]
			from datetime import datetime
			log.Info('Employee %s open url %s at: %s' % (request.employee.display_name, request.META['PATH_INFO'], datetime.now().isoformat()))
		else:
			request.employee = None
			
		return request.employee
	
	def set_admin_or_default(self, request):
		#log.Info('Set current user as admin, if admin not exist, then create default admin infomation.')
		user = User.objects.filter(username = 'admin')
		if not user:
			user = User.objects.create_superuser(username='admin', email='admin@admin.com', password='1')
		else:
			user = user[0]
		#log.Info('Current User: %s' % user.username)
		request.user = user
		
		
	def get_ADObject_by_principal(self, principal):
		try:	
			sid, domain, type = win32security.LookupAccountName('', principal)
			user = win32com.client.GetObject("LDAP://%s/<SID=%s>" % (domain, str(sid)[6:]))
			return user
		except BaseException, e:
			log.Debug("GetADDisplayName; Unable to resolve display name. Error: %s"%str(e))
			return 0