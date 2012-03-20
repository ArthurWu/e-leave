import datetime, calendar
import settings
from maitenance.models import AnnualLeaveReport, SickLeaveReport
from leave.models import LeaveRequest, LeaveType, Period
from leave.processe import status
from django.db.models import Q

from xlrd import open_workbook
from xlwt import easyxf, Style, Alignment, Pattern, Font, Borders
from xlutils.copy import copy
from xlutils.styles import Styles

from common.logger import log
	
def generate_leave_record_report_file(employees, start_date, end_date):
	queryset = LeaveRequest.objects.filter(
		(
			Q(period__start__range=(start_date, end_date))|
			Q(period__end__range=(start_date, end_date))
		)&
		Q(status__in=[status.PENDINGADMIN, status.ARCHIVED])
	).distinct()
	
	template = open_workbook(settings.REPORT_TEMPLATE + r'leave record report.xls', formatting_info=True)
	wb = copy(template)
	lrws = wb.get_sheet(0)
	
	left_center = Alignment()
	left_center.horz = Alignment.HORZ_LEFT
	left_center.vert = Alignment.VERT_CENTER
	
	center_center = Alignment()
	center_center.horz = Alignment.HORZ_CENTER
	center_center.vert = Alignment.VERT_CENTER
	
	style = easyxf(
		'font: name Arial;'
		'borders: left thin, right thin, top thin, bottom thin;'
	)
	style_bg = easyxf(
		'font: name Arial;'
		'borders: left thin, right thin, top thin, bottom thin;'
	)
	style_bg.alignment = left_center
	style.alignment = left_center
	
	pattern1 = Pattern()
	pattern1.pattern = Pattern.SOLID_PATTERN
	pattern1.pattern_fore_colour = 0x34
	
	pattern2 = Pattern()
	pattern2.pattern = Pattern.SOLID_PATTERN
	pattern2.pattern_fore_colour = 0x50
	
	style_bg.pattern = pattern1
	
	original_index = start_index = curr_index = 2
	for employee in employees:
		name_rows = queryset.filter(employee=employee).count()
		
		if name_rows > 0:
			leavetypes = list(LeaveType.objects.all())			
			for leavetype in leavetypes:
				
				leaverequests = queryset.filter(employee=employee, leave_type=leavetype)
				leavetype_rows = len(leaverequests)
				#print 'leavetype_rows', leavetype_rows
				if leavetype_rows > 0:
					if style_bg.pattern == pattern1:
						style_bg.pattern = pattern2
					else:
						style_bg.pattern = pattern1
					
					duration = 0.0
					for l in leaverequests:
						periods = l.period_set.all().filter(
											Q(start__range=(start_date, end_date))|
											Q(end__range=(start_date, end_date)))
						for p in periods:
							p_start = max(p.start, start_date)
							p_end = min(p.end, end_date)
							lrws.write(
								curr_index, 2, \
								Period(leave_request=l, start=p_start, end=p_end).__unicode__(), \
								style_bg)
							curr_index += 1
							duration += duration_days(p_start, p_end)
					
					style_bg.alignment = center_center
					lrws.write_merge(start_index, curr_index - 1, 3, 3, duration, style_bg)
					style_bg.alignment = left_center
					lrws.write_merge(start_index, curr_index - 1, 1, 1, leavetype.name, style_bg)
					start_index = curr_index
		
			lrws.write_merge(original_index, curr_index - 1, 0, 0, employee.display_name, style)
			original_index = start_index = curr_index
		
	filename = settings.REPORT_FILES + 'leaverecordreport-%s-%s.xls' % (start_date.strftime('%Y_%m_%d'), end_date.strftime('%Y_%m_%d'))
	wb.save(filename)
	
	return filename

