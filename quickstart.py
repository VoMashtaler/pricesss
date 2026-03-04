"""
Швидкий старт - Готовий скрипт для налаштування проєкту
=========================================================
Виконайте цей скрипт для автоматичного налаштування середовища

Використання:
    python quickstart.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Друкує заголовок"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_step(number, text):
    """Друкує крок"""
    print(f"\n{number}. {text}")

def run_command(cmd, description):
    """Виконує команду"""
    print(f"   Виконується: {description}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"   ✅ {description} - успішно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} - помилка: {e}")
        return False

def check_python_version():
    """Перевіряє версію Python"""
    print_step(1, "Перевірка версії Python")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 10):
        print("   ✅ Версія Python підходить")
        return True
    else:
        print("   ❌ Потрібен Python 3.10 або новіше")
        return False

def create_venv():
    """Створює віртуальне середовище"""
    print_step(2, "Створення віртуального середовища")
    
    if Path("venv").exists():
        print("   ℹ️  Віртуальне середовище вже існує")
        return True
    
    return run_command("python -m venv venv", "Створення venv")

def install_dependencies():
    """Встановлює залежності"""
    print_step(3, "Встановлення залежностей")
    
    # Determine pip command based on OS
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Оновлення pip"),
        (f"{pip_cmd} install -r requirements.txt", "Встановлення пакетів")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def check_secrets_file():
    """Перевіряє наявність secrets.toml"""
    print_step(4, "Перевірка конфігурації")
    
    secrets_path = Path(".streamlit/secrets.toml")
    example_path = Path(".streamlit/secrets.toml.example")
    
    if secrets_path.exists():
        print("   ✅ Файл secrets.toml знайдено")
        
        # Check if it's configured
        with open(secrets_path, 'r') as f:
            content = f.read()
            if "your-project-id" in content or "your-anon-key" in content:
                print("   ⚠️  УВАГА: secrets.toml містить заглушки!")
                print("   📝 Відредагуйте .streamlit/secrets.toml з реальними даними Supabase")
                return False
        
        return True
    else:
        print("   ❌ Файл secrets.toml не знайдено")
        print("\n   Створюю з шаблону...")
        
        try:
            secrets_path.parent.mkdir(exist_ok=True)
            
            if example_path.exists():
                import shutil
                shutil.copy(example_path, secrets_path)
                print("   ✅ Файл створено з шаблону")
            else:
                # Create basic secrets file
                basic_secrets = """# Supabase Configuration
[supabase]
url = "https://your-project-id.supabase.co"
key = "your-anon-key-here"

# Admin Configuration
[admin]
password_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
"""
                with open(secrets_path, 'w') as f:
                    f.write(basic_secrets)
                print("   ✅ Базовий файл створено")
            
            print("\n   📝 ВАЖЛИВО: Відредагуйте .streamlit/secrets.toml:")
            print("      1. Додайте URL вашого Supabase проєкту")
            print("      2. Додайте anon key з Supabase Dashboard")
            print("      3. За бажанням змініть пароль адміністратора")
            
            return False
            
        except Exception as e:
            print(f"   ❌ Помилка створення файлу: {e}")
            return False

def display_next_steps():
    """Показує наступні кроки"""
    print_header("📋 НАСТУПНІ КРОКИ")
    
    print("""
1. Налаштуйте Supabase:
   - Створіть проєкт на https://supabase.com
   - Виконайте SQL-схему з файлу supabase_schema.sql
   - Скопіюйте URL та API ключ
   
2. Оновіть .streamlit/secrets.toml:
   - Додайте Supabase URL та API ключ
   - За бажанням змініть пароль адміністратора
   
3. Запустіть тести:
   - python test_setup.py
   
4. Запустіть додаток:
   - streamlit run app.py
   
📖 Детальна інструкція: SETUP_GUIDE.md
""")

def main():
    """Головна функція"""
    print_header("🚀 Drone Components Configurator - Швидкий старт")
    
    print("""
Цей скрипт підготує ваше середовище для роботи:
  • Перевірить версію Python
  • Створить віртуальне середовище
  • Встановить залежності
  • Створить конфігураційні файли
""")
    
    input("\nНатисніть Enter для продовження...")
    
    # Run setup steps
    steps = [
        check_python_version,
        create_venv,
        install_dependencies,
        check_secrets_file
    ]
    
    all_success = True
    for step in steps:
        if not step():
            all_success = False
            if step == check_secrets_file:
                # secrets.toml is expected to need manual config
                continue
            else:
                print("\n❌ Помилка на етапі налаштування. Зупинка.")
                sys.exit(1)
    
    # Final summary
    print_header("✅ БАЗОВЕ НАЛАШТУВАННЯ ЗАВЕРШЕНО")
    
    if all_success:
        print("\n🎉 Середовище підготовлено!")
        print("\n⚠️  Перед запуском:")
        print("   1. Налаштуйте Supabase (див. SETUP_GUIDE.md)")
        print("   2. Оновіть .streamlit/secrets.toml")
        print("   3. Запустіть тести: python test_setup.py")
    else:
        print("\nДеякі кроки потребують вашої уваги:")
        display_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Несподівана помилка: {e}")
        sys.exit(1)
