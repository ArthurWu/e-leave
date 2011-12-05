from django.forms import ModelForm, Textarea
from django import forms
from models import *

class CreateLeaveRequestForm(ModelForm):
	widget=forms.Textarea
	class Meta:
		model = LeaveRequest
		fields = ('employee','leave_type', 'status', 'days', 'comments')
		widgets = {
			'comments': Textarea(attrs={'cols': 80, 'rows': 5}),
		}

	