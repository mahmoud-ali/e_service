from django.contrib.gis.db import models

class SmallMining(models.Model):
    OBJECTID = models.AutoField(primary_key=True,serialize=True)
    license_nu = models.CharField(max_length=254,null=True)
    company_name = models.CharField(max_length=100,null=True)
    state = models.CharField(max_length=50,blank=True,null=True)
    mineral = models.CharField(max_length=50,blank=True,null=True)
    valid = models.CharField(max_length=50,blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    area = models.FloatField(blank=True,null=True)
    nots = models.CharField(max_length=150,blank=True,null=True)
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f'{self.company_name} ({self.license_nu}) {self.geom.ewkt}'
    
class OsmanState(models.Model):
    OBJECTID = models.AutoField(primary_key=True,serialize=True)
    scode = models.CharField(max_length=4,null=True,blank=True)
    source = models.CharField(max_length=50,null=True,blank=True)
    name_arb = models.CharField(max_length=50,null=True,blank=True)
    state = models.CharField(max_length=40,null=True,blank=True)
    adm2_ne = models.CharField(max_length=2,null=True,blank=True)
    cnt_will_i = models.BigIntegerField(null=True,blank=True)
    adm2_na = models.CharField(max_length=25,null=True,blank=True)
    adm2 = models.IntegerField(null=True,blank=True)
    smrc_amm_d = models.FloatField(null=True,blank=True)
    areakm2 = models.FloatField(null=True,blank=True)
    areakm2z35 = models.FloatField(null=True,blank=True)
    shape_leng = models.FloatField(null=True,blank=True)
    shape_area = models.FloatField(null=True,blank=True)
    shape = models.PolygonField(srid=4326)

    def __str__(self):
        return f'{self.name_arb} ({self.scode})'
    