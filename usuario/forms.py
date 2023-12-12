from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.core.exceptions import ValidationError
import re
import phonenumbers
from phonenumbers import NumberParseException
from validate_docbr import CPF
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, HTML, Div, Submit, Button



def validate_cpf(value):
    cpf = CPF()
    if not cpf.validate(value):
        raise ValidationError('CPF inválido.')




def validate_phone(value):
    try:
        number = phonenumbers.parse(value, 'BR')  # 'BR' é o código do país para o Brasil
        if not phonenumbers.is_valid_number(number):
            print(number,'invalido')
            raise ValidationError('Número de telefone inválido.')
    except NumberParseException:
        print(number, 'invalido')
        raise ValidationError('Número de telefone inválido.')


class UserPhoneForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=False, validators=[validate_phone])
    whatsapp = forms.CharField(max_length=15, required=False, validators=[validate_phone])

    class Meta:
        model = User
        fields = ('phone_number', 'whatsapp')

    def __init__(self, *args, **kwargs):
        print('iniciando form', args, kwargs)

        super(UserPhoneForm, self).__init__(*args, **kwargs)
        print('iniciando form', args, kwargs)
        print('initial',self.initial)
        print('initial',self.data)

        # Desabilita o campo phone_number se ele não estiver presente nos dados enviados
        if 'phone_number' in self.data:
            self.fields['phone_number'].disabled = False
        else:
            self.fields['phone_number'].disabled = True

        # Desabilita o campo whatsapp se ele não estiver presente nos dados enviados
        if 'whatsapp' in self.data:
            self.fields['whatsapp'].disabled = False
        else:
            self.fields['whatsapp'].disabled = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Informações Adicionais",
                Div(
                    Field('phone_number', css_class='', data_mask='(00) 0000-00000', wrapper_class="col-8",
                          placeholder='Numero de Telefone', id="id_phone_number", disabled=True),
                    HTML(
                        '<button type="button" class="btn btn-primary mb-3" onclick="habilitaCampo(\'#id_phone_number\')"><i class="fa fa-pencil-alt"></i></button>'),
                    css_class='form-row align-items-end',
                ),
                Div(
                    Field('whatsapp', css_class='', wrapper_class="col-8", data_mask='(00) 0000-00000',
                          placeholder='Whatsapp', id="id_whatsapp", disabled=True),
                    HTML(
                        '<button type="button" class="btn btn-primary mb-3" onclick="habilitaCampo(\'#id_whatsapp\')"><i class="fa fa-pencil-alt"></i></button>'),
                    css_class='form-row align-items-end',
                ),
                Submit('submit', 'Salvar', css_class='btn btn-primary d-none', id="id_submit_celular")
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.filter(user__email=user).update(
                phone_number=self.cleaned_data['phone_number'],
                whatsapp=self.cleaned_data['whatsapp'],
            )
        return user



