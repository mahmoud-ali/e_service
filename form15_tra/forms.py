from django import forms
from form15_tra.models import CollectionForm

class CollectionFormModelForm(forms.ModelForm):
    """
    Form for creating and editing Collection Forms.
    """
    class Meta:
        model = CollectionForm
        fields = ['miner_name', 'sacks_count',] #, 'total_amount'
        labels = {
            'miner_name': 'اسم العميل / المعدن',
            'sacks_count': 'عدد الجوالات',
            # 'total_amount': 'المبلغ الإجمالي',
        }
        widgets = {
            'miner_name': forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right'}),
            'sacks_count': forms.NumberInput(attrs={'step': '0.01','class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-left', 'dir': 'ltr'}), # Numbers often LTR even in RTL
            # 'total_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-left', 'dir': 'ltr'}),
            'market': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-right'}),
        }
