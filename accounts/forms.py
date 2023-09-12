from django import forms

class Information(forms.Form):
    Avatar = forms.ImageField()
    Facebook = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "Facebook"}))
    Email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': "Email"}))
    Phone = forms.IntegerField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "Phone"}))
   