from django import forms


class LongText(forms.TextInput):
    template_name = "forms/NEXT_input_textarea.html"
