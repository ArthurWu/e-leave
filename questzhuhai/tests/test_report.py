import sys 
sys.path.append(r'C:\LeaveSystem\questzhuhai')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'questzhuhai.settings'

from nose.tools import *
from questzhuhai.maitenance.models import *
from questzhuhai.leave.models import *
from questzhuhai.common import report
import datetime

def _setup():
	employee = Employee.objects.get(id=3)
	employee1 = Employee.objects.get(id=2)
	leavetype = LeaveType.objects.get(id=1)
	sickleave = LeaveType.objects.get(id=2)
	lr1 = LeaveRequest.objects.create(employee=employee, status="Approved",leave_type=leavetype, days=1)
	Period.objects.create(leave_request=lr1, start=datetime.datetime(2011,8,10,9),end=datetime.datetime(2011,8,10,13))
	
	lr2 = LeaveRequest.objects.create(employee=employee, status="Approved",leave_type=leavetype, days=0.5)
	Period.objects.create(leave_request=lr2, start=datetime.datetime(2011,8,16,9),end=datetime.datetime(2011,8,16,9))
	
	lr3 = LeaveRequest.objects.create(employee=employee, status="Approved",leave_type=leavetype, days=1.5)
	Period.objects.create(leave_request=lr3, start=datetime.datetime(2011,8,23,9),end=datetime.datetime(2011,8,23,13))
	Period.objects.create(leave_request=lr3, start=datetime.datetime(2011,8,26,9),end=datetime.datetime(2011,8,26,9))
	
	lr4 = LeaveRequest.objects.create(employee=employee, status="Approved",leave_type=leavetype, days=4)
	Period.objects.create(leave_request=lr4, start=datetime.datetime(2011,9,8,9),end=datetime.datetime(2011,9,9,13))
	Period.objects.create(leave_request=lr4, start=datetime.datetime(2011,9,12,9),end=datetime.datetime(2011,9,13,13))
	
	lr5 = LeaveRequest.objects.create(employee=employee1, status="Approved",leave_type=leavetype, days=2.5)
	Period.objects.create(leave_request=lr5, start=datetime.datetime(2011,10,24,9),end=datetime.datetime(2011,10,26,9))
	
	lr6 = LeaveRequest.objects.create(employee=employee1, status="Approved",leave_type=leavetype, days=1.5)
	Period.objects.create(leave_request=lr6, start=datetime.datetime(2011,1,4,9),end=datetime.datetime(2011,1,5,9))
	
	lr7 = LeaveRequest.objects.create(employee=employee, status="Approved",leave_type=sickleave, days=2)
	Period.objects.create(leave_request=lr7, start=datetime.datetime(2011,1,10,9),end=datetime.datetime(2011,1,11,13))
	
	lr8 = LeaveRequest.objects.create(employee=employee, status="Approved",leave_type=sickleave, days=3)
	Period.objects.create(leave_request=lr8, start=datetime.datetime(2011,10,24,9),end=datetime.datetime(2011,10,26,13))
	Period.objects.create(leave_request=lr8, start=datetime.datetime(2011,10,27,9),end=datetime.datetime(2011,10,27,13))
	Period.objects.create(leave_request=lr8, start=datetime.datetime(2011,11,25,9),end=datetime.datetime(2011,11,25,13))
	Period.objects.create(leave_request=lr8, start=datetime.datetime(2011,11,27,9),end=datetime.datetime(2011,11,27,13))
	
	return employee, employee1

def _teardown(employees):
	for e in employees:
		e.leaverequest_set.all().delete()

def test_get_month_period():
	assert_equals(
		(datetime.datetime(2011, 1, 1, 0, 0), datetime.datetime(2011, 1, 31, 17, 30)),
		report.get_month_period(1)
	)
	assert_equals(
		(datetime.datetime(2011, 2, 1, 0, 0), datetime.datetime(2011, 2, 10, 17, 30)),
		report.get_month_period(2, 10)
	)
	
def test_report_days():
	start_date = datetime.datetime(2011,8,10)
	end_date = datetime.datetime(2011,8,20,12)
	
	days = report.report_days(start_date, end_date)
	expect = ['2011-08-10','2011-08-11','2011-08-12','2011-08-13','2011-08-14','2011-08-15','2011-08-16','2011-08-17','2011-08-18','2011-08-19','2011-08-20']
	expect.reverse()
	assert_equals(11, len(days))
	assert_equals(expect, days)
	
def test_month_leave_taken_days():
	employee = _setup()
	days1 = report.month_leave_taken_days(employee, 1, 10)
	days2 = report.month_leave_taken_days(employee, 1, 25)
	_teardown(employee)
	assert_equals(1.5, days1)
	assert_equals(1.5, days2)
	
def test_month_leave_taken_days_with_specify_month():
	employee = _setup()
	days1 = report.month_leave_taken_days(employee, 8, 10)
	days2 = report.month_leave_taken_days(employee, 8, 25)
	_teardown(employee)
	assert_equals(1, days1)
	assert_equals(2.5, days2)
	
