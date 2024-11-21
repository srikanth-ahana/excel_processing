from django import forms
from .models import UploadedFile

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'file2']
        labels = {
                    'file': 'Upload Arrival File',  
                    'file2': 'Upload Vendor File'  
                }