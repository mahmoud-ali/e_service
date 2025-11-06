from django import forms
from django.forms import inlineformset_factory
from .models import NeedsRequest, Item

class NeedsRequestForm(forms.ModelForm):
    class Meta:
        model = NeedsRequest
        fields = [
            'date',
            'sd_comment',
            'doa_comment',
            'it_comment',
            'dgdhra_recommendation',
            'dgfa_recommendation',
        ]

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input input-bordered w-full',
                }
            ),
        }

class CommentForm(forms.ModelForm):
    sd_comment = forms.CharField(
        label='تعليق قسم الإمداد',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered', 
            'placeholder': 'أدخل التعليق...'
        }),
        required=True,
        error_messages={
            'required': 'هذا الحقل مطلوب'
        }
    )
    class Meta:
        model = NeedsRequest
        fields = ['sd_comment']

class DOACommentForm(forms.ModelForm):
    doa_comment = forms.CharField(
        label='تعليق مدير الشؤون الإدارية',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered', 
            'placeholder': 'أدخل التعليق...'
        }),
        required=True,
        error_messages={
            'required': 'هذا الحقل مطلوب'
        }
    )
    class Meta:
        model = NeedsRequest
        fields = ['doa_comment']

class ITCommentForm(forms.ModelForm):
    it_comment = forms.CharField(
        label='تعليق مدير تقنية المعلومات',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered', 
            'placeholder': 'أدخل التعليق...'
        }),
        required=True,
        error_messages={
            'required': 'هذا الحقل مطلوب'
        }
    )
    class Meta:
        model = NeedsRequest
        fields = ['it_comment']

class DGDHRARecommendationForm(forms.ModelForm):
    dgdhra_recommendation = forms.CharField(
        label='توصية مدير الإدارة العامة للموارد البشرية والإدارية',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered', 
            'placeholder': 'أدخل التوصية...'
        }),
        required=True,
        error_messages={
            'required': 'هذا الحقل مطلوب'
        }
    )
    class Meta:
        model = NeedsRequest
        fields = ['dgdhra_recommendation']

class DGFARecommendationForm(forms.ModelForm):
    dgfa_recommendation = forms.CharField(
        label='توصية مدير الإدارة العامة للشؤون المالية',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered', 
            'placeholder': 'أدخل التوصية...'
        }),
        required=True,
        error_messages={
            'required': 'هذا الحقل مطلوب'
        }
    )
    class Meta:
        model = NeedsRequest
        fields = ['dgfa_recommendation']

class RejectionForm(forms.Form):
    rejection_cause = forms.CharField(
        label='سبب الرفض',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered', 
            'placeholder': 'أدخل سبب الرفض...'
        }),
        required=True,
        error_messages={
            'required': 'يجب إدخال سبب الرفض'
        }
    )

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['id','requested_item']

        widgets = {
            'requested_item': forms.Select(attrs={'class': 'select input input-bordered w-full '}),
        }
# class ApprovedItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ['approved_item_name']

ItemFormSet = inlineformset_factory(NeedsRequest, Item, form=ItemForm, extra=1, can_delete=True)
# ApprovedItemFormSet = inlineformset_factory(NeedsRequest, Item, form=ApprovedItemForm, extra=0)
