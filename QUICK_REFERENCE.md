# 🚁 Drone Components Configurator - Quick Reference

## ⚡ Швидкий старт (5 хвилин)

### 1. Встановлення
```bash
# Клонуйте або завантажте проєкт
cd pricesss

# Автоматичне налаштування
python quickstart.py

# АБО вручну:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Налаштування Supabase
```bash
# 1. Створіть проєкт на https://supabase.com
# 2. Виконайте SQL: supabase_schema.sql
# 3. Скопіюйте URL та API key
```

### 3. Конфігурація
```bash
# Створіть .streamlit/secrets.toml
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
nano .streamlit/secrets.toml  # Додайте ваші credentials
```

### 4. Запуск
```bash
# Тести
python test_setup.py

# Додаток
streamlit run app.py
# → http://localhost:8501
```

---

## 📁 Структура файлів

```
pricesss/
├── app.py                    ⭐ Головний додаток
├── supabase_schema.sql       📊 SQL схема + дані
├── db_helpers.py             🔧 Утиліти БД
├── test_setup.py             🧪 Тести
├── quickstart.py             🚀 Швидкий старт
├── deploy.sh                 📦 Деплой скрипт
├── requirements.txt          📦 Залежності
├── README.md                 📖 Документація
├── SETUP_GUIDE.md            📘 Інструкції
├── API_DOCS.md               📚 API довідка
├── EXAMPLES.md               💡 Приклади
├── CHANGELOG.md              📝 Історія змін
├── PROJECT_STRUCTURE.md      🗺️ Архітектура
├── LICENSE                   ⚖️ MIT
├── .gitignore                🚫 Git ignore
└── .streamlit/
    ├── config.toml           ⚙️ Конфігурація
    └── secrets.toml.example  🔐 Шаблон secrets
```

---

## 🔑 Ключові команди

### Розробка
```bash
streamlit run app.py              # Запуск додатку
python test_setup.py              # Тести
python quickstart.py              # Налаштування
python db_helpers.py              # Утиліти БД
```

### Деплой
```bash
bash deploy.sh local              # Локально
bash deploy.sh streamlit-cloud    # Streamlit Cloud
bash deploy.sh docker             # Docker
bash deploy.sh heroku             # Heroku
```

### Docker
```bash
docker build -t drone-calculator .
docker run -p 8501:8501 drone-calculator
```

---

## 🎯 Основні функції

### Для гостей (без авторизації)
- ✅ Перегляд всіх компонентів
- ✅ Фільтрація за типом/категорією
- ✅ Готові пресети (камікадзе, FPV, літак, перехоплювач)
- ✅ Кастомна збірка
- ✅ Кошик з динамічним розрахунком
- ✅ Експорт в Excel

### Для адміністраторів (пароль: admin123)
- ✅ Додавання компонентів
- ✅ Масове редагування цін
- ✅ Видалення компонентів
- ✅ Перегляд статистики
- ✅ Синхронізація цін (майбутнє)

---

## 🗄️ База даних

### Таблиця: components
| Поле         | Тип          | Опис                          |
|--------------|--------------|-------------------------------|
| id           | BIGSERIAL    | Primary key                   |
| name         | VARCHAR(255) | Назва компонента              |
| type         | VARCHAR(50)  | квадрік/літак/перехоплювач    |
| category     | VARCHAR(100) | Категорія (мотори, ESC, ...)  |
| price_uah    | DECIMAL(10,2)| Ціна в гривнях                |
| stock_status | BOOLEAN      | В наявності                   |
| url          | TEXT         | Посилання на магазин          |
| created_at   | TIMESTAMP    | Дата створення                |
| updated_at   | TIMESTAMP    | Дата оновлення                |

### Приклади запитів
```python
# Всі компоненти
supabase.table('components').select('*').execute()

# Фільтр за типом
supabase.table('components').select('*').eq('type', 'квадрік').execute()

# Діапазон цін
supabase.table('components').select('*').gte('price_uah', 1000).lte('price_uah', 2000).execute()

# В наявності
supabase.table('components').select('*').eq('stock_status', True).execute()
```

---

## 🔐 Безпека

### Зміна пароля адміна
```python
import hashlib

password = "ваш_новий_пароль"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(f"Hash: {hash_value}")

# Додайте hash в .streamlit/secrets.toml:
# [admin]
# password_hash = "ваш_hash"
```

### Secrets файл
```toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJhbGci..."

[admin]
password_hash = "240be518..."  # SHA256 hash паролю
```

**⚠️ ВАЖЛИВО:**
- ❌ НЕ додавайте secrets.toml до Git
- ✅ Використовуйте .gitignore
- ✅ Змініть пароль за замовчуванням
- ✅ Регулярно оновлюйте credentials

---

## 📊 API Швидка довідка

### Database Functions
```python
from app import supabase

# CRUD операції
get_all_components()                          # SELECT *
get_components_by_type("квадрік")             # WHERE type
add_component(name, type, category, ...)      # INSERT
update_component(id, updates)                 # UPDATE
delete_component(id)                          # DELETE
```

### Cart Functions
```python
add_to_cart(component_id, quantity)    # Додати до кошика
get_cart_items()                        # Отримати товари
calculate_total()                       # Розрахувати суму
clear_cart()                            # Очистити кошик
```

### Helpers
```python
from db_helpers import *

