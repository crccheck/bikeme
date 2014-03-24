from django.contrib import admin

from . import models


admin.site.register(models.Market)


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'market', 'capacity', 'active', )
    list_filter = ('market', 'active', )
    search_fields = ('name', )
admin.site.register(models.Station, StationAdmin)


class SnapshotAdmin(admin.ModelAdmin):
    date_heirarchy = 'timestamp'
    list_display = ('station', 'bikes', 'docks', 'timestamp')
    ordering = ('-timestamp', )
admin.site.register(models.Snapshot, SnapshotAdmin)
