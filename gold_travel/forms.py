from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gold_travel.models import TblStateRepresentative

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
    _selected_action = forms.CharField(widget=forms.HiddenInput)
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
