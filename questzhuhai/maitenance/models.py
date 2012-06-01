from django.db import models
import datetime
from leave import processe

class Admin(models.Model):
	sid = models.CharField(max_length=512, editable=False, unique=True)
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
	
class MaintenanceLog(models.Model):
	when = models.DateTimeField(auto_now=True)
	who = models.CharField(max_length=50)
	operation = models.CharField(max_length=512)
	
	
class Department(models.Model):
	name = models.CharField(max_length=512, unique=True)
	supervisor = models.CharField(max_length=256, blank=True)
	
	def __unicode__(self):
		return self.name

class Team(models.Model):
	department = models.ForeignKey(Department)
	name = models.CharField(max_length=512, unique=True)
	leader = models.CharField(max_length=50, blank=True)
	
	def __unicode__(self):
		return self.name

class Employee(models.Model):
	sid = models.CharField(max_length=512, editable=False, unique=True)
	domain_id = models.CharField(max_length=50, help_text="Employee's domain id (prod\\awu1)")
	display_name = models.CharField(max_length=128)
	chinese_name = models.CharField(max_length=20, blank=True)
	title = models.CharField(max_length=256)
	email = models.EmailField(max_length=75)
	department = models.ForeignKey(Department, related_name="employees", blank=True, null=True, on_delete=models.SET_NULL)
	team = models.ForeignKey(Team, related_name="team_members",  blank=True, null=True, on_delete=models.SET_NULL, help_text="All teams include in the department which you selected above.")
	join_date = models.DateField(help_text='The date when the employee joined Quest')
	start_fiscal_date = models.DateField(help_text="The start date that used for calculating employee's annual leave for the current year. For example, employee A joined quest on 22/04/2011, his/her StartFiscalDate of 2011 is 22/04/2011; Employee B joined quest on 15/12/2010, his/her StartFiscalDate of 2011 is 01/01/2011.")
	balanced_forward = models.FloatField(default=0, help_text='Days of annual leave that the employee remains from last year (should be less than 5 days and will be cleared at the middle of the calendar year).')
	al_entitlement = models.FloatField(verbose_name=r'A/L', help_text='Days that the employee could have annual leave for each calendar year. ')
	sl_entitlement = models.FloatField(verbose_name=r'S/L', help_text='Days that the employee could have sick leave for each calendar year. ')
	approvers = models.CharField(max_length=256,
		help_text="The persons who can approve/reject the employee's leave requests (prod\\rgong;prod\\awu1;).\n\
			Use ; to separate and end with ;")
	cc_to = models.CharField(max_length=512, blank=True, null=True,
		help_text='Use semicolon to separate all the carbon copy Employees.\n\
			Use ; to separate and end with ;')
	is_administrative_staff = models.BooleanField(verbose_name="Admin", default = False, help_text='Whether the employee is an administrative stuff.')
	is_active =  models.BooleanField(default = True, help_text='Whether the employee still work for quest or not.')
	last_login_date = models.DateTimeField(default=datetime.datetime.now, editable=False)
	balanced_days = models.FloatField(default=0, help_text='Days of annual leave with no paid that have been archived by administrative stuff.')

	def __unicode__(self):
		return self.display_name
		
	class Meta:
		app_label = 'maitenance'
		verbose_name = 'Employee'
		verbose_name_plural = 'Employees'
	
	@property
	def is_admin(self):
		return self.is_administrative_staff 
	
	def is_approver_of(self, leaverequest):
		if self.domain_id.lower() in leaverequest.employee.approvers.lower():
			return True
		else:
			return False
	
	def is_approver(self):
		res = Employee.objects.filter(approvers__icontains = self.domain_id.strip(';')+';')
		return len(res) > 0
		
	def is_mine(self, leaverequest):
		if self.sid == leaverequest.employee.sid:
			return True
		else:
			return False
		
	def get_approvers(self):
		approvers = self.approvers.strip().strip(';').replace(r'\\', r'\\\\').split(';')
		return Employee.objects.filter(domain_id__in=approvers)
	
	def approvers_email(self):
		return [a.email for a in self.get_approvers()]
	
	def cc_to_email(self):
		cc = self.cc_to.strip().strip(';').replace(r'\\', r'\\\\').split(';')
		cc_to = Employee.objects.filter(domain_id__in=cc)
		emails = [c.email for c in cc_to]
		return emails
	
	def days_available(self):
		from leave.models import LeaveType
		leavetypes = LeaveType.objects.all()
		
		available_days = {}
		for leavetype in leavetypes:
			used_days, need_approval = self.get_used_leave_days(leavetype)
			leave_adjustment_days = self.get_leave_adjustment_days(leavetype.name)
			
			if leavetype.name == 'Annual Leave':
				usable_annual_leave_days = self.get_annual_leave_days()
				from decimal import Decimal
				
				total_annual_leave_days = usable_annual_leave_days + \
												self.balanced_forward + \
												self.balanced_days + \
												leave_adjustment_days
				
				ad = total_annual_leave_days - used_days - need_approval

				available_days[leavetype.name.lower().replace(' ', '_')] = {
					'total_days': total_annual_leave_days,
					'used_days': used_days,
					'need_approval': need_approval,
					'available_days': ad if ad > 0 else 0
				}
			elif leavetype.name == 'Sick Leave':
				usable_sick_leave_days = self.get_sick_leave_days() + leave_adjustment_days
				
				available_days[leavetype.name.lower().replace(' ', '_')] = {
					'total_days': usable_sick_leave_days,
					'used_days': used_days,
					'need_approval': need_approval,
					'available_days': usable_sick_leave_days - used_days - need_approval
				}
			elif leavetype.name == 'Marriage Leave':
				marriage_leave_days = leavetype.max_days
				expire_date = None
				
				mlc = self.marriageleaveconfirm_set.all()
				if mlc:
					marriage_leave_days = mlc[0].days + leave_adjustment_days
					expire_date = mlc[0].expire_date	
				
				available_days[leavetype.name.lower().replace(' ', '_')] = {
					'total_days': marriage_leave_days,
					'used_days': used_days,
					'need_approval': need_approval,
					'available_days': marriage_leave_days - used_days - need_approval,
					'expire_date': expire_date
				}
				
			else:
				tol_days = leavetype.max_days + leave_adjustment_days
				available_days[leavetype.name.lower().replace(' ', '_')] = {
					'total_days': tol_days,
					'used_days': used_days,
					'need_approval': need_approval,
					'available_days': tol_days - used_days - need_approval
				}
				
		return available_days
	
	def get_sick_leave_days(self):
		days_to = self._total_days_to_next_settlement()
		return days_to/365*self.sl_entitlement

	def _total_days_to_next_settlement(self):
		import datetime, settings
		today = datetime.date.today()
		
		# account_day = datetime.date(today.year, today.month, settings.LEAVE_REPORT_FIRST_DAY)
		# if today > account_day:
			# account_day = datetime.date(today.year, today.month+1, settings.LEAVE_REPORT_FIRST_DAY)
		
		try:
			sfd = self.start_fiscal_date.date()
		except:
			sfd = self.start_fiscal_date
		
		first_day_of_this_year = datetime.date(today.year, 1, 1)
		if sfd < first_day_of_this_year:
			sfd = first_day_of_this_year
			
		days_to = float((today - sfd).days) + 1
		return days_to
	
	def get_annual_leave_days(self):
		days_to_now = self._total_days_to_next_settlement()
		return days_to_now/365*self.al_entitlement
		
	def get_used_leave_days(self, leavetype):		
		from leave.models import LeaveRequest
		from django.db.models import Q
		lrs = LeaveRequest.objects.filter(
			(Q(period__start__year = datetime.datetime.now().year) | \
			Q(period__end__year = datetime.datetime.now().year))&
			Q(employee__id = self.id)&
			Q(leave_type__id = leavetype.id)
		).distinct()

		used_days = need_approval = 0.0
		for l in lrs:
			if l.status in (processe.status.PENDINGADMIN, processe.status.ARCHIVED):
				used_days += l.days
			elif l.status in (processe.status.PENDINGMANAGER, processe.status.WAITINGADMINCONFIRM):
				need_approval += l.days
		return used_days, need_approval
	
	def get_leave_adjustment_days(self, leavetype):
		return sum([a.adjustment_days for a in self.adjustmentdays_set.all() if a.leave_type.name == leavetype])
	
	def send_approve_alert_email(self, lr):
		template = 'maitenance/email/alert_email.txt'
		subject = "Please handle my leave request"
		receiver = lr.employee.email
		
		import settings
		host = settings.LEAVESYSTEMHOST or ''
		
		from common.utils import send_mail
		send_mail(template = template,
				sender = self.email,
				receivers = [receiver],
				context = {'host': host, 'leave_request': lr, 'receiver': lr.employee.display_name, 'sender': self.display_name},
				subject = subject,
				cc = [])