def test_monthly_taken_days():
	employee = _setup()
	alr = AnnualLeaveReport(employee=employee)
	report.monthly_taken_days(alr, employee, base_day = 10, month = 9)
	_teardown(employee)
	assert_equals(1.5, alr.jan_taken)
	assert_equals(0, alr.feb_taken)
	assert_equals(0, alr.mar_taken)
	assert_equals(0, alr.apr_taken)
	assert_equals(0, alr.mar_taken)
	assert_equals(0, alr.jun_taken)
	assert_equals(0, alr.jul_taken)
	assert_equals(3, alr.aug_taken)
	assert_equals(2, alr.sep_taken)
	assert_equals(None, alr.oct_taken)
	assert_equals(None, alr.nov_taken)
	assert_equals(None, alr.dec_taken)
	
def test_create_report_data():
	employee = _setup()
	report.create_report_data([employee], base_day=10, month=1)
	alr = AnnualLeaveReport.objects.filter(employee=employee)[0]
	_teardown(employee)
	AnnualLeaveReport.objects.all().delete()
	assert_equals(employee, alr.employee)
	assert_equals(10, alr.working_days)
	assert_equals(0.32, alr.al_entitlement_of)
	assert_equals(employee.balanced_forward + 0.32, alr.total_entitled_as_of)
	
	assert_equals(1.5, alr.jan_taken)
	assert_equals(None, alr.feb_taken)
	assert_equals(None, alr.mar_taken)
	assert_equals(None, alr.apr_taken)
	assert_equals(None, alr.mar_taken)
	assert_equals(None, alr.jun_taken)
	assert_equals(None, alr.jul_taken)
	assert_equals(None, alr.aug_taken)
	assert_equals(None, alr.sep_taken)
	assert_equals(None, alr.oct_taken)
	assert_equals(None, alr.nov_taken)
	assert_equals(None, alr.dec_taken)
	
	assert_equals(1.5, alr.taken_in_this_year)
	
	assert_equals(-1, alr.jan_deduction)
	assert_equals(None, alr.feb_deduction)
	assert_equals(None, alr.mar_deduction)
	assert_equals(None, alr.apr_deduction)
	assert_equals(None, alr.mar_deduction)
	assert_equals(None, alr.jun_deduction)
	assert_equals(None, alr.jul_deduction)
	assert_equals(None, alr.aug_deduction)
	assert_equals(None, alr.sep_deduction)
	assert_equals(None, alr.oct_deduction)
	assert_equals(None, alr.nov_deduction)
	assert_equals(None, alr.dec_deduction)
	
	assert_equals(-2.18, alr.available_annual_leave_unclaimed)
	assert_equals(None, alr.application_comp_leave)
	assert_equals(None, alr.taken_comp_leave)
	assert_equals(None, alr.balance_of_comp_leave)
	assert_equals(None, alr.marrige_leave_balance)
	
def test_generate_annual_report_file():
	employee = _setup()
	es = Employee.objects.all()

	#report.generate_leave_report_file(es, base_day=10, month=i)
	import datetime
	start_date = datetime.datetime(2011,1,1)
	end_date = datetime.datetime(2011,12,1)
	report.generate_leave_record_report_file(es, start_date, end_date)
	_teardown(employee)
	AnnualLeaveReport.objects.all().delete()
	
	assert_equals(1,2)
	
def test_create_sick_leave_report_data():
	employee = _setup()
	res = report.create_sick_leave_report_data(employee, base_day=25, month=1)
	_teardown(employee)
	
	slr = res[0]
	print res
	assert_equals(employee, slr.employee)
	assert_equals(25, slr.working_days)
	assert_equals(15.00, slr.al_entitlement_of)
	assert_equals(1.03, slr.total_entitled_as_of)
	
	assert_equals(4.0, slr.jan_taken)
	assert_equals(None, slr.feb_taken)
	assert_equals(None, slr.mar_taken)
	assert_equals(None, slr.apr_taken)
	assert_equals(None, slr.mar_taken)
	assert_equals(None, slr.jun_taken)
	assert_equals(None, slr.jul_taken)
	assert_equals(None, slr.aug_taken)
	assert_equals(None, slr.sep_taken)
	assert_equals(None, slr.oct_taken)
	assert_equals(None, slr.nov_taken)
	assert_equals(None, slr.dec_taken)
	
	assert_equals(4.0, slr.taken_in_this_year)
	assert_equals(11.0, slr.balance)
	
	
def test_generate_leave_report_file():
	employees = _setup()
	start_date = datetime.datetime(2011, 1, 1)
	end_date = datetime.datetime(2011, 10, 25, 17, 30)
	filename = report.generate_leave_record_report_file(employees, start_date, end_date)
	_teardown(employees)
	print filename
	assert_equals(1, 0)