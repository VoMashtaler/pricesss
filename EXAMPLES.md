# Приклади використання

Цей файл містить практичні приклади використання Drone Components Configurator.

---

## 🎯 Базові сценарії

### 1. Запуск додатку для гостя

```bash
# Запустіть додаток
streamlit run app.py

# Відкрийте браузер: http://localhost:8501
# Оберіть "Готовий пресет"
# Виберіть "7-дюймовий камікадзе"
# Натисніть "Завантажити пресет"
# Переглядайте компоненти в кошику
```

### 2. Вхід як адміністратор

```python
# В бічній панелі:
# 1. Введіть пароль: admin123
# 2. Натисніть "Увійти як Admin"
# 3. Тепер доступна панель адміністратора
```

### 3. Додавання компонента

**Через UI:**
1. Увійдіть як адмін
2. Перейдіть на таб "➕ Додати компонент"
3. Заповніть форму:
   - Назва: "T-Motor F90 1300KV"
   - Тип: "квадрік"
   - Категорія: "мотори"
   - Ціна: 1450.00
   - В наявності: ✓
   - URL: https://store.com/motor
4. Натисніть "Додати компонент"

**Програмно:**
```python
from app import supabase, add_component

success = add_component(
    name="T-Motor F90 1300KV",
    comp_type="квадрік",
    category="мотори",
    price_uah=1450.00,
    stock_status=True,
    url="https://store.com/motor"
)

if success:
    print("✅ Компонент додано!")
```

### 4. Масове редагування цін

**Через UI:**
1. Увійдіть як адмін
2. Таб "✏️ Редагувати ціни"
3. Редагуйте таблицю (подвійний клік на комірку)
4. Змініть ціни декількох компонентів
5. Натисніть "Зберегти зміни"

**Програмно:**
```python
import pandas as pd
from app import supabase, get_all_components

# Отримати компоненти
df = get_all_components()

# Підвищити всі ціни на 10%
df['price_uah'] = df['price_uah'] * 1.10

# Оновити в базі
for _, row in df.iterrows():
    supabase.table('components').update(
        {'price_uah': row['price_uah']}
    ).eq('id', row['id']).execute()

print("✅ Ціни оновлено!")
```

---

## 🔌 Робота з базою даних

### Підключення до Supabase

```python
from supabase import create_client

url = "https://your-project.supabase.co"
key = "your-anon-key"

supabase = create_client(url, key)
```

### Отримання всіх компонентів

```python
# Всі компоненти
response = supabase.table('components').select('*').execute()
components = response.data

print(f"Всього компонентів: {len(components)}")
```

### Фільтрація за типом

```python
# Тільки квадрокоптери
response = supabase.table('components').select('*').eq('type', 'квадрік').execute()
drones = response.data

print(f"Квадрокоптерів: {len(drones)}")
```

### Пошук за категорією

```python
# Всі мотори
response = supabase.table('components').select('*').eq('category', 'мотори').execute()
motors = response.data

for motor in motors:
    print(f"{motor['name']}: {motor['price_uah']} UAH")
```

### Компоненти в наявності

```python
# В наявності
response = supabase.table('components').select('*').eq('stock_status', True).execute()
in_stock = response.data

print(f"В наявності: {len(in_stock)}")
```

### Діапазон цін

```python
# Від 1000 до 2000 грн
response = supabase.table('components').select('*')\
    .gte('price_uah', 1000)\
    .lte('price_uah', 2000)\
    .execute()

affordable = response.data
print(f"Компонентів від 1000-2000 грн: {len(affordable)}")
```

---

## 📊 Аналітика та статистика

### Статистика по типах

```python
import pandas as pd
from app import supabase

response = supabase.table('components').select('*').execute()
df = pd.DataFrame(response.data)

# Групування по типах
type_stats = df.groupby('type').agg({
    'id': 'count',
    'price_uah': ['mean', 'min', 'max']
}).round(2)

print(type_stats)
```

