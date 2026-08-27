from django.db import models
from django.utils.safestring import mark_safe
from ckeditor.fields import RichTextField

class Category(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    price = models.IntegerField(db_index=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True)
    hit_score = models.IntegerField(default=0, db_index=True)
    description = RichTextField(blank=True, null=True)
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    def __str__(self):
        return self.name

class User(models.Model):
    phone = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    surname = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Последний вход")
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    def __str__(self):
        return f"{self.surname} {self.name}".strip() or self.phone

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="reviews", null=True, blank=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар", related_name="reviews", null=True, blank=True, db_index=True)
    text = models.TextField(verbose_name="Отзыв")
    rating = models.IntegerField(
        choices=[
            (1, '⭐ 1 — Ужасно'),
            (2, '⭐ 2 — Плохо'),
            (3, '⭐ 3 — Нормально'),
            (4, '⭐ 4 — Хорошо'),
            (5, '⭐ 5 — Отлично')
        ],
        default=5,
        verbose_name="Оценка"
    )
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
    def __str__(self):
        user_str = self.user if self.user else "Аноним"
        product_str = self.product.name if self.product else "Без товара"
        return f"{user_str} → {product_str[:20]}"

class SupportMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    class Meta:
        verbose_name = "Сообщение в техподдержку"
        verbose_name_plural = "Сообщения в техподдержку"
    def __str__(self):
        return self.message[:30] + "..."

class LoginAttempt(models.Model):
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время входа")
    class Meta:
        verbose_name = "Попытка входа"
        verbose_name_plural = "Попытки входа"
    def __str__(self):
        return self.phone

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="orders", null=True, blank=True, db_index=True)
    name = models.CharField(max_length=100, verbose_name="Имя клиента")
    email = models.EmailField(verbose_name="Email")
    method = models.CharField(max_length=50, verbose_name="Способ оплаты")
    total = models.CharField(max_length=20, verbose_name="Сумма")
    items = models.TextField(verbose_name="Товары")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    def __str__(self):
        return f"{self.name} - {self.total}₽"

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    discount = models.IntegerField(verbose_name="Скидка (%)", default=10)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
    def __str__(self):
        return f"{self.code} (-{self.discount}%)"

class RecommendedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    class Meta:
        verbose_name = "Рекомендуемый товар"
        verbose_name_plural = "Рекомендуемые товары"
    def __str__(self):
        return self.product.name