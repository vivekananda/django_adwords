from django import forms

class DocumentUploadForm(forms.Form):
    csvfile = forms.FileField(label='Csv file',)
#    client     = forms.ChoiceField(label="Client", widget=forms.ChoiceField("ATC"), required=False)