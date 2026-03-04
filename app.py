import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Drone Configurator", layout="wide")

# Витягуємо ключі та перевіряємо їх наявність
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
except Exception as e:
    st.error(f"❌ Помилка в Secrets: {e}")
    st.stop()

# Ініціалізація клієнта
@st.cache_resource
def get_db():
    return create_client(url, key)

db = get_db()

st.title("🚁 Drone Configurator Pro")

# Діагностика підключення
try:
    # Пробуємо отримати дані
    response = db.table("platforms").select("*").execute()
    
    # Виводимо сирі дані для діагностики (потім видалимо)
    if not response.data:
        st.warning("⚠️ Supabase повернув порожній список. Перевірте RLS Policies (Крок 1 вище).")
        if st.button("🔄 Оновити"):
            st.cache_resource.clear()
            st.rerun()
    else:
        platforms = response.data
        p_names = [p['name'] for p in platforms]
        
        col1, col2 = st.columns(2)
        with col1:
            sel_p_name = st.selectbox("📍 Платформа", p_names)
            sel_p = next(p for p in platforms if p['name'] == sel_p_name)
            
            # Ролі (allowed_roles — це масив у базі)
            roles = sel_p.get('allowed_roles', [])
            sel_role = st.selectbox("👤 Роль", roles)

        with col2:
            st.success(f"💰 Базова ціна: {sel_p['base_price']} грн")
            
        st.divider()

        # Завантаження компонентів
        c_res = db.table("components").select("*").contains("compatibility_tags", [sel_p_name]).execute()
        if c_res.data:
            df_c = pd.DataFrame(c_res.data)
            for cat in df_c['category'].unique():
                items = df_c[df_c['category'] == cat]
                opts = ["Не вибрано"] + [f"{r['name']} (+{r['price_uah']} грн)" for _, r in items.iterrows()]
                st.selectbox(f"Оберіть {cat}", opts)

except Exception as e:
    st.error(f"💥 Критична помилка: {e}")

with st.sidebar:
    st.write(f"🔗 URL: {url}")
    if st.button("🧹 Очистити кеш"):
        st.cache_resource.clear()
        st.rerun()
