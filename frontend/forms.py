from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from accounts.serializers import send_verification_email
from blog.models import Post, Category

User = get_user_model()

class FrontendLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your username",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )


class FrontendRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Create a strong password",
                "autocomplete": "new-password",
            }
        ),
    )

    password_confirm = forms.CharField(
        label="Confirm password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Choose a username",
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter your email",
                    "autocomplete": "email",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "A user with this username already exists."
            )

        return username

    def clean_password(self):
        password = self.cleaned_data["password"]

        validate_password(password)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error(
                "password_confirm",
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.is_active = False
        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()
            send_verification_email(user)

        return user

class FrontendPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'category',
            'image',
            'is_published',
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter post title",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": "Write your post content here...",
                    "rows": 10,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-file",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["category"].queryset = Category.objects.all().order_by("name")
            self.fields["category"].empty_label = "Select category"

            self.fields["image"].required = False
            self.fields["category"].required = True

class ResendVerificationForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )
    def save(self):
        email = self.cleaned_data["email"]

        user = User.objects.filter(email=email).first()

        if not user:
            return

        if user.is_active:
            return

        send_verification_email(user)

class PasswordResetRequestFrontendForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )

class PasswordResetConfirmFrontendForm(forms.Form):
    new_password = forms.CharField(
        label="New password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Create a strong password",
                "autocomplete": "new-password",
            }
        ),
    )

    new_password_confirm = forms.CharField(
        label="Confirm password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")

        validate_password(password)

        return password
    
    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error(
                "new_password_confirm",
                "Passwords do not match."
            )
        return cleaned_data