CURRENT_YEAR = str(datetime.datetime.now().year)
MONTH_CHOICES = (
	(CURRENT_YEAR+'-1',  'Jan, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-2',  'Feb, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-3',  'Mar, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-4',  'Apr, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-5',  'May, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-6',  'Jun, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-7',  'Jul, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-8',  'Aug, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-9',  'Sep, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-10', 'Oct, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-11', 'Nov, '+CURRENT_YEAR),
	(CURRENT_YEAR+'-12', 'Dec, '+CURRENT_YEAR)
)
try:
	from leave.models import LeaveType
except:
	LeaveType = 'LeaveType'
	
class AdjustmentDays(models.Model):
	employee = models.ForeignKey(Employee)
	leave_type = models.ForeignKey(LeaveType, blank=True, null=True)
	month = models.CharField(max_length=10, choices=MONTH_CHOICES)
	adjustment_days = models.FloatField('Deduction')
	expire_date = models.DateField(blank=True, null=True)
	comment = models.CharField(max_length = 500, blank=True)
	create_date = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return '%s adjustment' % self.month
	
	class Meta:
		app_label = 'maitenance'
		verbose_name = 'Adjustment Day'
		verbose_name_plural = 'Adjustment Days'
		
class AdjustmentDaysHistory(models.Model):
	employee = models.ForeignKey(Employee)
	leave_type = models.ForeignKey(LeaveType, blank=True, null=True)
	month = models.CharField(max_length=10, choices=MONTH_CHOICES)
	adjustment_days = models.FloatField('Deduction')
	expire_date = models.DateField(blank=True, null=True)
	comment = models.CharField(max_length = 500, blank=True)
	create_date = models.DateTimeField()
	
	def __unicode__(self):
		return '%s adjustment' % self.month
	
	class Meta:
		app_label = 'maitenance'
		verbose_name = 'Adjustment Day History'
		verbose_name_plural = 'Adjustment Day History'

		
