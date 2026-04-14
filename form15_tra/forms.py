from django import forms
from form15_tra.models import CollectionForm

class CollectionFormModelForm(forms.ModelForm):
    """
    Form for creating and editing Collection Forms.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            input_id = field.widget.attrs.get("id") or f"id_{name}"
            describedby = f"{input_id}_help {input_id}_error"
            field.widget.attrs.setdefault("aria-describedby", describedby)
            if self.is_bound:
                field.widget.attrs["aria-invalid"] = "true" if self.errors.get(name) else "false"

    class Meta:
        model = CollectionForm
        fields = ['miner_name', 'phone', 'sacks_count', 'arrival_source', 'vehicle_plate',] #, 'total_amount'
        labels = {
            'miner_name': 'اسم العميل / المعدن',
            'phone': 'رقم الهاتف',
            'arrival_source': 'جهة القدوم',
            'vehicle_plate': 'لوحة العربة',
            'sacks_count': 'عدد الجوالات',
            # 'total_amount': 'المبلغ الإجمالي',
        }
        widgets = {
            'miner_name': forms.TextInput(attrs={'class': 'block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right'}),
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'autocomplete': 'tel',
                'class': 'block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right',
                'dir': 'ltr',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
                'maxlength': '10',
            }),
            'arrival_source': forms.TextInput(attrs={'class': 'block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right'}),
            'vehicle_plate': forms.TextInput(attrs={'class': 'block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right'}),
            'sacks_count': forms.NumberInput(attrs={
                'class': 'block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right',
                'dir': 'ltr',
                'inputmode': 'numeric',
                'min': '0',
                'step': '1',
            }), # Numbers often LTR even in RTL
            # 'total_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-left', 'dir': 'ltr'}),
            'market': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right'}),
        }
