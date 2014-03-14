from django.db import models


class Market(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, unique=True)

    def __unicode__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=60)
    market = models.ForeignKey(Market, related_name='stations')
    # store points as decimals to avoid postgis requirement
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    street = models.CharField(max_length=120)
    zip = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name
