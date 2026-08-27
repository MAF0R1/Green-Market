from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import F, Avg
import json
import time
from .models import Product, Category, SupportMessage, LoginAttempt, Order, Review, User, PromoCode, RecommendedProduct
from .forms import OrderForm

def index(request):
    return render(request, 'index.html')

def catalog(request):
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'default')
    page_number = request.GET.get('page', 1)
    cache_key = f'catalog_v2_{category_id}_{sort_by}_{page_number}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'catalog.html', cached_data)
    products = Product.objects.select_related('category').all()
    if category_id:
        products = products.filter(category_id=category_id)
    try:
        if sort_by == 'price': products = products.order_by('price')
        elif sort_by == '-price': products = products.order_by('-price')
        elif sort_by == 'name': products = products.order_by('name')
        elif sort_by == 'popular': products = products.order_by('-hit_score')
        elif sort_by == 'default': products = products.order_by('-hit_score')
    except:
        products = products.order_by('id')
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(page_number)
    categories = cache.get('all_categories_v2')
    if not categories:
        categories = Category.objects.all()
        cache.set('all_categories_v2', categories, 3600)
    for product in page_obj.object_list:
        if hasattr(product, 'hit_score'):
            if product.hit_score >= 20: product.rating = 5
            elif product.hit_score >= 10: product.rating = 4
            elif product.hit_score >= 5: product.rating = 3
            elif product.hit_score >= 2: product.rating = 2
            else: product.rating = 1
        else:
            product.rating = 0
    data = {
        'page_obj': page_obj,
        'products': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort_by,
        'breadcrumbs': [{'name': 'Главная', 'url': '/'}, {'name': 'Каталог', 'url': '/catalog/'}],
    }
    cache.set(cache_key, data, 300)
    return render(request, 'catalog.html', data)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if hasattr(product, 'hit_score'):
        if product.hit_score >= 20: product.rating = 5
        elif product.hit_score >= 10: product.rating = 4
        elif product.hit_score >= 5: product.rating = 3
        elif product.hit_score >= 2: product.rating = 2
        else: product.rating = 1
    else:
        product.rating = 0
    avg_rating = Review.objects.filter(product=product, is_approved=True).aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('user').order_by('-created_at')
    user = None
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
        except User.DoesNotExist:
            del request.session['user_id']
    if request.method == 'POST' and 'review_submit' in request.POST:
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        phone = request.POST.get('phone', '').strip()
        text = request.POST.get('text', '').strip()
        rating = request.POST.get('rating', 5)
        last_submit = request.session.get('last_review_submit', 0)
        if time.time() - last_submit < 30:
            return render(request, 'product_detail.html', {'product': product, 'reviews': reviews, 'avg_rating': avg_rating, 'user': user, 'error': '⏳ Пожалуйста, подождите 30 секунд перед отправкой нового отзыва.'})
        if not text:
            return render(request, 'product_detail.html', {'product': product, 'reviews': reviews, 'avg_rating': avg_rating, 'user': user, 'error': '❌ Пожалуйста, напишите текст отзыва.'})
        if not user:
            if not phone:
                return render(request, 'product_detail.html', {'product': product, 'reviews': reviews, 'avg_rating': avg_rating, 'user': user, 'error': '❌ Пожалуйста, введите номер телефона.'})
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone.startswith('+'):
                phone = '+' + phone
            user, created = User.objects.get_or_create(phone=phone, defaults={'name': name or phone, 'surname': surname or ''})
            if created:
                if name: user.name = name
                if surname: user.surname = surname
                user.save()
            request.session['user_id'] = user.id
            request.session['user_name'] = f"{user.surname} {user.name}".strip() or user.phone
        Review.objects.create(user=user, product=product, text=text, rating=int(rating))
        request.session['last_review_submit'] = time.time()
        reviews = Review.objects.filter(product=product, is_approved=True).select_related('user').order_by('-created_at')
        avg_rating = Review.objects.filter(product=product, is_approved=True).aggregate(Avg('rating'))['rating__avg']
        avg_rating = round(avg_rating, 1) if avg_rating else 0
        return render(request, 'product_detail.html', {'product': product, 'reviews': reviews, 'avg_rating': avg_rating, 'user': user, 'success': '✅ Спасибо за отзыв! Он будет опубликован после модерации.'})
    return render(request, 'product_detail.html', {'product': product, 'reviews': reviews, 'avg_rating': avg_rating, 'user': user})