def generate_leave_report_file(employees, base_day, month=None, year=None, start_date = None):
	'''
	start_date is the date report data start to generate.
	if None, will user 01-01 of the 'year'
	'''
	alr = create_report_data(employees, base_day, month, year)
	slr = create_sick_leave_report_data(employees, base_day, month, year)

	template = open_workbook(settings.REPORT_TEMPLATE + r'leave report.xls', formatting_info=True)
	wb = copy(template)
	alws = wb.get_sheet(0)
	slws = wb.get_sheet(1)
	
	add_annual_leave_header(alws, year, month, base_day)
	add_annual_leave_row_data(alws, alr)
	add_sick_leave_row_data(slws, slr)

	today = datetime.date.today()
	report_date = datetime.date(today.year, month, base_day)
	filename = settings.REPORT_FILES + 'leavereport-%s.xls' % report_date.strftime('%Y-%m-%d')
	wb.save(filename)
	
	return filename

def get_last_annual_leave_report_data(alr):
	_d = alr.report_date
	year = _d.year
	month = _d.month
	day = _d.day
	
	report_date = None
	if day == settings.LEAVE_REPORT_FIRST_DAY and month != 1:
		report_date = datetime.datetime(year, month-1, settings.LEAVE_REPORT_SECEND_DAY)
	elif day == settings.LEAVE_REPORT_SECEND_DAY:
		report_date = datetime.datetime(year, month, settings.LEAVE_REPORT_FIRST_DAY)
	else:
		date = datetime.datetime(year, month, day)
		alrs = AnnualLeaveReport.objects.filter(employee=alr.employee, report_date__lt=date, report_date__year=year).order_by('-report_date')
		if alrs:
			report_date = alrs[0].report_date
	
	last_alr = None
	if report_date:
		res = AnnualLeaveReport.objects.filter(employee=alr.employee, report_date=report_date)
		if res: last_alr = res[0]
		
	return last_alr

def compare_value(s, t, key_field):
	if not t or getattr(s, key_field) == getattr(t, key_field):
		return True
	return False

def add_sick_leave_header(ws, year, month, day):
	style, style_s, style_m = get_styles()
	
	ws.write(1, 0, 'Sick Leave Summary Report for the year of %s' % str(year), style)
	ws.write(3, 3, 'Working days for year %s as of %s-%s-%s' % (str(year), str(year), str(month), str(day)), style_s)
	ws.write(3, 8, 'Total entitled as of %s-%s-%s' % (str(year), str(month), str(day)), style_s)
	
	short_year = str(year)[2:]
	ws.write(7, 6,  'Jan, %s' % short_year, style_m)
	ws.write(7, 7,  'Feb, %s' % short_year, style_m)
	ws.write(7, 8,  'Mar, %s' % short_year, style_m)
	ws.write(7, 9,  'Apr, %s' % short_year, style_m)
	ws.write(7, 10, 'May, %s' % short_year, style_m)
	ws.write(7, 11, 'Jun, %s' % short_year, style_m)
	ws.write(7, 12, 'Jul, %s' % short_year, style_m)
	ws.write(7, 13, 'Aug, %s' % short_year, style_m)
	ws.write(7, 14, 'Sep, %s' % short_year, style_m)
	ws.write(7, 15, 'Oct, %s' % short_year, style_m)
	ws.write(7, 16, 'Nov, %s' % short_year, style_m)
	ws.write(7, 17, 'Dec, %s' % short_year, style_m)
	
def get_styles():
	style = easyxf(
		'font: name Arial;'
	)
	style_s = easyxf(
		'font: name Arial;'
		'borders: left thin, right thin, top medium, bottom thin;'
	)
	style_m = easyxf(
		'font: name Arial, bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
	)
	font = Font()
	font.bold = 1
	font.height = 320
	style.font = font
	style.alignment.horz = Alignment.HORZ_LEFT
	style.alignment.vert = Alignment.VERT_CENTER
	style_s.font.height = 200
	style_s.font.bold = 1
	style_s.alignment.horz = Alignment.HORZ_CENTER
	style_s.alignment.vert = Alignment.VERT_CENTER
	style_s.alignment.wrap = True
	
	return style, style_s, style_m