### Аналіз цін по категоріям

```python
category_stats = df.groupby('category').agg({
    'price_uah': ['count', 'mean', 'sum'],
    'stock_status': 'sum'  # кількість в наявності
}).round(2)

print(category_stats)
```

### Найдорожчі компоненти

```python
top_10 = df.nlargest(10, 'price_uah')[['name', 'category', 'price_uah']]
print(top_10)
```

### Найдешевші компоненти

```python
bottom_10 = df.nsmallest(10, 'price_uah')[['name', 'category', 'price_uah']]
print(bottom_10)
```

---

## 🛒 Робота з кошиком

### Додавання до кошика

```python
import streamlit as st
from app import add_to_cart

# Додати 2 одиниці компонента з ID=5
add_to_cart(component_id=5, quantity=2)

# Додати 1 одиницю компонента з ID=8
add_to_cart(component_id=8, quantity=1)
```

### Перегляд кошика

```python
from app import get_cart_items, calculate_total

# Отримати товари
cart_df = get_cart_items()

# Вивести таблицю
print(cart_df[['name', 'quantity', 'price_uah', 'total_price']])

# Загальна сума
total = calculate_total()
print(f"\nЗагалом: {total:.2f} UAH")
```

### Очищення кошика

```python
from app import clear_cart

clear_cart()
print("✅ Кошик очищено")
```

---

## 📥 Експорт та імпорт

### Експорт в CSV

```python
from db_helpers import export_components_to_csv
from app import supabase

filename = export_components_to_csv(supabase, "my_components.csv")
print(f"Експортовано в: {filename}")
```

### Експорт кошика в Excel

```python
from app import get_cart_items
import pandas as pd
from io import BytesIO

# Отримати кошик
cart_df = get_cart_items()

# Створити Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    cart_df.to_excel(writer, index=False, sheet_name='Замовлення')

# Зберегти
with open('order.xlsx', 'wb') as f:
    f.write(output.getvalue())

print("✅ Експорт в order.xlsx")
```

### Імпорт з CSV

```python
from db_helpers import import_components_from_csv
from app import supabase

result = import_components_from_csv(supabase, "components.csv")

if result['success']:
    print(f"✅ Імпортовано: {result['imported']}/{result['total']}")
else:
    print(f"❌ Помилка: {result['error']}")
```

---

## 🔐 Управління паролями

### Генерація хешу паролю

```python
import hashlib

def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Приклад
new_password = "my_super_secure_password_2026"
hash_value = generate_password_hash(new_password)

print(f"Пароль: {new_password}")
print(f"Hash: {hash_value}")
print("\nДодайте цей hash в .streamlit/secrets.toml:")
print(f'password_hash = "{hash_value}"')
```

### Перевірка паролю

```python
from app import check_admin_password

password = "admin123"
is_valid = check_admin_password(password)

if is_valid:
    print("✅ Пароль правильний")
else:
    print("❌ Пароль невірний")
```

---

## 🔧 Утиліти та допоміжні функції

### Пошук компонентів

```python
from db_helpers import search_components
from app import supabase

# Пошук по назві
results = search_components(supabase, "motor", search_in=['name'])
print(f"Знайдено: {len(results)}")

# Пошук по назві та категорії
results = search_components(supabase, "T-Motor", search_in=['name', 'category'])
```

### Дублювання компонента

```python
from db_helpers import duplicate_component
from app import supabase

# Дублювати компонент з ID=5
success = duplicate_component(
    supabase,
    component_id=5,
    new_name="T-Motor F60 Pro (копія)"
)

if success:
    print("✅ Компонент дубльовано")
```

### Масова зміна статусу

```python
from db_helpers import bulk_update_stock_status
from app import supabase

# Позначити компоненти 1, 2, 3 як відсутні
result = bulk_update_stock_status(
    supabase,
    component_ids=[1, 2, 3],
    status=False
)

print(f"Оновлено: {result['updated']}/{result['total']}")
```

---

