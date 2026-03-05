import streamlit as st
import pandas as pd
from supabase import create_client

# Налаштування сторінки
st.set_page_config(page_title="Drone Configurator Pro", page_icon="🚁", layout="wide")

# Підключення до бази даних
@st.cache_resource
def get_db():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    except Exception as e:
        st.error(f"Помилка підключення до бази: {e}")
        return None

db = get_db()

st.title("🚁 Drone Configurator Pro")
st.markdown("---")

if db:
    try:
        # 1. Завантаження даних з Supabase
        p_res = db.table("platforms").select("*").execute()
        c_res = db.table("components").select("*").execute()
        
        if p_res.data and c_res.data:
            platforms = p_res.data
            all_components = c_res.data
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📍 Крок 1: База та Роль")
                # Вибір Платформи
                p_names = [p['name'] for p in platforms]
                sel_p_name = st.selectbox("Оберіть платформу", p_names)
                sel_p = next(p for p in platforms if p['name'] == sel_p_name)
                
                # Логіка ролей: прибираємо розвідку для 10, 13, 15 дюймів
                available_roles = [r for r in sel_p['allowed_roles'] if r != "Розвідник"]
                sel_role = st.selectbox("Оберіть роль борту", available_roles)
                
                # Автоматичне нарахування за спецобладнання (Спецуха)
                spec_price = 0
                spec_name = ""
                if sel_role == "Камікадзе":
                    spec_price = 1200
                    spec_name = "Плата ініціації"
                elif sel_role == "Бомбер":
                    spec_price = 2000
                    spec_name = "Система скиду + поворотка"

                st.info(f"⚙️ **Обладнання за роллю:** {spec_name} (+{spec_price} грн)")
                st.divider()

                st.subheader("🔧 Крок 2: Комплектація")
                
                # 1. Керування (Виправлено пошук ціни)
                ctrl_items = [c for c in all_components if c['category'] == 'Керування']
                ctrl_opts = [f"{c['name']} (+{c['price_uah']} грн)" for c in ctrl_items]
                sel_ctrl_raw = st.selectbox("📡 Система керування", ctrl_opts)
                # Точний пошук по назві без ціни
                chosen_ctrl_name = sel_ctrl_raw.split(" (+")[0]
                sel_ctrl = next(c for c in ctrl_items if c['name'] == chosen_ctrl_name)

                # 2. Відеосистема (Виправлено пошук ціни)
                video_items = [c for c in all_components if c['category'] == 'Відео']
                video_opts = [f"{c['name']} (+{c['price_uah']} грн)" for c in video_items]
                sel_video_raw = st.selectbox("📺 Відеосистема", video_opts)
                # Точний пошук по назві без ціни
                chosen_video_name = sel_video_raw.split(" (+")[0]
                sel_video = next(c for c in video_items if c['name'] == chosen_video_name)

                # 3. Антена (Автоматична привязка по частоті)
                antenna_price = 0
                sel_antenna_name = "Не потрібна / В комплекті"
                if sel_video['system_type'] == 'Analog':
                    # Витягуємо частоту з назви відео (наприклад "1.2-1.3Ghz")
                    v_freq = sel_video['name'].split(' ')[0] 
                    antennas = [c for c in all_components if c['category'] == 'Антени' and v_freq in c['name']]
                    if antennas:
                        sel_antenna = antennas[0]
                        antenna_price = float(sel_antenna['price_uah'])
                        sel_antenna_name = sel_antenna['name']
                        st.success(f"📡 Антена (авто): {sel_antenna_name} (+{antenna_price} грн)")
                    else:
                        st.warning("⚠️ Відповідну антену не знайдено в базі")
                else:
                    st.write("📡 Антена входить у вартість цифри")

                # 4. Камера (Тільки для аналогового відео)
                camera_price = 0
                camera_name = "Вбудована (Цифра)"
                if sel_video['system_type'] == 'Analog':
                    cam_items = [c for c in all_components if c['category'] == 'Камери']
                    cam_opts = [f"{c['name']} (+{c['price_uah']} грн)" for c in cam_items]
                    sel_cam_raw = st.selectbox("📷 Оберіть камеру", cam_opts)
                    chosen_cam_name = sel_cam_raw.split(" (+")[0]
                    sel_cam = next(c for c in cam_items if c['name'] == chosen_cam_name)
                    camera_price = float(sel_cam['price_uah'])
                    camera_name = sel_cam['name']
                else:
                    st.info("📷 Камера вже є в цифровому модулі")

            with col2:
                st.subheader("📊 Підсумок конфігурації")
                
                base_p = float(sel_p['base_price'])
                ctrl_p = float(sel_ctrl['price_uah'])
                video_p = float(sel_video['price_uah'])
                
                total = base_p + spec_price + ctrl_p + video_p + antenna_price + camera_price
                
                # Деталізація чека
                st.write(f"**База {sel_p_name}:** {base_p:,.0f} грн")
                st.write(f"**Роль {sel_role}:** {spec_price:,.0f} грн")
                st.write(f"**Керування ({sel_ctrl['name']}):** {ctrl_p:,.0f} грн")
                st.write(f"**Відео ({sel_video['name']}):** {video_p:,.0f} грн")
                if antenna_price > 0:
                    st.write(f"**Антена ({sel_antenna_name}):** {antenna_price:,.0f} грн")
                if camera_price > 0:
                    st.write(f"**Камера ({camera_name}):** {camera_price:,.0f} грн")
                
                st.divider()
                st.header(f"💵 Загальна вартість: {total:,.2f} грн")
                
                if st.button("📄 Сформувати короткий звіт"):
                    text_report = f"""ЗБІРКА: {sel_p_name} ({sel_role})
---
База: {base_p} грн
Керування: {sel_ctrl['name']}
Відео: {sel_video['name']}
Антена: {sel_antenna_name}
Камера: {camera_name}
---
РАЗОМ: {total} грн"""
                    st.code(text_report)

    except Exception as e:
        st.error(f"Виникла помилка при розрахунку: {e}")

# Бічна панель
with st.sidebar:
    st.write("📊 **Статистика бази**")
    if 'platforms' in locals(): st.write(f"Платформ: {len(platforms)}")
    st.divider()
    if st.button("🔄 Оновити дані з Supabase"):
        st.cache_resource.clear()
        st.rerun()
