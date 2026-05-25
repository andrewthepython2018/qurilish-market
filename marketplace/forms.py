from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("customer_name", "phone", "city", "quantity", "comment")
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше имя"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+998 90 123 45 67"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ташкент"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Нужный объем, адрес или детали заказа"}),
        }
