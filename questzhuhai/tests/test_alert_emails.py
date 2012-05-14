import sys 
sys.path.append(r'C:\LeaveSystem\questzhuhai')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'questzhuhai.settings'

from nose.tools import *
from questzhuhai.maitenance.models import *
from questzhuhai.leave.models import *
from questzhuhai.common import report
import datetime

def test_CheckNotYetApprovedReqeusts():
	employee = Employee.objects.get(domain_id="warrior\peter")
	employee.leaverequest_set.all().delete()
	leavetype = LeaveType.objects.get(id=1)
	annualleave = LeaveType.objects.get(id=1)
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=1, create_date=datetime.datetime(2012,4,22,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,26,9),end=datetime.datetime(2012,4,26,13))	
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=1, create_date=datetime.datetime(2012,4,20,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,25,9),end=datetime.datetime(2012,4,25,13))	
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=1, create_date=datetime.datetime(2012,4,19,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,28,9),end=datetime.datetime(2012,4,28,13))
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=1, create_date=datetime.datetime(2012,4,24,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,29,9),end=datetime.datetime(2012,4,29,13))
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=1, create_date=datetime.datetime(2012,4,10,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,30,9),end=datetime.datetime(2012,4,30,13))
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=1, create_date=datetime.datetime(2012,4,11,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,5,2,9),end=datetime.datetime(2012,5,2,13))
	
	lr1 = LeaveRequest.objects.create(employee=employee, status="Waiting for manager approval",leave_type=leavetype, days=2, create_date=datetime.datetime(2012,4,12,9))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,19,9),end=datetime.datetime(2012,4,19,13))
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2012,4,21,9),end=datetime.datetime(2012,4,21,13))
	
	#res = report.CheckNotYetApprovedReqeusts()
	now = datetime.datetime.now()
	s, e = report.get_month_period(now.month, now.day)
	res = report.GetNoeApprovedInReportMonth(s,e)
	for r in res: print r.create_date, r.delay_days()
	assert_equals(
		4,
		len(res)
	)
	
	#employee.leaverequest_set.all().delete()
	