class MarriageLeaveConfirm(models.Model):
	employee = models.ForeignKey(Employee)
	days = models.FloatField('Marriage Leave Days')
	marrige_date = models.DateField(blank=True, null=True, verbose_name="Date of Marriage")
	expire_date = models.DateField()
	
	def __unicode__(self):
		return ''
	
	class Meta:
		app_label = 'maitenance'
		verbose_name = 'Marrige Leave Confirm'
		verbose_name_plural = 'Marrige Leave Confirm'
		
class AnnualLeaveReport(models.Model):
	employee = models.ForeignKey(Employee)
	working_days = models.FloatField()
	al_entitlement_of = models.FloatField(default=0.0)
	total_entitled_as_of = models.FloatField(default=0.0)
	report_date = models.DateTimeField()
	jan_taken = models.FloatField(null=True)
	feb_taken = models.FloatField(null=True)
	mar_taken = models.FloatField(null=True)
	apr_taken = models.FloatField(null=True)
	may_taken = models.FloatField(null=True)
	jun_taken = models.FloatField(null=True)
	jul_taken = models.FloatField(null=True)
	aug_taken = models.FloatField(null=True)
	sep_taken = models.FloatField(null=True)
	oct_taken = models.FloatField(null=True)
	nov_taken = models.FloatField(null=True)
	dec_taken = models.FloatField(null=True)
	taken_in_this_year = models.FloatField(default=0.0)
	jan_deduction = models.FloatField(null=True)
	feb_deduction = models.FloatField(null=True)
	mar_deduction = models.FloatField(null=True)
	apr_deduction = models.FloatField(null=True)
	may_deduction = models.FloatField(null=True)
	jun_deduction = models.FloatField(null=True)
	jul_deduction = models.FloatField(null=True)
	aug_deduction = models.FloatField(null=True)
	sep_deduction = models.FloatField(null=True)
	oct_deduction = models.FloatField(null=True)
	nov_deduction = models.FloatField(null=True)
	dec_deduction = models.FloatField(null=True)
	available_annual_leave_unclaimed = models.FloatField(default=0.0)
	application_comp_leave = models.FloatField(null=True)
	taken_comp_leave = models.FloatField(null=True)
	balance_of_comp_leave = models.FloatField(null=True)
	marrige_leave_balance = models.FloatField(null=True)
	create_date = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return '%s | Annual Leave Summary Report for the year of %s' % (self.employee.display_name, str(self.report_date.year))

class SickLeaveReport(models.Model):
	employee = models.ForeignKey(Employee)
	working_days = models.FloatField()
	sl_entitlement_of = models.FloatField(default=0.0)
	total_entitled_as_of = models.FloatField(default=0.0)
	report_date = models.DateTimeField()
	jan_taken = models.FloatField(null=True)
	feb_taken = models.FloatField(null=True)
	mar_taken = models.FloatField(null=True)
	apr_taken = models.FloatField(null=True)
	may_taken = models.FloatField(null=True)
	jun_taken = models.FloatField(null=True)
	jul_taken = models.FloatField(null=True)
	aug_taken = models.FloatField(null=True)
	sep_taken = models.FloatField(null=True)
	oct_taken = models.FloatField(null=True)
	nov_taken = models.FloatField(null=True)
	dec_taken = models.FloatField(null=True)
	taken_in_this_year = models.FloatField(default=0.0)
	balance = models.FloatField(default=0.0)
	create_date = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return '%s | Sick Leave Summary Report for the year of %s' % (self.employee.display_name, str(self.report_date.year))