def add_annual_leave_header(ws, year, month, day):
	style, style_s, style_m = get_styles()
	
	ws.write(1, 0, 'Annual Leave Summary Report for the year of %s' % str(year), style)
	ws.write(3, 2, 'Balanced forward from yr %s' % str(year), style_s)
	ws.write(3, 3, 'Adjustment days of yr %s' % str(year), style_s)
	ws.write(3, 5, 'Total %s A/L Entitlement' % str(year), style_s)
	ws.write(3, 6, 'Working days for year %s as of %s-%s-%s' % (str(year), str(year), str(month), str(day)), style_s)
	ws.write(3, 7, 'A/L Entitlement as of %s-%s-%s' % (str(year), str(month), str(day)), style_s)
	ws.write(3, 8, 'Total entitled as of %s-%s-%s' % (str(year), str(month), str(day)), style_s)
	
	short_year = str(year)[2:]
	ws.write(4, 9,  'Jan, %s' % short_year, style_m)
	ws.write(4, 10, 'Feb, %s' % short_year, style_m)
	ws.write(4, 11, 'Mar, %s' % short_year, style_m)
	ws.write(4, 12, 'Apr, %s' % short_year, style_m)
	ws.write(4, 13, 'May, %s' % short_year, style_m)
	ws.write(4, 14, 'Jun, %s' % short_year, style_m)
	ws.write(4, 15, 'Jul, %s' % short_year, style_m)
	ws.write(4, 16, 'Aug, %s' % short_year, style_m)
	ws.write(4, 17, 'Sep, %s' % short_year, style_m)
	ws.write(4, 18, 'Oct, %s' % short_year, style_m)
	ws.write(4, 19, 'Nov, %s' % short_year, style_m)
	ws.write(4, 20, 'Dec, %s' % short_year, style_m)
	
	ws.write(4, 22,  'Jan, %s' % short_year, style_m)
	ws.write(4, 23, 'Feb, %s' % short_year, style_m)
	ws.write(4, 24, 'Mar, %s' % short_year, style_m)
	ws.write(4, 25, 'Apr, %s' % short_year, style_m)
	ws.write(4, 26, 'May, %s' % short_year, style_m)
	ws.write(4, 27, 'Jun, %s' % short_year, style_m)
	ws.write(4, 28, 'Jul, %s' % short_year, style_m)
	ws.write(4, 29, 'Aug, %s' % short_year, style_m)
	ws.write(4, 30, 'Sep, %s' % short_year, style_m)
	ws.write(4, 31, 'Oct, %s' % short_year, style_m)
	ws.write(4, 32, 'Nov, %s' % short_year, style_m)
	ws.write(4, 33, 'Dec, %s' % short_year, style_m)

def create_report_data(employees, base_day, month=None, year=None):
	res_data = []
	for employee in list(employees):
		alr = AnnualLeaveReport(employee = employee)
		
		today = datetime.date.today()
		year = year or today.year
		month = month or today.month
		
		base_date = datetime.datetime(year, month, base_day)
		start_date = datetime.datetime(year, 1, 1)
		start_date = employee.start_fiscal_date < start_date and start_date or employee.start_fiscal_date
		days_to_base_date_of_this_year = float((base_date - start_date).days) + 1
		
		alr.working_days = days_to_base_date_of_this_year	
		_al_entitlement_of = convert_to_tow_places_float((days_to_base_date_of_this_year/365)*employee.al_entitlement)
		alr.al_entitlement_of = _al_entitlement_of
		alr.total_entitled_as_of = convert_to_tow_places_float(employee.balanced_forward + _al_entitlement_of)
		
		res = monthly_taken_days(alr, employee, base_day, month)
		alr.taken_in_this_year = sum(res)
		
		deduction_days = monthly_deduction_days(alr, employee, month)
		alr.available_annual_leave_unclaimed = convert_to_tow_places_float(alr.total_entitled_as_of - \
						alr.taken_in_this_year + sum(deduction_days) + employee.balanced_days)
		alr.marrige_leave_balance = marriage_leave_balance(employee, start_date, base_date)
		
		alr.report_date = datetime.datetime(year, month, base_day)
		alr.save()
		res_data.append(alr)
	return res_data
	
