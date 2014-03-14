from django.db import models
from django.utils.text import slugify


class Market(models.Model):
    """A market where bikes can be found, usually a city."""
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, unique=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = slugify(self.name)
        super(Market, self).save(*args, **kwargs)


class Station(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60)
    market = models.ForeignKey(Market, related_name='stations')
    # store points as decimals to avoid postgis requirement
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    street = models.CharField(max_length=120)
    zip = models.CharField(max_length=5)
    state = models.CharField(max_length=2)

    class Meta:
        unique_together = ('slug', 'market', )

    def __unicode__(self):
        return u'{}, {}'.format(self.name, self.market)

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = slugify(self.name)
        super(Station, self).save(*args, **kwargs)


class StationSnapshot(models.Model):
    STATUS_CHOICES = (
        ('active', 'active'),
        # TODO
    )
    station = models.ForeignKey(Station, related_name='history')
    timestamp = models.DateTimeField()
    bikes = models.PositiveSmallIntegerField(default=0)
    docks = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __unicode__(self):
        return u'{} {}/{} {}'.format(self.station, self.bikes,
            self.docks,
            self.timestamp.strftime('%Y-%m-%d %H:%M'),
        )

    class Meta:
        ordering = ('timestamp', )
