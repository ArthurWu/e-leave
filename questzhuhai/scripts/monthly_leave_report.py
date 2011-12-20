import sys, os
sys.path.append(r'C:\LeaveSystem\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from common import report
from datetime import datetime
from maitenance.models import Employee


now = datetime.now()
employees = Employee.objects.all()

report.generate_leave_report_file(employees, now.day, now.month, now.year)
