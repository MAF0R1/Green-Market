from django import forms

class OrderForm(forms.Form):
    name = forms.CharField(
        label="Имя владельца",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Иван Иванов'})
    )
    email = forms.EmailField(
        label="Email для чека",
        widget=forms.EmailInput(attrs={'placeholder': 'mail@example.ru'})
    )
    method = forms.ChoiceField(
        label="Способ оплаты",
        choices=[
            ('СБП', 'СБП'),
            ('СберКарта', 'СберКарта'),
            ('T-Карта', 'T-Карта'),
            ('Visa/Mastercard', 'Visa / Mastercard')
        ],
        widget=forms.Select(attrs={'class': 'payment-select'})
    )
    card_number = forms.CharField(
        label="Номер карты",
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000'})
    )
    expiry = forms.CharField(
        label="Срок (ММ/ГГ)",
        max_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'ММ/ГГ'})
    )
    cvv = forms.CharField(
        label="CVV",
        max_length=3,
        widget=forms.TextInput(attrs={'placeholder': '***'})
    )
    address = forms.CharField(
        label="Адрес доставки",
        widget=forms.TextInput(attrs={'placeholder': 'г. Москва, ул. Пушкина, д. 1'})
    )