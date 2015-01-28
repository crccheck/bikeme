# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Snapshot', fields ['station', 'timestamp']
        db.create_unique(u'core_snapshot', ['station_id', 'timestamp'])


        # Changing field 'Station.latest_snapshot'
        db.alter_column(u'core_station', 'latest_snapshot_id', self.gf('django.db.models.fields.related.OneToOneField')(null=True, on_delete=models.SET_NULL, to=orm['core.Snapshot'], unique=True))

    def backwards(self, orm):
        # Removing unique constraint on 'Snapshot', fields ['station', 'timestamp']
        db.delete_unique(u'core_snapshot', ['station_id', 'timestamp'])


        # Changing field 'Station.latest_snapshot'
        db.alter_column(u'core_station', 'latest_snapshot_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, null=True, to=orm['core.Snapshot']))

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
            'Meta': {'ordering': "('timestamp',)", 'unique_together': "(('station', 'timestamp'),)", 'object_name': 'Snapshot'},
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
            'latest_snapshot': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Snapshot']", 'blank': 'True', 'unique': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '6'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '6'}),
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