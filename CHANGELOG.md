# Changelog

Всі важливі зміни в проєкті будуть задокументовані в цьому файлі.

Формат базується на [Keep a Changelog](https://keepachangelog.com/uk/1.0.0/),
та цей проєкт дотримується [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-04

### 🎉 Початковий реліз

#### Added
- ✨ Повнофункціональний веб-додаток на Streamlit
- 🗄️ Інтеграція з Supabase для зберігання даних
- 👑 Адміністративна панель з авторизацією
- 🛒 Система кошика для розрахунку вартості
- 📦 Готові пресети для швидкого підбору комплектуючих
- 🎨 Кастомні конфігурації з фільтрами
- 🌙 Dark Mode інтерфейс
- 📥 Експорт замовлення в Excel
- 🔐 SHA256 хешування паролів
- 📊 Статистика та аналітика в sidebar
- 🔄 Архітектура для майбутньої інтеграції парсинг-агента

#### Components
- `app.py` - Головний файл додатку (580+ рядків)
- `supabase_schema.sql` - SQL схема бази даних з тестовими даними
- `db_helpers.py` - Допоміжні функції для роботи з БД
- `test_setup.py` - Автоматизовані тести налаштування
- `quickstart.py` - Скрипт швидкого старту
- `requirements.txt` - Python залежності

#### Documentation
- `README.md` - Повна документація проєкту
- `SETUP_GUIDE.md` - Детальна інструкція по налаштуванню
- `API_DOCS.md` - Технічна API документація
- `EXAMPLES.md` - Практичні приклади використання
- `LICENSE` - MIT ліцензія

#### Configuration
- `.streamlit/config.toml` - Налаштування Streamlit
- `.streamlit/secrets.toml.example` - Шаблон для secrets
- `.gitignore` - Git ignore правила

#### Database
- Таблиця `components` з полями:
  - `id` (BIGSERIAL PRIMARY KEY)
  - `name` (VARCHAR 255)
  - `type` (VARCHAR 50) - квадрік/літак/перехоплювач
  - `category` (VARCHAR 100)
  - `price_uah` (DECIMAL 10,2)
  - `stock_status` (BOOLEAN)
  - `url` (TEXT)
  - `created_at`, `updated_at` (TIMESTAMP)
- RLS політики для безпеки
- Індекси для оптимізації
- 30+ тестових компонентів

#### Features - Admin Panel
- ➕ Додавання нових компонентів
- ✏️ Масове редагування через `st.data_editor`
- 🗑️ Видалення компонентів
- 🔄 Синхронізація цін (заглушка для майбутнього)

#### Features - Guest Panel
- 📦 Готові пресети:
  - 7-дюймовий камікадзе
  - 5-дюймовий FPV
  - Літак-розвідник
  - Перехоплювач
- 🎨 Кастомна збірка з фільтрами:
  - За типом апарату
  - За категорією компонентів
  - Динамічне додавання до кошика
- 🛒 Інтерактивний кошик:
  - Перегляд обраних компонентів
  - Зміна кількості
  - Видалення позицій
  - Динамічний перерахунок суми
  - Посилання на магазини
- 📥 Експорт в Excel з повною специфікацією

#### Presets
- `7-дюймовий камікадзе` - квадрокоптер з моторами, рамою, ESC, контролером
- `5-дюймовий FPV` - FPV дрон з повним комплектом
- `Літак-розвідник` - фіксоване крило з двигуном та сервоприводами
- `Перехоплювач` - спеціалізована платформа з системою наведення

#### Security
- Хешування паролів SHA256
- Суpabase Row Level Security (RLS)
- Secrets management через `.streamlit/secrets.toml`
- `.gitignore` для захисту конфіденційних даних

#### Testing
- `test_setup.py` - Автоматичні тести:
  - Перевірка підключення до Supabase
  - CRUD операції
  - Авторизація адміністратора
  - Детальна звітність

#### UI/UX
- Сучасний Dark Mode дизайн
- Градієнтні кнопки з hover ефектами
- Кольорові бейджі для ролей
- Responsive layout
- Інтерактивні таблиці
- Інформативні картки компонентів
- Анімації та тіні

---

## [Unreleased] - Майбутні версії

### 🔮 Planned Features (v1.1.0)

#### Price Parser Agent
- [ ] Автоматичний парсинг цін з магазинів
- [ ] Інтеграція з BeautifulSoup/Selenium
- [ ] Scheduler для регулярних оновлень
- [ ] Історія змін цін
- [ ] Сповіщення про зміни

#### Enhanced Analytics
- [ ] Графіки цін (Chart.js/Plotly)
- [ ] Порівняння цін по категоріях
- [ ] Trending компоненти
- [ ] Price alerts

#### User Management
- [ ] Система реєстрації користувачів
- [ ] Збережені конфігурації
- [ ] Історія замовлень
- [ ] Улюблені компоненти

#### Additional Features
- [ ] Мультимовна підтримка (UA/EN/RU)
- [ ] Калькулятор доставки
- [ ] Порівняння різних збірок
- [ ] Рекомендації на основі бюджету
- [ ] PDF експорт замовлень
- [ ] API для зовнішніх інтеграцій

---

## [Future Roadmap]

### v1.2.0 - Advanced Features
- Real-time price updates
- Inventory management
- Supplier integration
- Order tracking system

### v1.3.0 - Mobile & PWA
- Progressive Web App
- Mobile-optimized UI
- Offline mode
- Push notifications

### v2.0.0 - Enterprise
- Multi-tenancy
- Advanced analytics dashboard
- Custom branding
- API marketplace
- Microservices architecture

---

## Version History Summary

| Version | Date       | Highlights                    |
|---------|------------|-------------------------------|
| 1.0.0   | 2026-03-04 | Початковий реліз              |

---

## Contributing

Щоб внести зміни до Changelog:
1. Додайте зміни під секцію `[Unreleased]`
2. При релізі створіть нову секцію з версією та датою
3. Використовуйте категорії: Added, Changed, Deprecated, Removed, Fixed, Security

### Категорії змін

- **Added** - нові функції
- **Changed** - зміни в існуючому функціоналі
- **Deprecated** - функції, які скоро будуть видалені
- **Removed** - видалені функції
- **Fixed** - виправлення помилок
- **Security** - виправлення вразливостей

---

**Maintained by:** Drone Price System Team  
**Last Updated:** March 4, 2026
