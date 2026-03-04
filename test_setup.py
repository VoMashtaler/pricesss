#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки підключення до Supabase
та базових операцій з базою даних
"""

import sys
from supabase import create_client
import os

def test_connection():
    """Перевірка підключення до Supabase"""
    print("=" * 60)
    print("🧪 Тестування підключення до Supabase")
    print("=" * 60)
    
    # Read secrets from environment or .streamlit/secrets.toml
    try:
        # Try environment variables first
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            # Try reading from secrets.toml
            import toml
            secrets = toml.load('.streamlit/secrets.toml')
            url = secrets['supabase']['url']
            key = secrets['supabase']['key']
        
        print(f"\n📡 URL: {url[:30]}...")
        print(f"🔑 Key: {key[:20]}...\n")
        
    except Exception as e:
        print(f"\n❌ Помилка читання конфігурації: {str(e)}")
        print("\nПереконайтеся що:")
        print("  1. Створено .streamlit/secrets.toml")
        print("  2. Або встановлено змінні оточення SUPABASE_URL та SUPABASE_KEY")
        return False
    
    try:
        # Create client
        supabase = create_client(url, key)
        print("✅ Клієнт Supabase створено")
        
        # Test connection
        response = supabase.table('components').select('*').limit(1).execute()
        print("✅ З'єднання з базою даних успішне")
        
        # Get count
        all_components = supabase.table('components').select('*').execute()
        count = len(all_components.data) if all_components.data else 0
        
        print(f"\n📊 Статистика:")
        print(f"   Компонентів в базі: {count}")
        
        if count > 0:
            print("\n📝 Приклад компонента:")
            example = all_components.data[0]
            print(f"   ID: {example.get('id')}")
            print(f"   Назва: {example.get('name')}")
            print(f"   Тип: {example.get('type')}")
            print(f"   Категорія: {example.get('category')}")
            print(f"   Ціна: {example.get('price_uah')} UAH")
            print(f"   В наявності: {'Так' if example.get('stock_status') else 'Ні'}")
        
        print("\n" + "=" * 60)
        print("✅ Всі тести пройдено успішно!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка підключення: {str(e)}")
        print("\nПеревірте:")
        print("  1. Правильність URL та API ключа")
        print("  2. Що SQL-схема виконана в Supabase")
        print("  3. Що таблиця 'components' існує")
        print("  4. RLS політики налаштовані")
        return False


def test_crud_operations():
    """Тестування CRUD операцій"""
    print("\n" + "=" * 60)
    print("🧪 Тестування CRUD операцій")
    print("=" * 60)
    
    try:
        # Setup
        import toml
        secrets = toml.load('.streamlit/secrets.toml')
        url = secrets['supabase']['url']
        key = secrets['supabase']['key']
        supabase = create_client(url, key)
        
        # CREATE
        print("\n1️⃣ CREATE: Додавання тестового компонента...")
        test_component = {
            'name': 'TEST Component (auto-generated)',
            'type': 'квадрік',
            'category': 'тестування',
            'price_uah': 999.99,
            'stock_status': True,
            'url': 'https://test.com'
        }
        
        create_response = supabase.table('components').insert(test_component).execute()
        test_id = create_response.data[0]['id']
        print(f"   ✅ Компонент створено з ID: {test_id}")
        
        # READ
        print("\n2️⃣ READ: Читання компонента...")
        read_response = supabase.table('components').select('*').eq('id', test_id).execute()
        print(f"   ✅ Компонент прочитано: {read_response.data[0]['name']}")
        
        # UPDATE
        print("\n3️⃣ UPDATE: Оновлення ціни...")
        supabase.table('components').update({'price_uah': 1999.99}).eq('id', test_id).execute()
        updated = supabase.table('components').select('*').eq('id', test_id).execute()
        print(f"   ✅ Ціна оновлена: {updated.data[0]['price_uah']} UAH")
        
        # DELETE
        print("\n4️⃣ DELETE: Видалення компонента...")
        supabase.table('components').delete().eq('id', test_id).execute()
        check = supabase.table('components').select('*').eq('id', test_id).execute()
        if not check.data:
            print(f"   ✅ Компонент видалено")
        
        print("\n" + "=" * 60)
        print("✅ Всі CRUD операції виконано успішно!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка CRUD операцій: {str(e)}")
        return False


def test_admin_auth():
    """Тестування авторизації адміністратора"""
    print("\n" + "=" * 60)
    print("🧪 Тестування авторизації")
    print("=" * 60)
    
    try:
        import hashlib
        import toml
        
        secrets = toml.load('.streamlit/secrets.toml')
        stored_hash = secrets['admin']['password_hash']
        
        # Test default password
        test_password = "admin123"
        test_hash = hashlib.sha256(test_password.encode()).hexdigest()
        
        print(f"\n🔐 Тестовий пароль: {test_password}")
        print(f"   Hash в конфігурації: {stored_hash[:30]}...")
        print(f"   Hash тестового паролю: {test_hash[:30]}...")
        
        if test_hash == stored_hash:
            print("\n   ✅ Хеш співпадає! Авторизація працює.")
            print("\n   ⚠️  УВАГА: Ви використовуєте пароль за замовчуванням!")
            print("   Рекомендується змінити пароль для безпеки.")
        else:
            print("\n   ℹ️  Хеш не співпадає - пароль змінено (це добре!)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка тестування авторизації: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n🚀 Запуск тестів Drone Components Configurator\n")
    
    # Run tests
    test_results = []
    
    test_results.append(("Підключення", test_connection()))
    test_results.append(("CRUD операції", test_crud_operations()))
    test_results.append(("Авторизація", test_admin_auth()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 ПІДСУМОК ТЕСТІВ")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(result for _, result in test_results)
    
    if all_passed:
        print("\n🎉 Всі тести пройдено! Система готова до використання.")
        sys.exit(0)
    else:
        print("\n⚠️  Деякі тести не пройшли. Перевірте конфігурацію.")
        sys.exit(1)
