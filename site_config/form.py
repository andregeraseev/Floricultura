from django import forms
from .models import ContactInfo


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = '__all__'

    def clean(self):
        # Aqui você pode adicionar suas validações personalizadas
        cleaned_data = super().clean()
        # Exemplo: validar o formato do telefone ou email
        return cleaned_data
