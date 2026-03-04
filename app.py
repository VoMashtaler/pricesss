import streamlit as st
import pandas as pd
from supabase import create_client

# Налаштування без зайвого пафосу
st.set_page_config(page_title="Drone Configurator", layout="wide")

# Підключення
@st.cache_resource
def init_db():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

db = init_db()

# Головний заголовок
st.title("🚁 Drone Configurator Pro")

try:
    # Отримуємо платформи
    p_res = db.table("platforms").select("*").execute()
    platforms = p_res.data

    if not platforms:
        st.error("База платформ порожня. Перевір таблицю 'platforms' в Supabase.")
    else:
        # Крок 1: Платформа
        p_names = [p['name'] for p in platforms]
        sel_p_name = st.selectbox("📍 Оберіть платформу", p_names)
        sel_p = next(p for p in platforms if p['name'] == sel_p_name)
        
        # Крок 2: Роль
        sel_role = st.selectbox("👤 Оберіть роль", sel_p['allowed_roles'])
        
        st.info(f"💰 Базова ціна: {sel_p['base_price']} грн")
        st.divider()

        # Крок 3: Компоненти
        c_res = db.table("components").select("*").contains("compatibility_tags", [sel_p_name]).execute()
        components = c_res.data

        if not components:
            st.warning("Компонентів не знайдено.")
        else:
            cats = sorted(list(set([c['category'] for c in components])))
            total = float(sel_p['base_price'])
            
            for cat in cats:
                items = [c for c in components if c['category'] == cat]
                # Простий вибір без мудрованої логіки
                opts = ["Не вибрано"] + [f"{i['name']} (+{i['price_uah']} грн)" for i in items]
                choice = st.selectbox(f"Оберіть {cat}", opts)
                
                if choice != "Не вибрано":
                    c_name = choice.split(" (+")[0]
                    c_data = next(i for i in items if i['name'] == c_name)
                    total += float(c_data['price_uah'])

            st.markdown(f"### 💵 Загальна вартість: {total:,.2f} грн")

except Exception as e:
    st.error(f"Помилка в коді: {e}")

# Проста адмінка внизу
with st.sidebar:
    st.write("### Статистика")
    if 'platforms' in locals(): st.write(f"Платформ: {len(platforms)}")
    if st.button("🔄 Оновити дані"):
        st.cache_resource.clear()
        st.rerun()
