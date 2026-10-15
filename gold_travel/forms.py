from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from company_profile.models import TblCompanyProduction
from production_control.models import GoldProductionFormAlloy

from gold_travel.models import AppGoldStorageCompanies, AppGoldStorageCompaniesDetails, TblStateRepresentative

UserModel = get_user_model()

class TblStateRepresentativeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserModel.objects.filter(groups__name__in=('gold_travel_state','gold_travel_ssmo')), label=_("user"))
    # def __init__(self, *args, **kwargs):        
    #     super().__init__(*args, **kwargs)

    class Meta:
        model = TblStateRepresentative    
        fields = ["user","name","state","authority"] 

class ImportDetailsCSVForm(forms.Form):
    csv_file = forms.FileField(
        label=_("CSV file"),
        help_text=_("CSV file with columns: id, weight, shape type. Shape type: مستطيل/rectangular/1 or دائري/circular/2")
    )
    selected_action = forms.CharField(widget=forms.HiddenInput)
    replace_existing = forms.BooleanField(
        label=_("Replace existing details"),
        required=False,
        initial=False,
        help_text=_("If checked, delete all existing details for the selected forms before importing")
    )

    SHAPE_MAP = {
        'مستطيل': 1, 'مستطيلة': 1, 'rectangular': 1, '1': 1,
        'دائري': 2, 'دائرى': 2, 'circular': 2, '2': 2,
    }

    def clean_csv_file(self):
        import csv
        import codecs
        
        f = self.cleaned_data['csv_file']
        try:
            # Try UTF-8 with BOM first
            f.seek(0)
            raw = f.read()
            if raw.startswith(codecs.BOM_UTF8):
                decoded = raw.decode('utf-8-sig')
            else:
                decoded = raw.decode('utf-8')
            
            reader = csv.DictReader(decoded.splitlines())
            rows = list(reader)
            
            if not rows:
                raise forms.ValidationError(_("CSV file is empty"))
            
            # Validate headers
            required_fields = {'id', 'weight', 'shape type'}
            actual_fields = set(reader.fieldnames or [])
            missing = required_fields - actual_fields
            if missing:
                raise forms.ValidationError(
                    _("Missing columns: %(cols)s. Expected: id, weight, shape type")
                    % {'cols': ', '.join(sorted(missing))}
                )
            
            # Validate each row
            errors = []
            valid_rows = []
            for i, row in enumerate(rows, start=2):
                row_errors = []
                
                alloy_id = row.get('id', '').strip()
                if not alloy_id:
                    row_errors.append(_("id is empty"))
                elif len(alloy_id) > 20:
                    row_errors.append(_("id too long (max 20 chars)"))
                
                weight_raw = row.get('weight', '').strip()
                try:
                    weight = float(weight_raw)
                    if weight <= 0:
                        row_errors.append(_("weight must be positive"))
                except (ValueError, TypeError):
                    row_errors.append(_("invalid weight: '%(val)s'") % {'val': weight_raw})
                
                shape_raw = row.get('shape type', '').strip()
                shape_val = self.SHAPE_MAP.get(shape_raw.lower() if shape_raw else '')
                if shape_val is None:
                    row_errors.append(
                        _("invalid shape type: '%(val)s'. Use: مستطيل/rectangular/1 or دائري/circular/2")
                        % {'val': shape_raw}
                    )
                
                if row_errors:
                    errors.append(_("Row %(row)s: %(err)s") % {'row': i, 'err': '; '.join(row_errors)})
                else:
                    valid_rows.append({
                        'alloy_id': alloy_id,
                        'alloy_weight_in_gram': weight,
                        'alloy_shape': shape_val,
                    })
            
            if errors:
                raise forms.ValidationError(errors)
            
            return valid_rows
        except forms.ValidationError:
            raise
        except Exception as e:
            raise forms.ValidationError(_("Could not read CSV file: %(err)s") % {'err': str(e)}) 

class CompanyByTypeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return TblCompanyProduction.objects.none()

        qs = TblCompanyProduction.objects.all()

        company_type = self.forwarded.get('company_type', None)
        if company_type:
            qs = qs.filter(company_type=company_type)

        if self.q:
            qs = qs.filter(name_ar__icontains=self.q) | qs.filter(name_en__icontains=self.q)

        return qs

class AppGoldStorageCompaniesForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=TblCompanyProduction.objects.all(),
        label=_("company"),
        widget=autocomplete.ModelSelect2(url='admin:lkp_company_by_type', forward=['company_type'])
    )

    class Meta:
        model = AppGoldStorageCompanies
        fields = "__all__"

class AlloySelectWidget(forms.Select):
    weight_map = {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:
            option['attrs']['data-weight'] = self.weight_map.get(str(value), '')
        return option

class AppGoldStorageCompaniesDetailsForm(forms.ModelForm):
    alloy_serial_no = forms.ModelChoiceField(
        queryset=GoldProductionFormAlloy.objects.none(),
        label=_("alloy_serial_no"),
        widget=AlloySelectWidget(),
    )
    company_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        company_id = self.company_id
        if self.data is not None:
            posted_company = self.data.get('company') or None
            company_id = posted_company or company_id

        qs = GoldProductionFormAlloy.objects.select_related('master').all()
        if company_id:
            qs = qs.filter(master__company_id=company_id)
        else:
            qs = qs.none()

        self.fields["alloy_serial_no"].queryset = qs
        self.fields["alloy_serial_no"].widget.weight_map = {str(obj.pk): obj.alloy_weight for obj in qs}

    class Meta:
        model = AppGoldStorageCompaniesDetails
        fields = ["alloy_serial_no","net_weight","karat"]
