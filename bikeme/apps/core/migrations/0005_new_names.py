# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for station in orm.Station.objects.filter(
                market__slug='nyc', name__contains=' - '):
            try:
                new_name = station.name.split(' - ', 2)[1]
            except IndexError:
                pass
            else:
                station.name = new_name
                station.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        # NOPE
        pass

    models = {
        u'core.market': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Market'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'core.snapshot': {
            'Meta': {'ordering': "('timestamp',)", 'object_name': 'Snapshot'},
            'bikes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'docks': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['core.Station']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'core.station': {
            'Meta': {'ordering': "('market', 'name')", 'unique_together': "(('slug', 'market'),)", 'object_name': 'Station'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'capacity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_snapshot': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'+'", 'unique': 'True', 'null': 'True', 'to': u"orm['core.Snapshot']"}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '5'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '5'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': u"orm['core.Market']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['core']
    symmetrical = True
