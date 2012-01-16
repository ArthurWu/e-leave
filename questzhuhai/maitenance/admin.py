from django.contrib import admin
from models import *
from django.utils.functional import update_wrapper
from django.db import router
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.contrib.admin import helpers
from django import template
from django.db import transaction
import main_utils

def generate_leave_record_report(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	app_label = opts.app_label
	
	if request.POST.get('post'):
		if queryset.count():
			start_date_ = request.POST.get('start_date').strip()
			end_date_ = request.POST.get('end_date').strip()
			import datetime
			start_date = datetime.datetime.strptime(start_date_, '%Y-%m-%d')
			end_date = datetime.datetime.strptime(end_date_, '%Y-%m-%d')
			
			from common.report import generate_leave_record_report_file
			filename = generate_leave_record_report_file(queryset, start_date, end_date)
			
			link = '/main/reports/download/leaverecord/%s/%s/' % (start_date.strftime('%Y_%m_%d'),end_date.strftime('%Y_%m_%d'))
			cont={'link': link}
			return render_to_response('maitenance/generate_report_successful.html',cont, context_instance=template.RequestContext(request))
	
	if len(queryset) == 1:
		objects_name = force_unicode(opts.verbose_name)
	else:
		objects_name = force_unicode(opts.verbose_name_plural)
	
	title = "Are you sure?"
	
	context = {
		"title": title,
		"objects_name": objects_name,
		'queryset': queryset,
		"opts": opts,
		"app_label": app_label,
		'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
		'leave_record': True
	}
	
	return render_to_response(
		'maitenance/generate_report_confirmation.html',
		context,
		context_instance=template.RequestContext(request)
	)
	
generate_leave_record_report.short_description = "Generate selected %(verbose_name_plural)s's leave record report"

def generate_leave_report(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	app_label = opts.app_label
	
	if request.POST.get('post'):
		if queryset.count():
			#start_date = request.POST.get('start_date').strip()
			end_date = request.POST.get('end_date').strip()
			import datetime
			date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
			
			from common.report import generate_leave_report_file
			filename = generate_leave_report_file(queryset, date.day, date.month, date.year)
			
			link = '/main/reports/download/leavereport/%s' % date.strftime('%Y/%m/%d/')
			cont={'link': link}
			return render_to_response('maitenance/generate_report_successful.html',cont, context_instance=template.RequestContext(request))
	
	if len(queryset) == 1:
		objects_name = force_unicode(opts.verbose_name)
	else:
		objects_name = force_unicode(opts.verbose_name_plural)
	
	title = "Are you sure?"
	
	context = {
		"title": title,
		"objects_name": objects_name,
		'queryset': queryset,
		"opts": opts,
		"app_label": app_label,
		'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
	}
	
	return render_to_response(
		'maitenance/generate_report_confirmation.html',
		context,
		context_instance=template.RequestContext(request)
	)

generate_leave_report.short_description = "Generate selected %(verbose_name_plural)s's leave report"

def update_obj_fields(obj, start_fiscal_date, al_entitlement, sl_entitlement, approvers, cc_to):
    fields = {
        'start_fiscal_date': start_fiscal_date,
        'al_entitlement': al_entitlement,
        'sl_entitlement': sl_entitlement,
        'approvers':approvers,
        'cc_to':cc_to
    }
    for k, v in fields.items():
        if v:
            setattr(obj, k, v)
    obj.save()

@transaction.commit_on_success
def update_selected(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	app_label = opts.app_label
	
	if request.POST.get('post'):
		n = queryset.count()
		if n:
			start_fiscal_date = request.POST.get('start_fiscal_date').strip()
			al_entitlement = request.POST.get('al_entitlement').strip()
			sl_entitlement = request.POST.get('sl_entitlement').strip()
			approvers = request.POST.get('approvers').strip()
			ccto = request.POST.get('ccto').strip()
			
			for obj in queryset:
				obj_display = force_unicode(obj)
				from main_utils import add_maitenance_log
				add_maitenance_log(request.employee.display_name, 'updated information of %s ' % obj_display)
				update_obj_fields(obj, start_fiscal_date, al_entitlement, sl_entitlement, approvers, ccto)
				
		# Return None to display the change list page again.
		return None
	
	if len(queryset) == 1:
		objects_name = force_unicode(opts.verbose_name)
	else:
		objects_name = force_unicode(opts.verbose_name_plural)
	
	title = "Are you sure?"
	
	context = {
		"title": title,
		"objects_name": objects_name,
		'queryset': queryset,
		"opts": opts,
		"app_label": app_label,
		'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
	}
	
	# Display the confirmation page
	return render_to_response(modeladmin.update_selected_confirmation_template,
							  context,
							  context_instance=template.RequestContext(request))

update_selected.short_description = "Update selected %(verbose_name_plural)s"

def archive_year_adjustment_days(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	
	if request.POST.get('post'):
		year = request.POST.get('year').strip()
		for q in queryset:
			adjustmentdays = q.adjustmentdays_set.all().filter(month__startswith=year)
			
			for a in adjustmentdays:
				adh = AdjustmentDaysHistory()
				adh.employee = a.employee
				adh.adjustment_days = a.adjustment_days
				adh.leave_type = a.leave_type
				adh.month = a.month
				adh.comment = a.comment
				adh.create_date = a.create_date
				adh.save()
				
			adjustmentdays.delete()
		# Return None to display the change list page again.
		return None
	
	if len(queryset) == 1:
		objects_name = force_unicode(opts.verbose_name)
	else:
		objects_name = force_unicode(opts.verbose_name_plural)
		
	context = {
		"objects_name": objects_name,
		'queryset': queryset,
		'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
	}
	return render_to_response('maitenance/archive_year_adjustment_days.html',
							  context,
							  context_instance=template.RequestContext(request))
archive_year_adjustment_days.short_description = "Archive selected %(verbose_name_plural)s' adjustment days"

class AjuestmentDaysInline(admin.TabularInline):
	model = AdjustmentDays
	extra = 0
	
	exclude = ('expire_date',)
	
class MarriageLeaveConfirmInline(admin.TabularInline):
	model = MarriageLeaveConfirm
	extra = 0

class EmployeeAdmin(admin.ModelAdmin):
	list_display = (
		'display_name', 
		'domain_id',
		'title', 
		'email',
		'department', 
		'team', 
		'join_date', 
		'start_fiscal_date', 
		'balanced_forward',
		'al_entitlement',
		'sl_entitlement',
		'approvers',
		'cc_to',
		'is_administrative_staff',
	)
	list_display_links = ('display_name',)
	change_list_template = 'maitenance/employee_list.html'
	add_form_template = 'maitenance/add_employee.html'
	change_form_template = 'maitenance/add_employee.html'
	delete_confirmation_template = 'maitenance/delete_confirmation.html'
	delete_selected_confirmation_template = 'maitenance/delete_selected_confirmation.html'
	update_selected_confirmation_template = 'maitenance/update_selected_confirmation.html'
	
	list_filter = ('department', 'team', 'title', 'join_date', 'is_administrative_staff', 'is_active')
	list_per_page = 20
	list_select_related = True
	ordering = ('-display_name',)
	search_fields = ['domain_id', 'display_name', 'title', 'email']
	save_on_top = True
	
	fieldsets = (
		(None, {
			'classes': ['wide', 'extrapretty'],
			'fields': ('domain_id', 'display_name', 'chinese_name', 'title', 'email', 'department', 'team')
		}),
		('Advanced data', {
			'classes': ('collapse','wide', 'extrapretty'),
			'fields': ('join_date', 'start_fiscal_date', 'balanced_forward', 'al_entitlement',
					   'sl_entitlement', 'approvers', 'cc_to', 'is_administrative_staff',
					   'is_active', 'balanced_days')
		})
	)
	
	inlines = [AjuestmentDaysInline,MarriageLeaveConfirmInline,]
	actions = [
		update_selected,
		generate_leave_report,
		generate_leave_record_report,
		archive_year_adjustment_days,
	]
	

	def changelist_view(self, request, extra_context=None):
		extra_context = {'nav': 'employees'}
		return super(EmployeeAdmin, self).changelist_view(request, extra_context)
		
	def change_view(self, request, object_id, extra_context=None):
		if request.method == 'POST':
			obj = self.get_object(request, object_id)
			main_utils.add_maitenance_log(request.employee.domain_id, 'have modified the information of %s' % obj.domain_id)
		extra_context = {'nav': 'employees'}
		return super(EmployeeAdmin, self).change_view(request, object_id, extra_context)
		
	def add_view(self, request, form_url='', extra_context=None):
		if request.method == 'POST':
			operator = request.employee.domain_id
			objname = request.POST.get('domain_id')
			main_utils.add_maitenance_log(operator, 'have added an employee %s' % objname)
			
			res = super(EmployeeAdmin, self).add_view(request, form_url, extra_context)

			from models import Employee
			emp = Employee.objects.filter(domain_id=objname)
			emp = emp and emp[0] or None
			if emp:
				import common.ad_utils as ad_utils
				emp.sid = ad_utils.GetADObject(objname)[1] or ''
				emp.approvers = emp.approvers.strip(';')+';'
				emp.cc_to = emp.cc_to.strip(';')+';'
				emp.save()
			return res
		extra_context = {'nav': 'employees'}
		return super(EmployeeAdmin, self).add_view(request, form_url, extra_context)
		
	def delete_view(self, request, object_id, extra_context=None):
		if request.method == 'POST':
			obj = self.get_object(request, object_id)
			main_utils.add_maitenance_log(request.employee.domain_id, 'have deleted the employee %s' % obj.domain_id)
		extra_context = {'nav': 'employees'}
		return super(EmployeeAdmin, self).delete_view(request, object_id, extra_context)
		
admin.site.register(Employee, EmployeeAdmin)

class DjangoAdminForAdmin(admin.ModelAdmin):
	list_per_page = 20
admin.site.register(Admin, DjangoAdminForAdmin)

class DepartmentAdmin(admin.ModelAdmin):
	list_display = ('name', 'supervisor')
	change_list_template = 'maitenance/department_list.html'
	add_form_template = 'maitenance/add_employee.html'
	change_form_template = 'maitenance/add_employee.html'
	delete_selected_confirmation_template = 'maitenance/delete_selected_confirmation.html'
	
	def changelist_view(self, request, extra_context=None):
		extra_context = {'nav': 'departments'}
		return super(DepartmentAdmin, self).changelist_view(request, extra_context)

admin.site.register(Department, DepartmentAdmin)

class TeamAdmin(admin.ModelAdmin):
	list_display = ('name', 'leader', 'department')
	change_list_template = 'maitenance/department_list.html'
	add_form_template = 'maitenance/add_employee.html'
	change_form_template = 'maitenance/add_employee.html'
	delete_selected_confirmation_template = 'maitenance/delete_selected_confirmation.html'
	
	def changelist_view(self, request, extra_context=None):
		extra_context = {'nav': 'teams'}
		return super(TeamAdmin, self).changelist_view(request, extra_context)

admin.site.register(Team)