def marriage_leave_balance(emp, start_date, end_date):
	'''
	the marriage leave balance untill the date specify for the current year.
	'''
	marriageleave = LeaveType.objects.filter(name = 'Marriage Leave')
	if marriageleave:
		marriageleave = marriageleave[0]
		
	max_days = marriageleave.max_days
	marriageleaveconfirm = emp.marriageleaveconfirm_set.all()
	if marriageleaveconfirm:
		max_days = marriageleaveconfirm[0].days
		
	leaverequests = emp.leaverequest_set.all().filter(leave_type=marriageleave)
	return max_days - leave_requests_duration_days(leaverequests, start_date, end_date)
		
def create_sick_leave_report_data(employees, base_day, month=None, year=None):
	res_data = []
	for employee in employees:
		slr = SickLeaveReport(employee = employee)
		today = datetime.date.today()
		year = year or today.year
		month = month or today.month
		
		base_date = datetime.datetime(year, month, base_day)
		start_date = datetime.datetime(year, 1, 1)
		start_date = employee.start_fiscal_date < start_date and start_date or employee.start_fiscal_date
		days_to_base_date_of_this_year = float((base_date - start_date).days) + 1
		slr.working_days = days_to_base_date_of_this_year
		slr.report_date = base_date
		
		_sl_entitlement_of = convert_to_tow_places_float((days_to_base_date_of_this_year/365)*employee.sl_entitlement)
		slr.al_entitlement_of = employee.sl_entitlement
		slr.total_entitled_as_of = _sl_entitlement_of + employee.get_leave_adjustment_days('Sick Leave')
		
		res = monthly_taken_days(slr, employee, base_day, month, leave_type="Sick Leave")
		slr.taken_in_this_year = sum(res)
		slr.balance = convert_to_tow_places_float(slr.total_entitled_as_of - slr.taken_in_this_year)
		
		slr.save()
		res_data.append(slr)
		
	return res_data

def add_annual_leave_row_data(ws, alr):
	style = easyxf(
		'font: name Arial;'
		'borders: left thin, right thin, top thin, bottom thin;'
	)
	style_bold = easyxf(
		'font: bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour light_yellow;'
	)
	style_green = easyxf(
		'font: bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour light_green;'
	)
	style_olive_green = easyxf(
		'font: bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour periwinkle;'
	)
	style_gray40 = easyxf(
		'font: bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour gray25;'
	)
	style_change = easyxf(
		'font: name Arial;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour red;'
	)
	
	for i in range(0, len(alr)):
		last_alr = get_last_annual_leave_report_data(alr[i])
		
		rownum = i + 5
		row = ws.row(rownum)
		row.write(0, alr[i].employee.display_name, style)
		row.write(1, alr[i].employee.chinese_name, style)
		row.write(2, alr[i].employee.balanced_forward, style)
		row.write(3, alr[i].employee.balanced_days, style)
		row.write(4, alr[i].employee.start_fiscal_date.strftime('%Y-%m-%d'), style)
		row.write(5, alr[i].employee.al_entitlement, style)
		row.write(6, alr[i].working_days, style)
		row.write(7, alr[i].al_entitlement_of, style_bold)
		row.write(8, alr[i].total_entitled_as_of, style_bold)
		row.write(9, alr[i].jan_taken, compare_value(alr[i], last_alr, 'jan_taken') and style or style_change)
		row.write(10, alr[i].feb_taken, compare_value(alr[i], last_alr, 'feb_taken') and style or style_change)
		row.write(11, alr[i].mar_taken, compare_value(alr[i], last_alr, 'mar_taken') and style or style_change)
		row.write(12, alr[i].apr_taken, compare_value(alr[i], last_alr, 'apr_taken') and style or style_change)
		row.write(13, alr[i].may_taken, compare_value(alr[i], last_alr, 'may_taken') and style or style_change)
		row.write(14, alr[i].jun_taken, compare_value(alr[i], last_alr, 'jun_taken') and style or style_change)
		row.write(15, alr[i].jul_taken, compare_value(alr[i], last_alr, 'jul_taken') and style or style_change)
		row.write(16, alr[i].aug_taken, compare_value(alr[i], last_alr, 'aug_taken') and style or style_change)
		row.write(17, alr[i].sep_taken, compare_value(alr[i], last_alr, 'sep_taken') and style or style_change)
		row.write(18, alr[i].oct_taken, compare_value(alr[i], last_alr, 'oct_taken') and style or style_change)
		row.write(19, alr[i].nov_taken, compare_value(alr[i], last_alr, 'nov_taken') and style or style_change)
		row.write(20, alr[i].dec_taken, compare_value(alr[i], last_alr, 'dec_taken') and style or style_change)
		row.write(21, alr[i].taken_in_this_year, style_green)
		row.write(22, alr[i].jan_deduction, compare_value(alr[i], last_alr, 'jan_deduction') and style or style_change)
		row.write(23, alr[i].feb_deduction, compare_value(alr[i], last_alr, 'feb_deduction') and style or style_change)
		row.write(24, alr[i].mar_deduction, compare_value(alr[i], last_alr, 'mar_deduction') and style or style_change)
		row.write(25, alr[i].apr_deduction, compare_value(alr[i], last_alr, 'apr_deduction') and style or style_change)
		row.write(26, alr[i].may_deduction, compare_value(alr[i], last_alr, 'may_deduction') and style or style_change)
		row.write(27, alr[i].jun_deduction, compare_value(alr[i], last_alr, 'jun_deduction') and style or style_change)
		row.write(28, alr[i].jul_deduction, compare_value(alr[i], last_alr, 'jul_deduction') and style or style_change)
		row.write(29, alr[i].aug_deduction, compare_value(alr[i], last_alr, 'aug_deduction') and style or style_change)
		row.write(30, alr[i].sep_deduction, compare_value(alr[i], last_alr, 'sep_deduction') and style or style_change)
		row.write(31, alr[i].oct_deduction, compare_value(alr[i], last_alr, 'oct_deduction') and style or style_change)
		row.write(32, alr[i].nov_deduction, compare_value(alr[i], last_alr, 'nov_deduction') and style or style_change)
		row.write(33, alr[i].dec_deduction, compare_value(alr[i], last_alr, 'dec_deduction') and style or style_change)
		row.write(34, alr[i].available_annual_leave_unclaimed, style_green)
		row.write(35, alr[i].application_comp_leave, style)
		row.write(36, alr[i].taken_comp_leave, style)
		row.write(37, alr[i].balance_of_comp_leave, style_bold)
		row.write(38, alr[i].marrige_leave_balance, style_green)

