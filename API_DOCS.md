# API Documentation

## Drone Components Configurator API

Документація для роботи з функціями та модулями додатку.

---

## 📦 Основні модулі

### app.py
Головний файл додатку з інтерфейсом Streamlit.

### db_helpers.py
Допоміжні функції для роботи з базою даних.

### test_setup.py
Тестовий скрипт для перевірки налаштувань.

---

## 🔌 Database Functions

### get_all_components()
Отримує всі компоненти з бази даних.

**Returns:**
- `pd.DataFrame`: DataFrame з усіма компонентами

**Example:**
```python
from app import get_all_components

components = get_all_components()
print(f"Total: {len(components)}")
```

---

### get_components_by_type(component_type: str)
Фільтрує компоненти за типом.

**Args:**
- `component_type` (str): "квадрік", "літак", або "перехоплювач"

**Returns:**
- `pd.DataFrame`: Відфільтровані компоненти

**Example:**
```python
drones = get_components_by_type("квадрік")
```

---

### add_component(name, comp_type, category, price_uah, stock_status, url)
Додає новий компонент до бази даних.

**Args:**
- `name` (str): Назва компонента
- `comp_type` (str): Тип апарату
- `category` (str): Категорія
- `price_uah` (float): Ціна в гривнях
- `stock_status` (bool): Наявність
- `url` (str): Посилання

**Returns:**
- `bool`: True якщо успішно

**Example:**
```python
success = add_component(
    name="T-Motor F60",
    comp_type="квадрік",
    category="мотори",
    price_uah=1250.00,
    stock_status=True,
    url="https://store.com/motor"
)
```

---

### update_component(component_id: int, updates: Dict)
Оновлює існуючий компонент.

**Args:**
- `component_id` (int): ID компонента
- `updates` (Dict): Словник з оновленнями

**Returns:**
- `bool`: True якщо успішно

**Example:**
```python
update_component(
    component_id=5,
    updates={"price_uah": 1300.00, "stock_status": True}
)
```

---

### delete_component(component_id: int)
Видаляє компонент.

**Args:**
- `component_id` (int): ID компонента

**Returns:**
- `bool`: True якщо успішно

---

## 🛒 Cart Functions

### add_to_cart(component_id: int, quantity: int = 1)
Додає компонент до кошика.

**Example:**
```python
add_to_cart(component_id=5, quantity=2)
```

---

### get_cart_items()
Отримує всі товари в кошику.

**Returns:**
- `pd.DataFrame`: DataFrame з товарами в кошику

---

### calculate_total()
Розраховує загальну вартість кошика.

**Returns:**
- `float`: Загальна сума

---

## 🔒 Authentication

### check_admin_password(password: str)
Перевіряє пароль адміністратора.

**Args:**
- `password` (str): Пароль для перевірки

**Returns:**
- `bool`: True якщо пароль правильний

---

### hash_password(password: str)
Генерує SHA256 хеш пароля.

**Args:**
- `password` (str): Пароль для хешування

**Returns:**
- `str`: SHA256 хеш

**Example:**
```python
import hashlib

password = "my_secure_password"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

---

## 📊 DB Helpers Functions

### export_components_to_csv(supabase_client, filename=None)
Експортує компоненти в CSV.

**Example:**
```python
from db_helpers import export_components_to_csv
from app import supabase

