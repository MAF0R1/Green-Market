from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from market.views import (
    index, catalog, aboyt, contacts, login, cart, wholesale, wholesale_checkout,
    contact, support_api, login_api, create_order_api, checkout,
    increment_hit_api, product_detail, logout, profile, check_promo_api
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('catalog/', catalog, name='catalog'),
    path('catalog/<int:product_id>/', product_detail, name='product_detail'),
    path('aboyt/', aboyt, name='aboyt'),
    path('contacts/', contacts, name='contacts'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('cart/', cart, name='cart'),
    path('wholesale/', wholesale, name='wholesale'),
    path('wholesale-checkout/', wholesale_checkout, name='wholesale_checkout'),
    path('contact/', contact, name='contact'),
    path('api/support/', support_api, name='support_api'),
    path('api/login/', login_api, name='login_api'),
    path('api/create_order/', create_order_api, name='create_order_api'),
    path('api/check_promo/', check_promo_api, name='check_promo_api'),
    path('checkout/', checkout, name='checkout'),
    path('api/increment_hit/<int:product_id>/', increment_hit_api, name='increment_hit'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)