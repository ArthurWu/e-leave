import sys, os
sys.path.append(r'C:\projects\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from common import report
from datetime import datetime
from maitenance.models import Employee
from maitenance.utils import send_email_to_admin

now = datetime.now()
start_date = report.get_lastest_month_period(now)
employees = Employee.objects.all()

report.generate_leave_record_report_file(employees, start_date, now)

# send email to notice admin
subject = "Monthly leave record report(%s~%s)" % (start_date.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d'))
send_email_to_admin('report_notification.txt', subject, now, start_date, type = 'leave record')