filename = export_components_to_csv(supabase)
print(f"Exported to: {filename}")
```

---

### import_components_from_csv(supabase_client, filename)
Імпортує компоненти з CSV.

**Returns:**
```python
{
    'success': True,
    'imported': 25,
    'total': 25,
    'errors': []
}
```

---

### get_database_statistics(supabase_client)
Отримує статистику бази даних.

**Returns:**
```python
{
    'total_components': 30,
    'in_stock': 25,
    'out_of_stock': 5,
    'by_type': {'квадрік': 20, 'літак': 8, 'перехоплювач': 2},
    'by_category': {...},
    'price_range': {'min': 100.0, 'max': 8500.0, 'median': 1500.0},
    'avg_price': 1850.50
}
```

---

### search_components(supabase_client, query, search_in=['name', 'category'])
Пошук компонентів.

**Example:**
```python
results = search_components(supabase, "motor")
print(f"Found: {len(results)}")
```

---

## 🔮 Future Integration

### sync_prices()
**Статус:** Offline (майбутня функція)

Архітектура для інтеграції парсинг-агента:

```python
def sync_prices():
    """
    Майбутня реалізація:
    1. Викликати API парсера
    2. Для кожного component.url:
       - Отримати актуальну ціну
       - Оновити в БД
    3. Логувати зміни
    4. Повернути звіт
    """
    # Current implementation
    return {
        'status': 'offline',
        'timestamp': datetime.now(),
        'updated_count': 0
    }
```

**Інтеграція:**
1. Розробити парсинг-сервіс (BeautifulSoup/Selenium)
2. Створити API endpoint
3. Замінити заглушку викликом API
4. Додати обробку помилок та логування

---

## 📝 Data Models

### Component Model

```python
{
    'id': int,                    # Primary key
    'name': str,                  # Назва компонента
    'type': str,                  # квадрік | літак | перехоплювач
    'category': str,              # мотори, ESC, рама, тощо
    'price_uah': float,           # Ціна в гривнях
    'stock_status': bool,         # В наявності
    'url': str,                   # Посилання на магазин
    'created_at': timestamp,      # Дата створення
    'updated_at': timestamp       # Дата оновлення
}
```

### Cart Item Model

```python
{
    'component_id': int,          # ID компонента
    'quantity': int,              # Кількість
    'name': str,                  # Назва
    'price_uah': float,           # Ціна за одиницю
    'total_price': float,         # Загальна вартість
    'url': str                    # Посилання
}
```

---

## 🛡️ Security

### Row Level Security (RLS)

База даних використовує RLS політики:

- **Public Read**: Всі можуть читати
- **Authenticated Insert/Update/Delete**: Тільки авторизовані

### Password Storage

Паролі зберігаються як SHA256 хеші:

```python
import hashlib

password = "your_password"
hash_value = hashlib.sha256(password.encode()).hexdigest()
```

**⚠️ Важливо:** 
- Ніколи не зберігайте паролі в відкритому вигляді
- Використовуйте сильні паролі (12+ символів)
- Регулярно оновлюйте credentials

---

## 🔄 State Management

### Session State Variables

```python
st.session_state.is_admin         # bool: Статус адміністратора
st.session_state.cart             # dict: Кошик {id: quantity}
st.session_state.last_sync        # datetime: Остання синхронізація
```

---

## 📡 API Endpoints (Supabase)

### SELECT
```python
supabase.table('components').select('*').execute()
```

### INSERT
```python
supabase.table('components').insert(data).execute()
```

### UPDATE
```python
supabase.table('components').update(data).eq('id', component_id).execute()
```

### DELETE
```python
supabase.table('components').delete().eq('id', component_id).execute()
```

### FILTER
```python
supabase.table('components').select('*').eq('type', 'квадрік').execute()
```

---

## 📊 Response Formats

### Success Response
```python
{
    'data': [...],           # Results
    'count': int,            # Count if requested
    'error': None
}
```

### Error Response
```python
{
    'data': None,
    'count': None,
    'error': {
        'message': str,      # Error message
        'details': str,      # Additional details
        'hint': str,         # Suggestion
        'code': str          # Error code
    }
}
```

---

## 🧪 Testing

### Run Tests
```bash
python test_setup.py
```

### Manual Testing
```python
# Test connection
from supabase import create_client

url = "your_url"
key = "your_key"
supabase = create_client(url, key)

# Test query
result = supabase.table('components').select('*').limit(5).execute()
print(result.data)
```

---

## 📞 Support

**Issues:** GitHub Issues  
**Documentation:** README.md, SETUP_GUIDE.md  
**Version:** 1.0.0

---

**© 2026 Drone Price System**
