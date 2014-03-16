from django.contrib import admin

from . import models


admin.site.register(models.Market)


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'market', 'capacity', 'active', )
    list_filter = ('market', 'active', )
admin.site.register(models.Station, StationAdmin)


class SnapshotAdmin(admin.ModelAdmin):
    date_heirarchy = 'timestamp'
    list_display = ('station', 'bikes', 'docks', 'timestamp')
    # WISHLIST select_related the list_filter queryset
    list_filter = ('station', )
admin.site.register(models.Snapshot, SnapshotAdmin)