## 🎨 Кастомізація пресетів

### Додавання власного пресету

```python
# У файлі app.py знайдіть DRONE_PRESETS і додайте:

DRONE_PRESETS = {
    # ... існуючі пресети
    
    "Мій кастомний дрон": {
        "type": "квадрік",
        "categories": ["мотори", "ESC", "рама", "контролер польоту", "пропелери"]
    }
}
```

### Використання пресету

```python
from app import get_preset_components

# Завантажити пресет
preset_df = get_preset_components("7-дюймовий камікадзе")

print("Компоненти в пресеті:")
print(preset_df[['name', 'category', 'price_uah']])

total = preset_df['price_uah'].sum()
print(f"\nВартість пресету: {total:.2f} UAH")
```

---

## 🧪 Тестування

### Запуск тестів

```bash
python test_setup.py
```

### Ручне тестування підключення

```python
from supabase import create_client

url = "https://your-project.supabase.co"
key = "your-anon-key"

try:
    supabase = create_client(url, key)
    response = supabase.table('components').select('*').limit(1).execute()
    
    if response.data:
        print("✅ Підключення успішне!")
    else:
        print("⚠️ Підключення встановлено, але таблиця порожня")
        
except Exception as e:
    print(f"❌ Помилка: {e}")
```

---

## 📱 Приклади використання API

### REST API через Supabase

```python
import requests

url = "https://your-project.supabase.co/rest/v1/components"
headers = {
    "apikey": "your-anon-key",
    "Authorization": f"Bearer your-anon-key"
}

# GET всі компоненти
response = requests.get(url, headers=headers)
components = response.json()

print(f"Компонентів: {len(components)}")

# POST новий компонент
new_component = {
    "name": "Test Component",
    "type": "квадрік",
    "category": "тест",
    "price_uah": 999.99,
    "stock_status": True
}

response = requests.post(url, json=new_component, headers=headers)
if response.status_code == 201:
    print("✅ Компонент додано через API")
```

---

## 🔮 Розширення функціоналу

### Додавання власної функції

```python
# У файлі app.py або створіть новий модуль

def calculate_discount(price: float, discount_percent: float) -> float:
    """Розрахунок ціни зі знижкою"""
    discount = price * (discount_percent / 100)
    return price - discount

# Використання
original_price = 1500.00
discounted = calculate_discount(original_price, 15)
print(f"Ціна зі знижкою 15%: {discounted:.2f} UAH")
```

### Інтеграція з іншими сервісами

```python
# Приклад: відправка email про замовлення
import smtplib
from email.mime.text import MIMEText

def send_order_email(cart_items, total, recipient):
    """Відправка email з деталями замовлення"""
    
    # Формування повідомлення
    message_body = "Ваше замовлення:\n\n"
    for item in cart_items:
        message_body += f"{item['name']}: {item['quantity']} x {item['price_uah']} UAH\n"
    message_body += f"\nЗагалом: {total} UAH"
    
    # Відправка (налаштуйте SMTP)
    # ... код відправки email
    
    print("✅ Email відправлено")
```

---

## 💡 Корисні поради

### 1. Оптимізація запитів

```python
# Замість багатьох запитів:
for component_id in [1, 2, 3, 4, 5]:
    component = supabase.table('components').select('*').eq('id', component_id).execute()

# Використовуйте один запит:
components = supabase.table('components').select('*').in_('id', [1, 2, 3, 4, 5]).execute()
```

### 2. Кешування даних

```python
import streamlit as st

@st.cache_data(ttl=300)  # Кеш на 5 хвилин
def get_components_cached():
    return supabase.table('components').select('*').execute().data
```

### 3. Обробка помилок

```python
try:
    component = supabase.table('components').select('*').eq('id', 999).execute()
    if not component.data:
        print("⚠️ Компонент не знайдено")
except Exception as e:
    print(f"❌ Помилка: {str(e)}")
```

---

**© 2026 Drone Price System**  
Версія: 1.0.0
