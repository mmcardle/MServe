# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Relationship'
        db.create_table('dataservice_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('entity1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_left', to=orm['dataservice.MFile'])),
            ('entity2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_right', to=orm['dataservice.MFile'])),
        ))
        db.send_create_signal('dataservice', ['Relationship'])


    def backwards(self, orm):
        
        # Deleting model 'Relationship'
        db.delete_table('dataservice_relationship')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dataservice.auth': {
            'Meta': {'object_name': 'Auth'},
            'authname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'base': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.NamedBase']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.Auth']", 'null': 'True', 'blank': 'True'}),
            'roles_csv': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dataservice.Usage']", 'symmetrical': 'False'})
        },
        'dataservice.backupfile': {
            'Meta': {'ordering': "['-created']", 'object_name': 'BackupFile', '_ormbases': ['dataservice.NamedBase']},
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '400'}),
            'mfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFile']"}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dataservice.dataservice': {
            'Meta': {'ordering': "['-created']", 'object_name': 'DataService', '_ormbases': ['dataservice.NamedBase']},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.HostingContainer']", 'null': 'True', 'blank': 'True'}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subservices'", 'null': 'True', 'to': "orm['dataservice.DataService']"}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'dataservice.dataserviceprofile': {
            'Meta': {'object_name': 'DataServiceProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profiles'", 'to': "orm['dataservice.DataService']"})
        },
        'dataservice.dataservicetask': {
            'Meta': {'object_name': 'DataServiceTask'},
            'args': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'taskset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['dataservice.DataServiceTaskSet']"})
        },
        'dataservice.dataservicetaskset': {
            'Meta': {'ordering': "['order']", 'object_name': 'DataServiceTaskSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasksets'", 'to': "orm['dataservice.DataServiceWorkflow']"})
        },
        'dataservice.dataserviceworkflow': {
            'Meta': {'object_name': 'DataServiceWorkflow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workflows'", 'to': "orm['dataservice.DataServiceProfile']"})
        },
        'dataservice.hostingcontainer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'HostingContainer', '_ormbases': ['dataservice.NamedBase']},
            'default_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'default_profile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dataservice.managementproperty': {
            'Meta': {'object_name': 'ManagementProperty'},
            'base': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.NamedBase']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'duplicated_from'", 'null': 'True', 'to': "orm['dataservice.MFolder']"}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFolder']", 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.DataService']"})
        },
        'dataservice.mserveprofile': {
            'Meta': {'object_name': 'MServeProfile'},
            'auths': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'profileauths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dataservice.Auth']"}),
            'bases': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bases'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dataservice.NamedBase']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
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
        'dataservice.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'entity1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_left'", 'to': "orm['dataservice.MFile']"}),
            'entity2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_right'", 'to': "orm['dataservice.MFile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dataservice.remotemserveservice': {
            'Meta': {'object_name': 'RemoteMServeService'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'dataservice.servicerequest': {
            'Meta': {'ordering': "['-time']", 'object_name': 'ServiceRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'servicerequests'", 'null': 'True', 'to': "orm['dataservice.MServeProfile']"}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['dataservice']