class UserRegistrationForm(UserCreationForm):
    cpf = forms.CharField(max_length=14, required=True, validators=[validate_cpf])
    celular = forms.CharField(max_length=15, required=False, validators=[validate_phone])
    whatsapp = forms.CharField(max_length=15, required=False, validators=[validate_phone])
    data_de_nascimento = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    genero = forms.ChoiceField(choices=[('male', 'Masculino'), ('female', 'Feminino'), ('other', 'Outros')], required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if UserProfile.objects.filter(cpf=cpf).exists():
            raise ValidationError("CPF já cadastrado.")
        return cpf

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Fieldset(

                "Dados do Usuário",
                Field('username', css_class='', wrapper_class="", placeholder='Usuario', autofocus=True, required=True,oninput="verificaUsername(this)", help_text='O nome de usuário deve conter apenas letras, números e os caracteres @/./+/-/_',),
                Div(
                    Field('first_name', css_class='', wrapper_class="col-6", placeholder='Primeiro nome', required=True),
                    Field('last_name', css_class='', wrapper_class="col-6", placeholder='Sobrenome', required=True),
                    css_class='form-row',

                    ),

                Field('email', css_class='', placeholder='E-mail',required=True),

                # Adicione mais campos aqui
            ),
            # Div(
            #     HTML("<p>Informações Adicionais</p>"),
            #     'cpf',
            #     'phone_number',
            #     'whatsapp',
            #     'password1',
            #     'password2',
            #     css_class='classe-css-div'
            # ),
            Fieldset(
                "Informações Adicionais",
                Field('cpf', css_class='', wrapper_class="", data_mask='000.000.000-00', placeholder='Número do CPF', required=True, oninput="this.setCustomValidity(validaCPF(this) ? '' : 'CPF inválido');" ),

                Div(
                    Field('celular', css_class='', data_mask='(00) 0000-00000', wrapper_class="col-6",
                          placeholder='Numero de Telefone'),
                    Field('whatsapp', css_class='', wrapper_class="col-6", data_mask='(00) 0000-00000',
                          placeholder='Whatsapp'),
                    css_class='form-row',

                ),
                Div(
                    Field('data_de_nascimento', css_class='', wrapper_class="col-6", placeholder='Data de Nascimento'),
                    Field('genero', css_class='', wrapper_class="col-6", placeholder='Genero'),
                    css_class='form-row',

                ),

                Field('password1', css_class='', placeholder='Senha', oninput="this.setCustomValidity(validaSenha(this.value) ? '' : 'Senha Fraca');" ),
                Field('password2', css_class='', wrapper_class="", placeholder='Confirmar Senha'),

                # Adicione mais campos aqui
            ),
            Submit('submit', 'Registrar', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                cpf=self.cleaned_data['cpf'],
                phone_number=self.cleaned_data['celular'],
                whatsapp=self.cleaned_data['whatsapp'],
                birth_date=self.cleaned_data['data_de_nascimento'],
                gender=self.cleaned_data['genero'],
                # Adicione outros campos conforme necessário
            )
        return user


from django import forms
from .models import Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div, Submit
import requests

from django import forms
from .models import Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div, Submit
import requests

class AddressForm(forms.ModelForm):

    # destinatario = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Destinatário'}))
    # rua = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Rua'}))
    # numero = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'placeholder': 'Número'}))
    # bairro = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Bairro'}))
    # cidade = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Cidade'}))
    # estado = forms.ChoiceField(choices=[
    #     ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    #     ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    #     ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    #     ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    #     ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    #     ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    #     ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
    # ], required=True)
    # # cep = forms.CharField(max_length=9, widget=forms.TextInput(attrs={'placeholder': 'CEP'}))
    # complemento = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'Complemento'}))


    class Meta:
        model = Address
        fields = ['destinatario', 'cpf_destinatario', 'rua', 'numero','cep','bairro','cidade', 'estado', 'complemento']


    def clean_cpf_destinatario(self):
        cpf = CPF()
        print('limpando cpf')
        cpf_destinatario= self.cleaned_data.get('cpf_destinatario')
        print(cpf_destinatario)
        if not cpf.validate(self.cleaned_data.get('cpf_destinatario')):
            raise ValidationError('CPF inválido.')
        return cpf_destinatario

    def clean_cep(self):
        print('limpando cep')
        cep = self.cleaned_data.get('cep')
        if cep:
            response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
            if response.status_code != 200 or response.json().get('erro'):
                raise forms.ValidationError('CEP inválido ou não encontrado.')
        return cep

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        try:
            user = kwargs.get('initial').get('user')
        except:
            user = None
        if user and user.is_authenticated:
            self.fields['destinatario'].initial = f"{user.first_name} {user.last_name}"
            self.fields['cpf_destinatario'].initial = user.profile.cpf
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Endereço",
                Div(

                    Field('destinatario', wrapper_class="col-12", placeholder='Destinatário'),
                    Field('cep', wrapper_class="col-6", data_mask='00000-000', placeholder='CEP',oninvalid="this.setCustomValidity('CEP invalido') ; ", oninput="this.setCustomValidity(''); validacep_submit(this.value)" ),
                    Field('cpf_destinatario', css_class='', wrapper_class="col-6", data_mask='000.000.000-00', placeholder='Número do CPF', required=True, oninput="this.setCustomValidity(validaCPF(this) ? '' : 'CPF inválido');"),

                    css_class='form-row'
                ),

                Div(


                    Field('rua', wrapper_class="col-10", placeholder='Rua'),
                    Field('numero', wrapper_class="col-2", placeholder='Número',oninput="this.setCustomValidity(''); ", oninvalid="this.setCustomValidity('Caso nao tenha numero, digite S/N')" ),
                    css_class='form-row'
                ),
                Div(
                    Field('complemento', wrapper_class="col-6", placeholder='Complemento'),
                    Field('cidade', wrapper_class="col-6", placeholder='Cidade'),
                    css_class='form-row'),
                Div(

                    Field('bairro', wrapper_class="col-8", placeholder='Bairro'),
                    Field('estado', wrapper_class="col-4", placeholder='Estado'),
                    css_class='form-row'
                ),


            ),
            Submit('submit', 'SALVAR', css_class='site-btn',)
        )





