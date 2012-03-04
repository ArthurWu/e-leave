from django.db import models
import leave.processe.status as status
from maitenance.models import Employee

class LeaveType(models.Model):
	name = models.CharField(max_length=128, unique=True)
	notifyadmin = models.BooleanField(default = False)
	max_days = models.IntegerField(default=0, blank=True, null=True)
	build_in = models.BooleanField(default = False)
	
	def __unicode__(self):
		return self.name
	
class LeaveRequestManager(models.Manager):
	def by_employee(self, emp):
		return self.filter(employee=emp).order_by('-create_date')
		
	def by_approver(self, emp):
		s = emp.domain_id.replace(r'\\', r'\\\\')
		return self.filter(employee__approvers__icontains=s).order_by('-create_date')

class LeaveRequest(models.Model):
	employee = models.ForeignKey(Employee)
	status = models.CharField(max_length=50, default=status.INITIAL)
	leave_type = models.ForeignKey(LeaveType)
	days = models.FloatField(default=0)
	create_date = models.DateTimeField(auto_now_add=True)
	comments = models.CharField(max_length=500, blank=True, null=True)
	objects = LeaveRequestManager()
	
	def __unicode__(self):
		return '%s-%s-%s' % (self.employee.display_name, self.leave_type.name, self.status)
		
	def get_absolute_url(self):
		return '/leave/leaverequests/%i/' % self.id
	
	def manager_shortcut_actions(self):
		actions = []
		if self.status in (status.PENDINGMANAGER):#, status.WAITINGADMINCONFIRM):
			actions.append(('Approve', '/leave/leaverequest/approve/%i/' % self.id))
			#('Reject', '/leave/leaverequest/reject/%i/' % self.id),
		return actions
	
	def started(self):
		periods = self.period_set.all()
		if len(periods) > 0:
			for period in periods:
				if period.have_started():
					return True
		return False
	
	def is_approved(self):
		return self.status in (status.PENDINGADMIN, status.ARCHIVED)
	
class Period(models.Model):
	leave_request = models.ForeignKey(LeaveRequest)
	start = models.DateTimeField()
	end = models.DateTimeField()
	
	def __unicode__(self):
		return '%s  ~  %s' % (self.start.strftime('%Y-%m-%d %p'), self.end.strftime('%Y-%m-%d %p'))
			
	def have_started(self):
		import datetime
		return datetime.datetime.now() > self.start
	
class LeaveRequestProcesses(models.Model):
	leave_request = models.ForeignKey(LeaveRequest)
	who = models.CharField(max_length=30)
	do = models.CharField(max_length=30)
	at = models.DateTimeField(auto_now=True)
	reason = models.TextField(blank=True, null=True)