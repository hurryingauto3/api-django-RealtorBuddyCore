# forms.py
from django import forms
from .models import Building

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'  # You can specify the fields you want to include