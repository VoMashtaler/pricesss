import streamlit as st
import pandas as pd
from supabase import create_client, Client
import hashlib

# Конфігурація сторінки
st.set_page_config(page_title="Drone Configurator Pro", page_icon="🚁", layout="wide")

# Стилізація
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1e2530; }
    </style>
    """, unsafe_allow_html=True)

# Підключення до Supabase
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Помилка підключення: {e}")
        return None

supabase = init_connection()

# Функції отримання даних
def get_platforms():
    res = supabase.table("platforms").select("*").execute()
    return res.data

def get_components(platform_name):
    # Фільтруємо компоненти, де в масиві compatibility_tags є назва нашої платформи
    res = supabase.table("components").select("*").contains("compatibility_tags", [platform_name]).execute()
    return res.data

# Головний інтерфейс
st.title("🚁 Drone Configurator Pro")
st.markdown("---")

if supabase:
    platforms_data = get_platforms()

    if not platforms_data:
        st.warning("⚠️ Платформ не знайдено в базі даних (перевірте таблицю platforms)")
    else:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📍 Крок 1: Оберіть платформу")
            # Назви платформ: "10 дюймів", "13 дюймів", "15 дюймів"
            platform_names = [p['name'] for p in platforms_data]
            selected_platform_name = st.selectbox("Платформа", platform_names)
            
            # Шукаємо дані обраної платформи
            selected_platform = next(p for p in platforms_data if p['name'] == selected_platform_name)

            st.subheader("👤 Крок 2: Оберіть роль")
            # Використовуємо колонку allowed_roles зі скріншота
            selected_role = st.selectbox("Роль борту", selected_platform['allowed_roles'])

        with col2:
            st.info(f"💰 Базова ціна платформи: {selected_platform['base_price']} грн")
            st.write(f"📋 Обрано: **{selected_platform_name}** | Роль: **{selected_role}**")

        st.markdown("---")
        st.subheader("🔧 Крок 3: Комплектація")

        components = get_components(selected_platform_name)
        
        if not components:
            st.warning(f"⚠️ Для платформи '{selected_platform_name}' не знайдено сумісних компонентів.")
        else:
            # Групуємо по категоріях
            categories = sorted(list(set([c['category'] for c in components])))
            total_price = float(selected_platform['base_price'])
            
            for cat in categories:
                cat_items = [c for c in components if c['category'] == cat]
                
                # Логіка ролей: приховуємо плату ініціації для Бомбера
                if selected_role == "Бомбер" and cat == "Спецуха" and "ініціації" in cat_items[0]['name'].lower():
                    continue

                options = ["Не вибрано"] + [f"{c['name']} (+{c['price_uah']} грн)" for c in cat_items]
                choice = st.selectbox(f"Оберіть {cat}", options)
                
                if choice != "Не вибрано":
                    item_name = choice.split(" (+")[0]
                    item_data = next(c for c in cat_items if c['name'] == item_name)
                    total_price += float(item_data['price_uah'])

            st.markdown("---")
            st.header(f"💵 Загальна вартість: {total_price:,.2f} грн")

# Бічна панель
with st.sidebar:
    st.title("📊 Статистика")
    if supabase and platforms_data:
        st.write(f"Доступно платформ: {len(platforms_data)}")
    
    st.divider()
    st.markdown("🔒 **Вхід для адміна**")
    pwd = st.text_input("Пароль", type="password")
    if pwd:
        # Хеш для admin123
        if hashlib.sha256(pwd.encode()).hexdigest() == st.secrets["admin"]["password_hash"]:
            st.success("Ви увійшли як адмін")
            if st.button("Очистити кеш даних"):
                st.cache_resource.clear()
                st.rerun()
