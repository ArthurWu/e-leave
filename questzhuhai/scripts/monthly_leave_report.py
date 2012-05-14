import sys, os
sys.path.append(r'C:\E-LeaveSystem\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from common import report
from datetime import datetime
from maitenance.models import Employee
from common.utils import send_email_to_admin


def GenerateLeavesReport():
	now = datetime.now()
	employees = Employee.objects.all()

	# generate leave report file automaticaly,
	# use Windows Task Scheduler to control
	report.generate_leave_report_file(employees, now.day, now.month, now.year)

	# send email to notice admin
	subject = "Monthly leave report %s" % now.strftime('%Y-%m-%d')
	send_email_to_admin('report_notification.txt', subject, now, type = 'leave report')
	

if __name__ == '__main__':
	GenerateLeavesReport()