def aboyt(request):
    return render(request, 'aboyt.html')

def contacts(request):
    return render(request, 'contacts.html')

def login(request):
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
            return redirect('/')
        except User.DoesNotExist:
            del request.session['user_id']
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        phone = request.POST.get('phone', '').strip()
        if not phone:
            return render(request, 'login.html', {'error': '❌ Пожалуйста, введите номер телефона.'})
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            phone = '+' + phone
        user, created = User.objects.get_or_create(phone=phone, defaults={'name': name or phone, 'surname': surname or ''})
        if created:
            if name: user.name = name
            if surname: user.surname = surname
            user.save()
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.surname} {user.name}".strip() or user.phone
        LoginAttempt.objects.create(phone=phone)
        return redirect('/')
    return render(request, 'login.html')

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['user_name']
    return redirect('/')

def profile(request):
    if 'user_id' not in request.session:
        return redirect('/login/')
    user = get_object_or_404(User, id=request.session['user_id'])
    reviews = Review.objects.filter(user=user).select_related('product').order_by('-created_at')
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'profile.html', {'user': user, 'reviews': reviews, 'orders': orders})

def cart(request):
    recommendations = RecommendedProduct.objects.filter(is_active=True).select_related('product')[:6]
    return render(request, 'cart.html', {'recommendations': recommendations})

def wholesale(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'wholesale.html', {'products': products, 'categories': categories})

def wholesale_checkout(request):
    return render(request, 'wholesale_checkout.html')

def contact(request):
    return render(request, 'contact.html')

@csrf_exempt
def support_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg = data.get('message', '')
            if msg:
                SupportMessage.objects.create(name=data.get('name', ''), email=data.get('email', ''), message=msg)
                return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone', '')
            if phone:
                LoginAttempt.objects.create(phone=phone)
                return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def create_order_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = None
            if 'user_id' in request.session:
                user = User.objects.get(id=request.session['user_id'])
            # Проверка промокода
            promo_code = data.get('promo_code', '')
            discount = 0
            if promo_code:
                promo = PromoCode.objects.filter(code=promo_code, is_active=True).first()
                if promo:
                    discount = promo.discount
            total = int(data.get('total', 0))
            final_total = int(total * (1 - discount / 100))
            Order.objects.create(
                user=user,
                name=data.get('name'),
                email=data.get('email'),
                method=data.get('method'),
                total=str(final_total),
                address=data.get('address', ''),
                items=json.dumps(data.get('items'), ensure_ascii=False)
            )
            return JsonResponse({'status': 'ok', 'final_total': final_total})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'}, status=400)

def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            method = form.cleaned_data['method']
            address = form.cleaned_data['address']
            return render(request, 'order_success.html')
    else:
        form = OrderForm()
    return render(request, 'checkout.html', {'form': form})

@csrf_exempt
def increment_hit_api(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            product.hit_score = F('hit_score') + 1
            product.save(update_fields=['hit_score'])
            product.refresh_from_db()
            return JsonResponse({'status': 'ok', 'new_score': product.hit_score})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)
@csrf_exempt
def check_promo_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            promo = PromoCode.objects.filter(code=code, is_active=True).first()
            if promo:
                return JsonResponse({'valid': True, 'discount': promo.discount})
            return JsonResponse({'valid': False})
        except:
            pass
    return JsonResponse({'valid': False})