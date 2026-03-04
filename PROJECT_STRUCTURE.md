# Структура проєкту

```
pricesss/
│
├── 📄 app.py                          # Головний файл додатку (Streamlit)
│   ├── UI компоненти
│   ├── Бізнес-логіка
│   ├── Database операції
│   └── Аутентифікація
│
├── 🗄️ supabase_schema.sql            # SQL схема та тестові дані
│   ├── CREATE TABLE components
│   ├── Indices
│   ├── RLS Policies
│   ├── Triggers
│   └── Sample data (30+ компонентів)
│
├── 🔧 db_helpers.py                   # Утиліти для роботи з БД
│   ├── export_components_to_csv()
│   ├── import_components_from_csv()
│   ├── get_database_statistics()
│   ├── search_components()
│   ├── duplicate_component()
│   └── bulk_update_stock_status()
│
├── 🧪 test_setup.py                   # Тестування налаштувань
│   ├── test_connection()
│   ├── test_crud_operations()
│   └── test_admin_auth()
│
├── 🚀 quickstart.py                   # Швидкий старт
│   ├── check_python_version()
│   ├── create_venv()
│   ├── install_dependencies()
│   └── check_secrets_file()
│
├── 📦 requirements.txt                # Python залежності
│   ├── streamlit >= 1.32.0
│   ├── supabase >= 2.3.0
│   ├── pandas >= 2.2.0
│   └── openpyxl >= 3.1.2
│
├── 📚 Документація
│   ├── README.md                      # Основна документація
│   ├── SETUP_GUIDE.md                 # Інструкція по налаштуванню
│   ├── API_DOCS.md                    # API документація
│   ├── EXAMPLES.md                    # Приклади використання
│   └── CHANGELOG.md                   # Історія змін
│
├── 🔐 Конфігурація
│   ├── .gitignore                     # Git ignore правила
│   ├── LICENSE                        # MIT ліцензія
│   └── .streamlit/
│       ├── config.toml                # Streamlit конфігурація
│       └── secrets.toml.example       # Шаблон secrets
│
└── 📁 Структура проєкту
    └── PROJECT_STRUCTURE.md           # Цей файл
```

---

## 📂 Детальний опис файлів

### Основні файли

#### `app.py` (31 KB, ~900 рядків)
Головний файл веб-додатку з повним функціоналом:

**Секції:**
- **Configuration** - Налаштування Streamlit, custom CSS
- **Database Connection** - Ініціалізація Supabase клієнта
- **Session State** - Управління станом сесії
- **Authentication** - Авторизація адміністратора
- **Database Operations** - CRUD операції
- **Presets Management** - Готові конфігурації
- **Price Sync** - Заглушка для майбутнього парсера
- **Cart Management** - Логіка кошика
- **UI Components** - Рендеринг інтерфейсу

**Функції (20+):**
- `init_supabase()` - Підключення до Supabase
- `get_all_components()` - Отримання всіх компонентів
- `add_component()` - Додавання компонента
- `update_component()` - Оновлення компонента
- `delete_component()` - Видалення компонента
- `add_to_cart()` - Додавання до кошика
- `calculate_total()` - Розрахунок суми
- `render_admin_panel()` - Административна панель
- `render_guest_panel()` - Панель користувача

---

#### `supabase_schema.sql` (9.6 KB)
SQL схема для бази даних Supabase:

**Структура:**
```sql
CREATE TABLE components (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('квадрік', 'літак', 'перехоплювач')),
    category VARCHAR(100) NOT NULL,
    price_uah DECIMAL(10, 2) CHECK (price_uah >= 0),
    stock_status BOOLEAN DEFAULT true,
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Індекси:**
- `idx_components_type` - По типу
- `idx_components_category` - По категорії
- `idx_components_stock_status` - По наявності
- `idx_components_type_category` - Композитний

**Тригери:**
- `update_components_updated_at` - Автоматичне оновлення timestamp

**Тестові дані:**
- 4 типи моторів для квадрокоптерів
- 4 рами
- 4 ESC контролери
- 4 контролери польоту
- 4 набори пропелерів
- 8 компонентів для літаків
- 6 компонентів для перехоплювачів

---

#### `db_helpers.py` (9.3 KB)
Утиліти для роботи з базою даних:

**Експорт/Імпорт:**
- `export_components_to_csv()` - Експорт в CSV
- `import_components_from_csv()` - Імпорт з CSV

**Аналітика:**
- `get_database_statistics()` - Статистика БД
- `search_components()` - Текстовий пошук

**Управління:**
- `duplicate_component()` - Дублювання компонента
- `bulk_update_stock_status()` - Масове оновлення статусу
- `get_price_history()` - Історія цін (TODO)

---

#### `test_setup.py` (7.8 KB)
Автоматизоване тестування налаштувань:

**Тести:**
1. **test_connection()** - Підключення до Supabase
2. **test_crud_operations()** - CREATE, READ, UPDATE, DELETE
3. **test_admin_auth()** - Авторизація адміністратора

**Вихід:**
```
🧪 Тестування підключення до Supabase
✅ Клієнт Supabase створено
✅ З'єднання з базою даних успішне
📊 Статистика: Компонентів в базі: 30
```

---

#### `quickstart.py` (7.4 KB)
Скрипт швидкого налаштування проєкту:

**Функції:**
- Перевірка версії Python (≥ 3.10)
- Створення віртуального середовища
- Встановлення залежностей
- Створення конфігураційних файлів
- Інтерактивні інструкції

---

### Документація

#### `README.md` (8.5 KB)
Головна документація проєкту:
- Опис особливостей
- Інструкція по встановленню
- Використання для гостей та адмінів
- Структура бази даних
- Майбутня інтеграція парсера
- Кастомізація
- Troubleshooting

#### `SETUP_GUIDE.md` (7.9 KB)
Детальна інструкція по налаштуванню:
- Покроковий швидкий старт
- Налаштування Supabase
- Конфігурація secrets
- Зміна паролю
- Деплой (Streamlit Cloud, Docker)
- Тестування
- Чеклист перед продакшеном

#### `API_DOCS.md` (9.1 KB)
Технічна API документація:
- Database Functions
- Cart Functions
- Authentication
- DB Helpers
- Data Models
- Security (RLS, Password Storage)
- API Endpoints
- Response Formats

#### `EXAMPLES.md` (14 KB)
Практичні приклади:
- Базові сценарії використання
- Робота з базою даних
- Аналітика та статистика
- Робота з кошиком
- Експорт/імпорт
- Управління паролями
- REST API приклади
- Розширення функціоналу

#### `CHANGELOG.md` (7.5 KB)
Історія версій та змін:
- v1.0.0 - Початковий реліз
- Unreleased features
- Future roadmap
- Contributing guidelines

---

### Конфігурація

#### `.streamlit/config.toml` (2.4 KB)
Налаштування Streamlit:
```toml
[theme]
primaryColor = "#00D9FF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1E2530"
textColor = "#FFFFFF"

