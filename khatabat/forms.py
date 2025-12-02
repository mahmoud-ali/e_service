from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget,FilteredSelectMultiple

from khatabat.models import HarkatKhatabat, HarkatKhatabatInbox, HarkatKhatabatOutbox, MaktabTanfiziJiha

jiha_none = MaktabTanfiziJiha.objects.none() #MaktabTanfiziJiha.objects.filter(maktab_tanfizi=obj.maktab_tanfizi)
jiha_all_qs = MaktabTanfiziJiha.objects.all()

class HarkatKhatabatInboxAdminForm(ModelForm):
    request = None
    qs = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.request:
            try:
                self.fields["source_entity"].queryset = self.qs
            except:
                self.fields["source_entity"].queryset = self.qs.none()

    class Meta:
        model = HarkatKhatabatInbox
        fields = ["date","source_entity","letter_attachment","delivery_date","note"]
        widgets = {
            "date":AdminDateWidget(),
            "delivery_date":AdminDateWidget(),
        }

class HarkatKhatabatOutboxAdminForm(ModelForm):
    request = None
    qs = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["forwarded_to"].required=False

        if self.request:
            try:
                self.fields["source_entity"].queryset = self.qs
                self.fields["forwarded_to"].queryset = self.qs
            except:
                self.fields["source_entity"].queryset = self.qs.none()
                self.fields["forwarded_to"].queryset = self.qs.none()

    class Meta:
        model = HarkatKhatabatOutbox
        fields = ["date","source_entity","procedure","forward_date","forwarded_to","letter_attachment","delivery_date","note"]
        widgets = {
            "date":AdminDateWidget(),
            "forward_date":AdminDateWidget(),
            "forwarded_to":FilteredSelectMultiple('الجهة المحول لها', is_stacked=False),
            "delivery_date":AdminDateWidget(),
        }