def add_sick_leave_row_data(ws, slr):
	style = easyxf(
		'font: name Arial;'
		'borders: left thin, right thin, top thin, bottom thin;'
	)
	style_bold = easyxf(
		'font: name Arial, bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour light_yellow;'
	)
	style_green = easyxf(
		'font: bold True;'
		'borders: left thin, right thin, top thin, bottom thin;'
		'pattern: pattern solid, fore_colour light_green;'
	)
	for i in range(0, len(slr)):
		rownum = i + 8
		row = ws.row(rownum)
		row.write(0, slr[i].employee.display_name, style)
		row.write(1, slr[i].employee.chinese_name, style)
		row.write(2, slr[i].employee.start_fiscal_date.strftime('%Y-%m-%d'), style)
		row.write(3, slr[i].working_days, style)
		row.write(4, slr[i].al_entitlement_of, style_bold)
		row.write(5, slr[i].total_entitled_as_of, style_bold)
		row.write(6, slr[i].jan_taken, style)
		row.write(7, slr[i].feb_taken, style)
		row.write(8, slr[i].mar_taken, style)
		row.write(9, slr[i].apr_taken, style)
		row.write(10, slr[i].may_taken, style)
		row.write(11, slr[i].jun_taken, style)
		row.write(12, slr[i].jul_taken, style)
		row.write(13, slr[i].aug_taken, style)
		row.write(14, slr[i].sep_taken, style)
		row.write(15, slr[i].oct_taken, style)
		row.write(16, slr[i].nov_taken, style)
		row.write(17, slr[i].dec_taken, style)
		row.write(18, slr[i].taken_in_this_year, style_green)
		row.write(19, slr[i].balance, style_green)
		
def convert_to_tow_places_float(value):
	from decimal import Decimal
	TWOPLACES = Decimal(10) ** -2
	return float(Decimal(str(value)).quantize(TWOPLACES))
	
