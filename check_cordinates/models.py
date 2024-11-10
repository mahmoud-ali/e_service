from django.contrib.gis.db import models

class SmallMining(models.Model):
    license_nu = models.CharField(max_length=254,null=True)
    company_name = models.CharField(max_length=100,null=True)
    state = models.CharField(max_length=50,blank=True,null=True)
    mineral = models.CharField(max_length=50,blank=True,null=True)
    valid = models.CharField(max_length=50,blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    area = models.FloatField(blank=True,null=True)
    nots = models.CharField(max_length=150,blank=True,null=True)
    geom = models.MultiPolygonField(srid=32636)

    def __str__(self):
        return self.geom.ewkt