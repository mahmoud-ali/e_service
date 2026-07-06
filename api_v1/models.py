from django.db import models


class DeductionsView(models.Model):
    """
    Unmanaged model backing the deductions_view in the external 'deductions' database.
    """
    tdate = models.DateField()
    companyid = models.IntegerField()
    company_name = models.CharField(max_length=255)
    produced_gold = models.DecimalField(max_digits=18, decimal_places=4)
    pure_gold = models.DecimalField(max_digits=18, decimal_places=4)
    deduction_weight = models.DecimalField(max_digits=18, decimal_places=4)
    net_weight = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta:
        managed = False
        db_table = "deductions_view"
        ordering = ["-tdate"]

    def __str__(self):
        return f"Deduction {self.id} — {self.company_name} ({self.tdate})"
