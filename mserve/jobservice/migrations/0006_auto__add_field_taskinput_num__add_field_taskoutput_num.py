# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'TaskInput.num'
        db.add_column('jobservice_taskinput', 'num', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'TaskOutput.num'
        db.add_column('jobservice_taskoutput', 'num', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'TaskInput.num'
        db.delete_column('jobservice_taskinput', 'num')

        # Deleting field 'TaskOutput.num'
        db.delete_column('jobservice_taskoutput', 'num')


    models = {
        'dataservice.dataservice': {
            'Meta': {'ordering': "['-created']", 'object_name': 'DataService', '_ormbases': ['dataservice.NamedBase']},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.HostingContainer']", 'null': 'True', 'blank': 'True'}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subservices'", 'null': 'True', 'to': "orm['dataservice.DataService']"}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'dataservice.hostingcontainer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'HostingContainer', '_ormbases': ['dataservice.NamedBase']},
            'default_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'default_profile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dataservice.mfile': {
            'Meta': {'ordering': "('-created', 'name')", 'object_name': 'MFile', '_ormbases': ['dataservice.NamedBase']},
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFile']", 'null': 'True'}),
            'empty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFolder']", 'null': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'poster': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'proxy': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.DataService']"}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dataservice.mfolder': {
            'Meta': {'ordering': "['-created']", 'object_name': 'MFolder', '_ormbases': ['dataservice.NamedBase']},
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'duplicated_from'", 'null': 'True', 'to': "orm['dataservice.MFolder']"}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFolder']", 'null': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.DataService']"})
        },
        'dataservice.namedbase': {
            'Meta': {'ordering': "['-created']", 'object_name': 'NamedBase'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'initial_usage_recorded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reportnum': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dataservice.Usage']", 'symmetrical': 'False'})
        },
        'dataservice.usage': {
            'Meta': {'object_name': 'Usage'},
            'base': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.NamedBase']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'nInProgress': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.FloatField', [], {}),
            'rateCumulative': ('django.db.models.fields.FloatField', [], {}),
            'rateTime': ('django.db.models.fields.DateTimeField', [], {}),
            'reports': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'squares': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'jobservice.job': {
            'Meta': {'ordering': "('-created', 'name')", 'object_name': 'Job', '_ormbases': ['dataservice.NamedBase']},
            'mfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFile']"}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'taskset_id': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'jobservice.jobasyncresult': {
            'Meta': {'object_name': 'JobASyncResult'},
            'async_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobservice.Job']"})
        },
        'jobservice.joboutput': {
            'Meta': {'ordering': "['-created']", 'object_name': 'JobOutput', '_ormbases': ['dataservice.NamedBase']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobservice.Job']"}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        'jobservice.taskdescription': {
            'Meta': {'object_name': 'TaskDescription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'jobservice.taskinput': {
            'Meta': {'object_name': 'TaskInput'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'taskdescription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inputs'", 'to': "orm['jobservice.TaskDescription']"})
        },
        'jobservice.taskoption': {
            'Meta': {'object_name': 'TaskOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'taskdescription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'to': "orm['jobservice.TaskDescription']"})
        },
        'jobservice.taskoutput': {
            'Meta': {'object_name': 'TaskOutput'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'taskdescription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outputs'", 'to': "orm['jobservice.TaskDescription']"})
        },
        'jobservice.taskresult': {
            'Meta': {'object_name': 'TaskResult'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'taskdescription': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['jobservice.TaskDescription']"})
        }
    }

    complete_apps = ['jobservice']
