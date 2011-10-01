from django import forms

class NewHS(forms.Form):
    username = forms.CharField(min_length=3, max_length=20, label="username",
                    widget=forms.TextInput())
class GameOver(forms.Form):
    count = forms.CharField(min_length=1, max_length=2)
