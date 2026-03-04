# Contributing to Drone Components Configurator

Дякуємо за інтерес до проєкту! Ми раді вашій участі.

## 📋 Зміст

- [Code of Conduct](#code-of-conduct)
- [Як допомогти](#як-допомогти)
- [Процес розробки](#процес-розробки)
- [Стандарти коду](#стандарти-коду)
- [Тестування](#тестування)
- [Документація](#документація)
- [Комміти](#комміти)

---

## 📜 Code of Conduct

### Наші цінності

- **Повага:** Поважайте всіх учасників
- **Інклюзивність:** Всі Welcome незалежно від досвіду
- **Конструктивність:** Критика має бути конструктивною
- **Відкритість:** Прозора комунікація

### Неприйнятна поведінка

- Образи, тролінг, провокації
- Дискримінація будь-якого виду
- Спам або нерелевантний контент
- Порушення приватності інших

---

## 🤝 Як допомогти

### Способи участі

1. **Звіти про помилки (Bug Reports)**
   - Опишіть проблему детально
   - Додайте кроки відтворення
   - Вкажіть очікувану поведінку
   - Додайте скріншоти якщо є

2. **Пропозиції функцій (Feature Requests)**
   - Опишіть бажану функцію
   - Поясніть use case
   - Запропонуйте реалізацію

3. **Покращення документації**
   - Виправлення помилок
   - Додавання прикладів
   - Переклади

4. **Код (Pull Requests)**
   - Виправлення помилок
   - Нові функції
   - Оптимізація

5. **Тестування**
   - Написання нових тестів
   - Покращення покриття

---

## 🔄 Процес розробки

### 1. Fork & Clone

```bash
# Fork репозиторій на GitHub
# Потім clone:
git clone https://github.com/your-username/pricesss.git
cd pricesss
```

### 2. Створення гілки

```bash
# Оновіть main
git checkout main
git pull origin main

# Створіть feature гілку
git checkout -b feature/your-feature-name

# Або bugfix гілку
git checkout -b bugfix/issue-description
```

### 3. Налаштування середовища

```bash
# Віртуальне середовище
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Залежності
pip install -r requirements.txt

# Додаткові dev залежності
pip install pytest black flake8 mypy
```

### 4. Внесення змін

```bash
# Редагуйте код
# Дотримуйтесь стандартів (див. нижче)

# Перевірте code style
black app.py
flake8 app.py

# Запустіть тести
python test_setup.py
pytest  # якщо є pytest тести
```

### 5. Commit & Push

```bash
# Додати зміни
git add .

# Commit з осмисленим повідомленням
git commit -m "feat: додано функцію експорту в PDF"

# Push в ваш fork
git push origin feature/your-feature-name
```

### 6. Pull Request

1. Відкрийте GitHub
2. Перейдіть в ваш fork
3. Натисніть "Pull Request"
4. Заповніть опис:
   - Що робить ваш PR
   - Як тестували
   - Які issue вирішені

---

## 💻 Стандарти коду

### Python Style Guide

#### PEP 8
Дотримуємось [PEP 8](https://pep8.org/)

```python
# ✅ Добре
def calculate_total(items: List[Dict]) -> float:
    """Розраховує загальну суму."""
    return sum(item['price'] * item['quantity'] for item in items)

# ❌ Погано
def calc_tot(items):
    return sum([item['price']*item['quantity'] for item in items])
```

#### Naming Conventions

```python
# Змінні та функції: snake_case
user_name = "John"
def get_user_data():
    pass

# Класи: PascalCase
class UserManager:
    pass

# Константи: UPPER_CASE
MAX_RETRY_COUNT = 3
API_TIMEOUT = 30
```

#### Docstrings

```python
def add_component(name: str, price: float) -> bool:
    """
    Додає новий компонент до бази даних.
    
    Args:
        name (str): Назва компонента
        price (float): Ціна в гривнях
    
    Returns:
        bool: True якщо успішно, False інакше
    
    Example:
        >>> add_component("T-Motor F60", 1250.00)
        True
    """
    # Implementation
    pass
```

#### Type Hints

```python
from typing import List, Dict, Optional

def process_items(
    items: List[Dict],
    discount: Optional[float] = None
) -> Dict[str, float]:
    """Обробляє список товарів."""
    # Implementation
    return {"total": 0.0, "discount": 0.0}
```

### Code Formatting

#### Black
Ми використовуємо [Black](https://github.com/psf/black) для форматування:

```bash
# Форматування одного файлу
black app.py

# Форматування всього проєкту
black .

# Перевірка без змін
black --check .
```

#### Flake8
Для linting використовуємо [Flake8](https://flake8.pycqa.org/):

```bash
# Перевірка
flake8 app.py

# Конфігурація в setup.cfg:
[flake8]
max-line-length = 100
exclude = venv,.git,__pycache__
```

---

## 🧪 Тестування

### Структура тестів

```
tests/
├── test_database.py      # Тести БД операцій
├── test_cart.py          # Тести кошика
├── test_auth.py          # Тести авторизації
└── test_helpers.py       # Тести утиліт
```

### Написання тестів

```python
import pytest
from app import add_to_cart, calculate_total

def test_add_to_cart():
    """Тест додавання до кошика."""
    # Arrange
    component_id = 1
    quantity = 2
    
    # Act
    add_to_cart(component_id, quantity)
    
    # Assert
    assert st.session_state.cart[component_id] == quantity

def test_calculate_total():
    """Тест розрахунку суми."""
    # Setup test data
    st.session_state.cart = {1: 2, 2: 3}
    
    # Calculate
    total = calculate_total()
    
    # Assert
    assert total > 0
```

### Запуск тестів

```bash
# Існуючі тести
python test_setup.py

# pytest (якщо встановлено)
pytest tests/

# З покриттям
pytest --cov=. tests/
```

### Вимоги до PR

- ✅ Всі тести проходять
- ✅ Додано нові тести для нового коду
- ✅ Покриття не зменшилось

---

## 📚 Документація

### Структура документації

```
README.md            - Основна документація
SETUP_GUIDE.md       - Налаштування
API_DOCS.md          - API довідка
EXAMPLES.md          - Приклади
CHANGELOG.md         - Історія змін
```

### Оновлення документації

При додаванні нової функції:

1. **README.md** - Додати в список Features
2. **API_DOCS.md** - Документувати API
3. **EXAMPLES.md** - Додати приклади
4. **CHANGELOG.md** - Додати в [Unreleased]

### Markdown стиль

```markdown
# H1 - Тільки для заголовка файлу

## H2 - Основні розділи

### H3 - Підрозділи

#### H4 - Деталі

**Bold** - Виділення
*Italic* - Курсив
`code` - Інлайн код

```python
# Блок коду
def example():
    pass
```
```

---

## 📝 Комміти

### Commit Message Format

Використовуємо [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat:** Нова функція
- **fix:** Виправлення помилки
- **docs:** Зміни в документації
- **style:** Форматування (без змін логіки)
- **refactor:** Рефакторинг коду
- **test:** Додавання тестів
- **chore:** Допоміжні зміни (builds, tools)

### Examples

```bash
# Нова функція
git commit -m "feat(cart): додано експорт кошика в PDF"

# Виправлення
git commit -m "fix(database): виправлено помилку підключення до Supabase"

# Документація
git commit -m "docs(readme): оновлено інструкції по встановленню"

# Рефакторинг
git commit -m "refactor(helpers): оптимізовано функцію search_components"

# З body
git commit -m "feat(admin): масове видалення компонентів

Додано функціонал для видалення декількох компонентів одночасно
через чекбокси в таблиці. Покращує UX адміністратора.

Closes #42"
```

---

## 🔍 Code Review Process

### Що перевіряємо

1. **Функціональність**
   - Код працює як очікується
   - Немає регресій

2. **Якість коду**
   - Дотримання стандартів
   - Читабельність
   - Документованість

3. **Тести**
   - Наявність тестів
   - Покриття нового коду

4. **Документація**
   - Оновлена при необхідності
   - Зрозуміла

5. **Безпека**
   - Немає вразливостей
   - Валідація даних

### Процес

1. Автор створює PR
2. Ревьюери залишають коментарі
3. Автор вносить зміни
4. Після approve - merge

---

## 🎯 Priority Labels

- **critical** - Критичні помилки
- **bug** - Звичайні помилки
- **enhancement** - Покращення
- **feature** - Нові функції
- **documentation** - Документація
- **good first issue** - Для початківців
- **help wanted** - Потрібна допомога

---

## 📞 Комунікація

### Де обговорювати

- **GitHub Issues** - Помилки та пропозиції
- **Pull Requests** - Обговорення коду
- **Discussions** - Загальні питання
- **Email** - support@example.com

### Час відповіді

- Issues: 1-3 дні
- PR: 2-5 днів
- Критичні: 24 години

---

## 🎓 Resources

### Навчальні матеріали

- **Python:** https://docs.python.org/3/tutorial/
- **Streamlit:** https://docs.streamlit.io
- **Supabase:** https://supabase.com/docs
- **Git:** https://git-scm.com/doc

### Корисні інструменти

- **Black:** https://black.readthedocs.io/
- **Flake8:** https://flake8.pycqa.org/
- **pytest:** https://docs.pytest.org/
- **mypy:** http://mypy-lang.org/

---

## 🌟 Recognition

Всі контриб'ютори будуть додані в:
- README.md (секція Contributors)
- CHANGELOG.md (зазначення автора змін)

---

## ❓ FAQ

### Q: Як почати контриб'ютити?
A: Шукайте issues з лейблом "good first issue"

### Q: Скільки часу займає review?
A: Зазвичай 2-5 днів

### Q: Чи потрібен досвід?
A: Ні! Вітаємо контриб'ютори будь-якого рівня

### Q: Як запропонувати нову функцію?
A: Створіть issue з описом та use case

---

## 📄 License

Контриб'ютячи в проєкт, ви погоджуєтесь з MIT License.

---

## 🙏 Подяка

Дякуємо всім, хто допомагає робити цей проєкт кращим!

---

**Happy Contributing! 🚀**

**Version:** 1.0.0  
**Last Updated:** March 4, 2026
