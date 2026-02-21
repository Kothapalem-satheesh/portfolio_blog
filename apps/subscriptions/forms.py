from django import forms


class SubscribeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}))