[server]
port = 8501
headless = true
enableCORS = false
```

#### `.streamlit/secrets.toml.example` (2.1 KB)
Шаблон для secrets (НЕ в Git):
```toml
[supabase]
url = "https://your-project-id.supabase.co"
key = "your-anon-key-here"

[admin]
password_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
```

#### `.gitignore` (1.3 KB)
Файли та директорії, що ігноруються Git:
- `.streamlit/secrets.toml` - Секретні дані
- `venv/` - Віртуальне середовище
- `__pycache__/` - Python кеш
- `.vscode/`, `.idea/` - IDE файли

#### `LICENSE` (1.1 KB)
MIT License - дозвіл на використання, модифікацію та розповсюдження.

---

## 🗺️ Карта залежностей

```
app.py
├── supabase (БД)
├── streamlit (UI)
├── pandas (data manipulation)
└── db_helpers.py (утиліти)

db_helpers.py
├── supabase (БД)
├── pandas (data)
└── logging (logs)

test_setup.py
├── supabase (БД)
├── toml (config)
└── hashlib (auth)

quickstart.py
├── subprocess (commands)
└── pathlib (files)
```

---

## 🎯 Точки входу

### Для користувача:
```bash
streamlit run app.py
```
→ Відкриває веб-інтерфейс на http://localhost:8501

### Для розробника:
```bash
python test_setup.py        # Тестування
python quickstart.py         # Швидкий старт
python db_helpers.py         # Утиліти
```

---

## 💾 Структура даних

### Session State
```python
st.session_state = {
    'is_admin': bool,              # Статус адміна
    'cart': {                       # Кошик
        component_id: quantity
    },
    'selected_components': [],      # Обрані компоненти
    'last_sync': datetime           # Остання синхронізація
}
```

### Supabase Table: components
```
┌────────┬───────────────┬──────────┬────────────┬───────────┬─────────────┬─────────┐
│   id   │     name      │   type   │  category  │ price_uah │ stock_status│   url   │
├────────┼───────────────┼──────────┼────────────┼───────────┼─────────────┼─────────┤
│   1    │ T-Motor F60   │ квадрік  │  мотори    │  1250.00  │    true     │ https://│
│   2    │ iFlight Nazgul│ квадрік  │   рама     │  2200.00  │    true     │ https://│
└────────┴───────────────┴──────────┴────────────┴───────────┴─────────────┴─────────┘
```

---

## 📦 Модульність

Проєкт побудовано модульно для легкого розширення:

1. **app.py** - UI та основна логіка
2. **db_helpers.py** - Операції з БД (можна розширити)
3. **test_setup.py** - Тести (можна додати більше)
4. **Майбутні модулі:**
   - `parser.py` - Парсинг цін
   - `analytics.py` - Розширена аналітика
   - `notifications.py` - Сповіщення
   - `api.py` - REST API

---

## 🔮 Розширення

### Додавання нового модуля:

1. Створіть файл `new_module.py`
2. Імпортуйте в `app.py`:
   ```python
   from new_module import my_function
   ```
3. Додайте тести в `test_setup.py`
4. Оновіть документацію

### Додавання нової функції:

1. Додайте функцію в відповідний модуль
2. Додайте docstring
3. Додайте приклад в `EXAMPLES.md`
4. Оновіть `API_DOCS.md`
5. Додайте запис в `CHANGELOG.md`

---

## 📊 Статистика проєкту

| Метрика              | Значення    |
|----------------------|-------------|
| Файлів Python        | 4           |
| Рядків коду (Python) | ~2000       |
| Функцій              | 40+         |
| Документація (KB)    | 50+         |
| SQL запитів          | 100+        |
| Тестів               | 3           |
| Залежностей          | 8           |

---

**Версія структури:** 1.0.0  
**Оновлено:** March 4, 2026  
**© 2026 Drone Price System**
