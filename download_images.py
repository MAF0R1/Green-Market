import os
import django
import requests
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from market.models import Product

# =========================================
# КАРТИНКИ ДЛЯ КОНКРЕТНЫХ ТОВАРОВ
# =========================================
image_urls = {
    'Добрый кола': 'https://cdn-icons-png.flaticon.com/512/3096/3096594.png',
    'Пепси кола': 'https://cdn-icons-png.flaticon.com/512/3096/3096594.png',
    '7Up': 'https://cdn-icons-png.flaticon.com/512/3096/3096594.png',
    'Mirinda': 'https://cdn-icons-png.flaticon.com/512/3096/3096594.png',
    'Fanta': 'https://cdn-icons-png.flaticon.com/512/3096/3096594.png',
    'Хлеб бородинский': 'https://cdn-icons-png.flaticon.com/512/1046/1046777.png',
    'Батон': 'https://cdn-icons-png.flaticon.com/512/1046/1046777.png',
    'Чипсы Lays': 'https://cdn-icons-png.flaticon.com/512/1046/1046777.png',
    'Кириешки': 'https://cdn-icons-png.flaticon.com/512/1046/1046777.png',
}


def download_fixed_images():
    """Скачивает картинки по готовым ссылкам"""
    print("🔄 Начинаю скачивание...")
    print("=" * 60)

    success = 0
    fail = 0

    for product_name, url in image_urls.items():
        try:
            # Ищем товар
            product = Product.objects.filter(name__icontains=product_name).first()
            if not product:
                print(f"❌ Товар '{product_name}' не найден")
                fail += 1
                continue

            # Скачиваем
            response = requests.get(url, timeout=10)
            img = Image.open(BytesIO(response.content))

            # Сохраняем
            filename = f"{product_name.lower().replace(' ', '_')}.png"
            save_path = os.path.join('media', 'products', filename)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            img.save(save_path, 'PNG')

            # Прикрепляем к товару
            product.image = f'products/{filename}'
            product.save()

            print(f"✅ {product_name} → {filename}")
            success += 1

        except Exception as e:
            print(f"❌ Ошибка для {product_name}: {e}")
            fail += 1

    print("\n" + "=" * 60)
    print(f"✅ Успешно: {success}")
    print(f"❌ Ошибок: {fail}")


if __name__ == '__main__':
    download_fixed_images()