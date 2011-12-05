import sys, os
sys.path.append(r'C:\projects\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from common import report
from datetime import datetime
from maitenance.models import Employee

now = datetime.now()
start_date = report.get_lastest_month_period(now)
employees = Employee.objects.all()

report.generate_leave_record_report_file(employees, start_date, now)