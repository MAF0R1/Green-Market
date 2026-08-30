from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Category, Product, SupportMessage, Order, Review, User, PromoCode, RecommendedProduct, UserPromoCode, Favorite, LoyaltyConfig
from ckeditor.widgets import CKEditorWidget
from django.db import models
import csv

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product_count']
    search_fields = ['name']
    ordering = ['name']
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Товаров'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'category', 'hit_score', 'hit_status', 'product_image_preview']
    list_filter = ['category', 'hit_score']
    search_fields = ['name', 'description']
    list_editable = ['price', 'category', 'hit_score']
    list_per_page = 25
    ordering = ['-hit_score', 'name']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
    def hit_status(self, obj):
        if obj.hit_score >= 20: return '🔥 Хит'
        elif obj.hit_score >= 10: return '⭐ Бестселлер'
        elif obj.hit_score >= 5: return '👍 Популярный'
        return '📦 Обычный'
    hit_status.short_description = 'Статус'
    def product_image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;" />', obj.image.url)
        return '📦'
    product_image_preview.short_description = 'Фото'
    actions = ['make_hit', 'make_bestseller', 'make_popular', 'reset_hit_score', 'increase_price_10', 'decrease_price_10', 'increase_price_20', 'decrease_price_20', 'export_selected_products', 'delete_selected_products']
    def make_hit(self, request, queryset):
        count = queryset.update(hit_score=50)
        self.message_user(request, f'Сделано хитами: {count}')
    make_hit.short_description = 'Сделать ХИТАМИ (50)'
    def make_bestseller(self, request, queryset):
        count = queryset.update(hit_score=20)
        self.message_user(request, f'Сделано бестселлерами: {count}')
    make_bestseller.short_description = 'Сделать БЕСТСЕЛЛЕРАМИ (20)'
    def make_popular(self, request, queryset):
        count = queryset.update(hit_score=10)
        self.message_user(request, f'Сделано популярными: {count}')
    make_popular.short_description = 'Сделать ПОПУЛЯРНЫМИ (10)'
    def reset_hit_score(self, request, queryset):
        count = queryset.update(hit_score=0)
        self.message_user(request, f'Сброшено: {count}')
    reset_hit_score.short_description = 'Сбросить популярность (0)'
    def increase_price_10(self, request, queryset):
        count = 0
        for product in queryset:
            product.price = int(product.price * 1.1)
            product.save()
            count += 1
        self.message_user(request, f'+10 процентов для {count} товаров')
    increase_price_10.short_description = '+10 процентов к цене'
    def decrease_price_10(self, request, queryset):
        count = 0
        for product in queryset:
            product.price = int(product.price * 0.9)
            product.save()
            count += 1
        self.message_user(request, f'-10 процентов для {count} товаров')
    decrease_price_10.short_description = '-10 процентов к цене'
    def increase_price_20(self, request, queryset):
        count = 0
        for product in queryset:
            product.price = int(product.price * 1.2)
            product.save()
            count += 1
        self.message_user(request, f'+20 процентов для {count} товаров')
    increase_price_20.short_description = '+20 процентов к цене'
    def decrease_price_20(self, request, queryset):
        count = 0
        for product in queryset:
            product.price = int(product.price * 0.8)
            product.save()
            count += 1
        self.message_user(request, f'-20 процентов для {count} товаров')
    decrease_price_20.short_description = '-20 процентов к цене'
    def export_selected_products(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Название', 'Цена', 'Категория', 'Хит-счёт', 'Статус'])
        for product in queryset:
            status = 'Хит' if product.hit_score >= 20 else 'Бестселлер' if product.hit_score >= 10 else 'Популярный' if product.hit_score >= 5 else 'Обычный'
            writer.writerow([product.id, product.name, product.price, product.category.name if product.category else '', product.hit_score, status])
        self.message_user(request, f'Экспортировано: {queryset.count()}')
        return response
    export_selected_products.short_description = 'Экспортировать в CSV'
    def delete_selected_products(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Удалено: {count}')
    delete_selected_products.short_description = 'Удалить выбранные'

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_short_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message',)
    ordering = ['-created_at']
    readonly_fields = ('message', 'created_at')
    def get_short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    get_short_message.short_description = 'Сообщение'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'method', 'total', 'item_count', 'created_at')
    list_filter = ('method', 'created_at')
    search_fields = ('name', 'email', 'address')
    ordering = ['-created_at']
    fieldsets = (
        ('Клиент', {'fields': ('name', 'email')}),
        ('Оплата', {'fields': ('method', 'total')}),
        ('Доставка', {'fields': ('address',)}),
    )
    def item_count(self, obj):
        try:
            import json
            items = json.loads(obj.items)
            return len(items)
        except:
            return 0
    item_count.short_description = 'Товаров'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'name', 'surname', 'created_at', 'last_login']
    search_fields = ['phone', 'name', 'surname']
    list_filter = ['created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user_name', 'get_user_phone', 'get_product_name', 'get_category_name', 'rating', 'is_approved', 'short_text', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at', 'product__category']
    search_fields = ['user__name', 'user__phone', 'user__surname', 'product__name', 'text']
    readonly_fields = ['created_at']
    list_editable = ['is_approved']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'disapprove_reviews', 'delete_reviews']
    def get_user_name(self, obj):
        if obj.user: return f"{obj.user.surname or ''} {obj.user.name or ''}".strip() or obj.user.phone
        return obj.name or "—"
    get_user_name.short_description = 'Имя'
    def get_user_phone(self, obj):
        if obj.user: return obj.user.phone
        return obj.email or "—"
    get_user_phone.short_description = 'Телефон/Email'
    def get_product_name(self, obj):
        if obj.product: return obj.product.name
        return "—"
    get_product_name.short_description = 'Товар'
    def get_category_name(self, obj):
        if obj.product and obj.product.category: return obj.product.category.name
        return "—"
    get_category_name.short_description = 'Категория'
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Текст'
    def approve_reviews(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'✅ Одобрено {count} отзывов!')
    approve_reviews.short_description = '✅ Одобрить выбранные'
    def disapprove_reviews(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'❌ Отклонено {count} отзывов!')
    disapprove_reviews.short_description = '❌ Отклонить выбранные'
    def delete_reviews(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'🗑️ Удалено {count} отзывов!')
    delete_reviews.short_description = '🗑️ Удалить выбранные'

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['code']
    list_filter = ['is_active']

@admin.register(RecommendedProduct)
class RecommendedProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'is_active']
    list_editable = ['is_active']
    search_fields = ['product__name']

@admin.register(UserPromoCode)
class UserPromoCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'promo_code', 'expires_at', 'is_used', 'created_at']
    list_editable = ['is_used']
    list_filter = ['is_used', 'expires_at']
    search_fields = ['user__phone', 'promo_code__code']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'created_at']
    search_fields = ['user__phone', 'product__name']

@admin.register(LoyaltyConfig)
class LoyaltyConfigAdmin(admin.ModelAdmin):
    list_display = ['min_order_amount', 'promo_code_template', 'discount', 'validity_days', 'is_active']
    list_editable = ['discount', 'validity_days', 'is_active']