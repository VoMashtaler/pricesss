# ============================================================================
# Інструкція по налаштуванню Drone Components Configurator
# ============================================================================

## 📝 Швидкий старт (Quick Start)

### 1. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 2. Налаштування Supabase

#### Крок 1: Створіть проєкт
- Зайдіть на https://supabase.com
- Натисніть "New Project"
- Виберіть організацію та введіть назву проєкту
- Виберіть регіон (найближчий до вас)
- Створіть надійний пароль для бази даних
- Натисніть "Create New Project" та дочекайтеся ініціалізації (~2 хвилини)

#### Крок 2: Виконайте SQL-схему
1. В меню зліва виберіть "SQL Editor"
2. Натисніть "New Query"
3. Скопіюйте весь вміст файлу `supabase_schema.sql`
4. Вставте в редактор і натисніть "Run" (або Ctrl+Enter)
5. Ви побачите повідомлення "Success. No rows returned"
6. Перевірте: Table Editor → components (повинна з'явитися таблиця з тестовими даними)

#### Крок 3: Отримайте API ключі
1. Settings (внизу зліва) → API
2. Скопіюйте:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGci...` (довгий ключ)

### 3. Налаштування Secrets

#### Для локальної розробки:

```bash
# Створіть директорію
mkdir -p .streamlit

# Скопіюйте шаблон
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Відредагуйте файл
nano .streamlit/secrets.toml
```

Заповніть реальні дані:
```toml
[supabase]
url = "ваш_project_url"
key = "ваш_anon_key"

[admin]
password_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
```

#### Для Streamlit Cloud:

1. Задеплойте додаток на Streamlit Cloud
2. Відкрийте Settings вашого додатку
3. Secrets → Edit
4. Вставте вміст у форматі TOML (як вище)
5. Збережіть (Save)

### 4. Зміна паролю адміністратора

```python
# Запустіть в терміналі Python:
python3 << EOF
import hashlib
password = "ваш_новий_супер_секретний_пароль"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(f"Ваш хеш: {hash_value}")
EOF
```

Скопіюйте отриманий хеш у `secrets.toml`:
```toml
[admin]
password_hash = "ваш_новий_хеш"
```

### 5. Запуск додатку

```bash
streamlit run app.py
```

Відкрийте браузер: http://localhost:8501

---

## 🔐 Безпека

### Важливі правила:

1. **НІКОЛИ** не додавайте `secrets.toml` до Git
2. **ЗАВЖДИ** використовуйте сильні паролі
3. **ЗМІНІТЬ** пароль за замовчуванням `admin123`
4. **ОНОВЛЮЙТЕ** регулярно API ключі
5. **ВИКОРИСТОВУЙТЕ** HTTPS в продакшені

### Генерація безпечного паролю:

```bash
# Linux/Mac
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Деплой

### Streamlit Cloud (Рекомендовано)

1. Завантажте код на GitHub
2. Зайдіть на https://streamlit.io/cloud
3. Підключіть GitHub репозиторій
4. Виберіть файл `app.py`
5. Додайте Secrets (Settings → Secrets)
6. Deploy!

### Docker (Advanced)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t drone-calculator .
docker run -p 8501:8501 drone-calculator
```

---

## 🧪 Тестування

### Перевірка підключення до Supabase:

```python
from supabase import create_client

url = "your_project_url"
key = "your_anon_key"

supabase = create_client(url, key)
result = supabase.table('components').select('*').limit(1).execute()

if result.data:
    print("✅ З'єднання успішне!")
    print(f"Знайдено {len(result.data)} записів")
else:
    print("❌ Помилка з'єднання")
```

### Перевірка авторизації:

```python
import hashlib

password = "admin123"
expected_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

actual_hash = hashlib.sha256(password.encode()).hexdigest()

if actual_hash == expected_hash:
    print("✅ Авторизація працює!")
else:
    print("❌ Неправильний пароль або хеш")
```

---

## 📊 Моніторинг

### Supabase Dashboard:
- Database → Tables → components: перегляд даних
- API → Logs: перегляд запитів
- Auth → Users: перегляд користувачів (якщо буде auth)

### Streamlit Analytics:
- Streamlit Cloud → Analytics
- Перегляд кількості відвідувачів
- Час роботи додатку

---

## 🐛 Відлагодження (Troubleshooting)

### Помилка: "KeyError: 'supabase'"
```
Рішення: Перевірте що secrets.toml існує в .streamlit/ директорії
та містить правильну структуру [supabase]
```

### Помилка: "Connection refused"
```
Рішення: 
1. Перевірте що Supabase проєкт активний
2. Перевірте правильність URL (без зайвих слешів)
3. Перевірте firewall налаштування
```

### Помилка: "Invalid API key"
```
Рішення:
1. Отримайте новий anon key з Supabase Dashboard
2. Оновіть secrets.toml
3. Рестартуйте додаток
```

### Таблиця порожня
```
Рішення:
1. Перевірте що SQL-схема виконана повністю
2. Подивіться Table Editor в Supabase
3. Виконайте INSERT запити з supabase_schema.sql вручну
```

---

## 📝 Чеклист перед продакшеном

- [ ] Змінено пароль адміністратора
- [ ] Додано .gitignore
- [ ] secrets.toml НЕ в Git
- [ ] SQL-схема виконана
- [ ] Тестові дані завантажені
- [ ] RLS політики налаштовані
- [ ] Перевірено всі функції
- [ ] Додано моніторинг помилок
- [ ] Налаштовано backup бази даних
- [ ] Документація оновлена

---

## 💡 Корисні команди

```bash
# Перевірка залежностей
pip list | grep streamlit

# Очистка кешу Streamlit
streamlit cache clear

# Запуск на іншому порту
streamlit run app.py --server.port 8502

# Запуск без автооновлення
streamlit run app.py --server.runOnSave false

# Дебаг режим
streamlit run app.py --logger.level debug

# Створення backup бази
pg_dump -h db.xxxxx.supabase.co -U postgres -d postgres > backup.sql
```

---

**Потрібна допомога?**
- 📖 Документація Streamlit: https://docs.streamlit.io
- 📖 Документація Supabase: https://supabase.com/docs
- 🐛 Issue Tracker: GitHub Issues

**Версія інструкції**: 1.0.0  
**Оновлено**: Березень 2026
