from django import forms

class PointCordinateForm(forms.Form):
    x = forms.FloatField(label="Long/ East/ X")
    y = forms.FloatField(label="Lat/ West/ Y")