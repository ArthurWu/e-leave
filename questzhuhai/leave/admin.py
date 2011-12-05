from django.contrib import admin
from models import *
from django.db import router
from django.utils.encoding import force_unicode
from django.contrib.admin import helpers
from django.shortcuts import render_to_response
from django import template
import processe.status as status
from maitenance.main_utils import add_maitenance_log

def archive_seleted(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	app_label = opts.app_label
	using = router.db_for_write(modeladmin.model)
	
	if request.POST.get('post'):
		n = queryset.count()
		if n:
			res = []
			for obj in queryset:
				if obj.status == status.PENDINGADMIN:
					obj.status = status.ARCHIVED
					obj.save()
					add_maitenance_log(request.employee.display_name, 'archived leave request of %s ' % obj.__unicode__())
				else:
					res.append(obj)
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
	return render_to_response(modeladmin.archive_selected_confirmation_template,
							context,
							context_instance=template.RequestContext(request)
						)

archive_seleted.short_description = "Archive selected %(verbose_name_plural)s"

class LeaveRequestAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'employee', 'leave_type', 'days', 'status', 'create_date')
	list_display_links = ('__unicode__', 'employee', 'leave_type')
	
	list_filter = ('leave_type', 'employee__department', 'status', 'create_date',)
	list_per_page = 20
	search_fields = ['employee', 'leave_type', 'status']
	date_hierarchy = 'create_date'
	
	change_list_template = 'leave/change_list.html'
	archive_selected_confirmation_template = 'leave/archive_selected_confirmation.html'
	
	actions = [archive_seleted,]
	
	def changelist_view(self, request, extra_context=None):
		extra_context = {'nav': 'all_leave_requests'}
		return super(LeaveRequestAdmin, self).changelist_view(request, extra_context)
	
	
admin.site.register(LeaveRequest, LeaveRequestAdmin)

admin.site.register(LeaveType)