# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Employee.test_field'
        db.delete_column('maitenance_employee', 'test_field')


    def backwards(self, orm):
        
        # Adding field 'Employee.test_field'
        db.add_column('maitenance_employee', 'test_field', self.gf('django.db.models.fields.CharField')(default='test', max_length=75), keep_default=False)


    models = {
        'leave.leavetype': {
            'Meta': {'object_name': 'LeaveType'},
            'build_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_days': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'}),
            'notifyadmin': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'maitenance.adjustmentdays': {
            'Meta': {'object_name': 'AdjustmentDays'},
            'adjustment_days': ('django.db.models.fields.FloatField', [], {}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Employee']"}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leave_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['leave.LeaveType']"}),
            'month': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'maitenance.admin': {
            'Meta': {'object_name': 'Admin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'})
        },
        'maitenance.department': {
            'Meta': {'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'}),
            'supervisor': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'maitenance.employee': {
            'Meta': {'object_name': 'Employee'},
            'al_entitlement': ('django.db.models.fields.FloatField', [], {}),
            'approvers': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'balanced_days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'balanced_forward': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cc_to': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'chinese_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employees'", 'blank': 'True', 'null': 'True', 'to': "orm['maitenance.Department']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'domain_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_administrative_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'join_date': ('django.db.models.fields.DateField', [], {}),
            'last_login_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'}),
            'sl_entitlement': ('django.db.models.fields.FloatField', [], {}),
            'start_fiscal_date': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_members'", 'blank': 'True', 'null': 'True', 'to': "orm['maitenance.Team']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'maitenance.maintenancelog': {
            'Meta': {'object_name': 'MaintenanceLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'maitenance.team': {
            'Meta': {'object_name': 'Team'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'})
        }
    }

    complete_apps = ['maitenance']
