from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget,FilteredSelectMultiple

from khatabat.models import HarkatKhatabat, MaktabTanfiziJiha

jiha_none = MaktabTanfiziJiha.objects.none() #MaktabTanfiziJiha.objects.filter(maktab_tanfizi=obj.maktab_tanfizi)
jiha_all_qs = MaktabTanfiziJiha.objects.all()

class KhatabatAdminForm(ModelForm):
    request = None
    qs = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields["forwarded_to"].required=False

        if self.request:
            try:
                self.fields["source_entity"].queryset = self.qs
                self.fields["forwarded_to"].queryset = self.qs
            except:
                self.fields["source_entity"].queryset = self.qs.none()
                self.fields["forwarded_to"].queryset = self.qs.none()

    class Meta:
        model = HarkatKhatabat
        fields = ["movement_type","date","source_entity","procedure","letter_attachment","forwarded_to","forward_date","delivery_date","followup_result","followup_attachment","note"]
        widgets = {
            "date":AdminDateWidget(),
            "forward_date":AdminDateWidget(),
            "forwarded_to":FilteredSelectMultiple('الجهة المحول لها', is_stacked=False),
            "delivery_date":AdminDateWidget(),
        }

