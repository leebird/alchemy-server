from django import forms

class SearchPubMedForm(forms.Form):
    query = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control',
               'placeholder': 'Input gene names or PMIDs, e.g., "BAD", "22587342, 23981989"',
               'cols': '40',
               'rows': '5'}),
                            label='')

class SearchDocForm(forms.Form):
    docids = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control',
               'placeholder': 'Input PMIDs separated by comma, space or newline',
               'cols': '40',
               'rows': '5'}),
                             label='')