def monthly_deduction_days(annual_leave_report, employee, month=None):
	month_deduction = ['jan_deduction', 'feb_deduction', 'mar_deduction', 'apr_deduction', 'may_deduction',
				   'jun_deduction', 'jul_deduction', 'aug_deduction', 'sep_deduction', 'oct_deduction', 'nov_deduction', 'dec_deduction']
	c_year = str(datetime.datetime.now().year)
	aju_set = employee.adjustmentdays_set.all().filter(month__startswith=c_year, leave_type__name='Annual Leave')
	aju_his_set = employee.adjustmentdayshistory_set.all().filter(month__startswith=c_year, leave_type__name='Annual Leave')
	res = []
	
	def set_value(queryset):
		for i in range(1, month+1):
			i_ = c_year + '-' + str(i)
			if queryset.filter(month=i_):
				d = queryset.filter(month=i_)[0].adjustment_days
				setattr(annual_leave_report, month_deduction[i-1], d)
				res.append(d)
	
	if len(aju_set) > 0:
		set_value(aju_set)
	if len(aju_his_set) > 0:
		set_value(aju_his_set)
			
	return res

def monthly_taken_days(leave_report, employee, base_day, month, leave_type="Annual Leave"):
	month_taken = ['jan_taken', 'feb_taken', 'mar_taken', 'apr_taken', 'may_taken',
				   'jun_taken', 'jul_taken', 'aug_taken', 'sep_taken', 'oct_taken', 'nov_taken', 'dec_taken']
	res = []
	for i in range(1, month+1):
		day = base_day if i == month else None
		d = month_leave_taken_days(employee, month=i, base_day=day, leave_type=leave_type)
		if d > 0:
			setattr(leave_report, month_taken[i-1], d)
		res.append(d)
	
	return res

def month_leave_taken_days(employee, month, base_day=None, leave_type="Annual Leave"):
	start_date, end_date = get_month_period(month, base_day)
	report_days_ = report_days(start_date, end_date)
	lrs = list(employee.leaverequest_set.all().filter(leave_type__name=leave_type,\
												 status__in=[status.PENDINGADMIN, status.ARCHIVED]))
	duration = 0.0
	for l in lrs:
		for p in l.period_set.all():
			if p.start.strftime('%Y-%m-%d') in report_days_:
				if p.end < end_date:
					duration += duration_days(p.start, p.end)
				else:
					duration += duration_days(p.start, end_date)
	return duration

def leave_requests_duration_days(leaverequests, start_date, end_date):
	duration = 0.0
	for l in leaverequests:
		periods = l.period_set.all().filter(
							Q(start__range=(start_date, end_date))|
							Q(end__range=(start_date, end_date)))
		for p in periods:
			p_start = max(p.start, start_date)
			p_end = min(p.end, end_date)
			duration += duration_days(p_start, p_end)
	return duration
	
def duration_days(start, end):
	def caculate(s, e):
		if s == e: return 0.5
		if s == 'AM' and e == 'PM': return 1.0
		if s == 'PM' and e == 'AM': return 0
		
	start_ampm = start.strftime('%Y-%m-%d-%p').split('-')[-1]
	end_ampm = end.strftime('%Y-%m-%d-%p').split('-')[-1]
	return (end - start).days + caculate(start_ampm, end_ampm)
	
def report_days(start_date, end_date):
	days = (end_date - start_date).days + 1
	res = []
	for i in range(0, days):
		res.append((end_date - datetime.timedelta(days = i)).strftime('%Y-%m-%d'))
	
	return res
	
def get_month_period(month, base_day=None):
	cur_year = datetime.datetime.now().year
	from_date = datetime.datetime(cur_year, month, 1)
	to_date = datetime.datetime(cur_year, month, calendar.monthrange(cur_year, month)[1], 17,30)
	if base_day:
		to_date = datetime.datetime(cur_year, month, base_day, 17, 30)
	
	return from_date, to_date

def get_lastest_month_period(end_date):
	month = end_date.month
	if month == 1:
		start_date = datetime.datetime(end_date.year, month, 1)
	else:
		start_date = datetime.datetime(end_date.year, month - 1, end_date.day + 1)
	
	return start_date
		