from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget

from khatabat.models import HarkatKhatabat, MaktabTanfiziJiha

jiha_none = MaktabTanfiziJiha.objects.none() #MaktabTanfiziJiha.objects.filter(maktab_tanfizi=obj.maktab_tanfizi)
jiha_all_qs = MaktabTanfiziJiha.objects.all()

class KhatabatAdminForm(ModelForm):
    request = None
    source_entity = forms.ModelChoiceField(queryset=jiha_none, label="جهة الخطاب")
    forwarded_to = forms.ModelChoiceField(queryset=jiha_none, label="الجهة المحول لها",required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.request:
            maktab = self.request.user.maktab_tanfizi_user
            self.fields["source_entity"].queryset = jiha_all_qs.filter(maktab_tanfizi=maktab)
            self.fields["forwarded_to"].queryset = jiha_all_qs.filter(maktab_tanfizi=maktab)

    class Meta:
        model = HarkatKhatabat
        fields = ["movement_type","date","source_entity","procedure","letter_attachment","forwarded_to","forward_date","delivery_date","followup_result","followup_attachment",]
        widgets = {
            "date":AdminDateWidget(),
            "forward_date":AdminDateWidget(),
            "delivery_date":AdminDateWidget(),
        }

