from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users
from django.contrib.auth import authenticate


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })

    class Meta(UserCreationForm.Meta):
        model = Users
        fields = ('email', 'nickname', 'password1', 'password2', 'phone_number', 'name')
        labels = {
            'email': '이메일',
            'nickname': '닉네임',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
            'phone_number': '전화번호',
            'name': '이름'
        }
        widgets = {
            'email': forms.EmailInput(),
            'nickname': forms.TextInput(),
            'phone_number': forms.TextInput(),
            'name': forms.TextInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 사용 중인 이메일입니다.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError('전화번호는 숫자만 입력해주세요.')
        return phone_number


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='이메일',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        label='비밀번호',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user.is_active:
            raise forms.ValidationError("have no data")
        return cleaned_data