export_components_to_csv(supabase)            # Експорт CSV
import_components_from_csv(supabase, file)    # Імпорт CSV
get_database_statistics(supabase)             # Статистика
search_components(supabase, "motor")          # Пошук
duplicate_component(supabase, id)             # Дублювання
```

---

## 🎨 Пресети

### Доступні конфігурації
| Пресет               | Тип          | Категорії                                    |
|----------------------|--------------|----------------------------------------------|
| 7-дюймовий камікадзе | квадрік      | мотори, рама, контролер, ESC                |
| 5-дюймовий FPV       | квадрік      | мотори, рама, пропелери, контролер          |
| Літак-розвідник      | літак        | двигун, ESC, сервоприводи, пропелер         |
| Перехоплювач         | перехоплювач | мотори, рама, бортовий комп'ютер, наведення |

### Додавання власного пресету
```python
# У app.py знайдіть DRONE_PRESETS:
DRONE_PRESETS = {
    "Мій пресет": {
        "type": "квадрік",
        "categories": ["мотори", "ESC", "рама"]
    }
}
```

---

## 🐛 Troubleshooting

### Помилка: "KeyError: 'supabase'"
```bash
# Рішення: Створіть .streamlit/secrets.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
nano .streamlit/secrets.toml
```

### Помилка: "Connection refused"
```bash
# Рішення: Перевірте Supabase credentials
python test_setup.py
```

### Таблиця порожня
```bash
# Рішення: Виконайте SQL схему в Supabase Dashboard
# SQL Editor → New Query → Paste supabase_schema.sql → Run
```

### Не працює авторизація
```python
# Рішення: Згенеруйте новий hash
import hashlib
print(hashlib.sha256("admin123".encode()).hexdigest())
```

---

## 📦 Залежності

```
streamlit >= 1.32.0      # Web framework
supabase >= 2.3.0        # Database client
pandas >= 2.2.0          # Data manipulation
openpyxl >= 3.1.2        # Excel support
```

### Встановлення
```bash
pip install -r requirements.txt
```

---

## 🔄 Workflow

### Для гостя
```
1. Відкрити додаток → http://localhost:8501
2. Обрати режим (Пресет / Кастом)
3. Додати компоненти до кошика
4. Переглянути загальну суму
5. Експортувати в Excel
```

### Для адміна
```
1. Увійти (пароль: admin123)
2. Додати/редагувати компоненти
3. Оновити ціни масово
4. Видалити застарілі позиції
5. Переглянути статистику
```

---

## 🚀 Деплой

### Streamlit Cloud
```bash
1. git push to GitHub
2. https://streamlit.io/cloud
3. Connect repository
4. Add secrets (Settings → Secrets)
5. Deploy!
```

### Docker
```bash
docker build -t drone-calculator .
docker run -p 8501:8501 \
  -v $(pwd)/.streamlit:/app/.streamlit \
  drone-calculator
```

### Heroku
```bash
heroku login
heroku create drone-calculator
git push heroku main
heroku open
```

---

## 📚 Документація

| Файл                  | Опис                              |
|-----------------------|-----------------------------------|
| README.md             | Основна документація              |
| SETUP_GUIDE.md        | Детальне налаштування             |
| API_DOCS.md           | Технічна API документація         |
| EXAMPLES.md           | Приклади використання             |
| PROJECT_STRUCTURE.md  | Архітектура проєкту               |
| CHANGELOG.md          | Історія версій                    |
| QUICK_REFERENCE.md    | Цей файл (швидка довідка)         |

---

## ⚡ Корисні посилання

- **Supabase Docs:** https://supabase.com/docs
- **Streamlit Docs:** https://docs.streamlit.io
- **Python Docs:** https://docs.python.org/3/

---

## 💡 Поради

### Продуктивність
```python
# Кешуйте дані
@st.cache_data(ttl=300)
def get_cached_components():
    return supabase.table('components').select('*').execute().data
```

### Безпека
```python
# Ніколи не коміттьте secrets
echo ".streamlit/secrets.toml" >> .gitignore
```

### Оптимізація запитів
```python
# Замість багатьох запитів:
components = supabase.table('components').select('*').in_('id', [1,2,3]).execute()
```

---

## 🆘 Підтримка

- **Issues:** GitHub Issues
- **Email:** support@example.com
- **Docs:** Дивіться файли документації

---

## 📝 Чеклист

### Перед запуском
- [ ] Python 3.10+ встановлено
- [ ] Залежності встановлено
- [ ] Supabase проєкт створено
- [ ] SQL схема виконана
- [ ] secrets.toml налаштовано
- [ ] Тести пройдено

### Перед продакшеном
- [ ] Пароль адміна змінено
- [ ] secrets.toml не в Git
- [ ] .gitignore налаштовано
- [ ] Backup БД створено
- [ ] Моніторинг налаштовано
- [ ] Документація оновлена

---

**Version:** 1.0.0  
**Last Updated:** March 4, 2026  
**© 2026 Drone Price System**

---

## 🎯 Наступні кроки

1. ✅ Прочитайте README.md
2. ✅ Виконайте SETUP_GUIDE.md
3. ✅ Запустіть test_setup.py
4. ✅ Перегляньте EXAMPLES.md
5. ✅ Почніть використовувати додаток!

**Успіхів! 🚀**
