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

# Словник складу платформ (згідно з твоїми даними)
platform_details = {
    "10 дюймів": [
        "Мотори 3115 900kv (4 шт) — 4000 грн",
        "Рама Mark4 10 — 1100 грн",
        "Пропелери (4 шт) — 500 грн",
        "Польотник F405 + ESC — 2600 грн",
        "Батарея 6s3p — 4000 грн",
        "Стрепи (2 шт) — 40 грн"
    ],
    "13 дюймів": [
        "Мотори 4320 640kv (4 шт) — 9600 грн",
        "Рама Mark4 13 — 2100 грн",
        "Пропелери (4 шт) — 1000 грн",
        "Польотник F405 + ESC — 4000 грн",
        "Батарея 8s3p — 5400 грн",
        "Стрепи (2 шт) — 40 грн"
    ],
    "15 дюймів": [
        "Мотори 4320 380kv (4 шт) — 9600 грн",
        "Рама Mark4 15 — 3400 грн",
        "Пропелери (4 шт) — 1300 грн",
        "Польотник F405 + ESC — 4000 грн",
        "Батарея 8s4p — 7500 грн",
        "Стрепи (2 шт) — 40 грн"
    ]
}

st.title("🚁 Drone Configurator Pro")
st.markdown("---")

if db:
    try:
        p_res = db.table("platforms").select("*").execute()
        c_res = db.table("components").select("*").execute()
        
        if p_res.data and c_res.data:
            platforms = p_res.data
            all_components = c_res.data
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📍 Крок 1: База та Роль")
                p_names = [p['name'] for p in platforms]
                sel_p_name = st.selectbox("Оберіть платформу", p_names)
                sel_p = next(p for p in platforms if p['name'] == sel_p_name)
                
                # Деталізація складу платформи
                with st.expander(f"🔍 Що входить у базу {sel_p_name}?"):
                    for item in platform_details.get(sel_p_name, []):
                        st.write(f"• {item}")

                available_roles = [r for r in sel_p['allowed_roles'] if r != "Розвідник"]
                sel_role = st.selectbox("Оберіть роль борту", available_roles)
                
                spec_price = 1200 if sel_role == "Камікадзе" else 2000
                spec_name = "Плата ініціації" if sel_role == "Камікадзе" else "Система скиду + поворотка"
                st.info(f"⚙️ **Обладнання:** {spec_name} (+{spec_price} грн)")
                
                st.divider()
                st.subheader("🔧 Крок 2: Комплектація")
                
                # Керування
                ctrl_items = [c for c in all_components if c['category'] == 'Керування']
                sel_ctrl_raw = st.selectbox("📡 Система керування", [f"{c['name']} (+{c['price_uah']} грн)" for c in ctrl_items])
                sel_ctrl = next(c for c in ctrl_items if c['name'] == sel_ctrl_raw.split(" (+")[0])

                # Відеосистема
                video_items = [c for c in all_components if c['category'] == 'Відео']
                sel_video_raw = st.selectbox("📺 Відеосистема", [f"{c['name']} (+{c['price_uah']} грн)" for c in video_items])
                sel_video = next(c for c in video_items if c['name'] == sel_video_raw.split(" (+")[0])

                # Авто-антена
                antenna_price = 0
                sel_antenna_name = "В комплекті"
                if sel_video['system_type'] == 'Analog':
                    v_freq = sel_video['name'].split(' ')[0] 
                    antennas = [c for c in all_components if c['category'] == 'Антени' and v_freq in c['name']]
                    if antennas:
                        sel_antenna = antennas[0]
                        antenna_price = float(sel_antenna['price_uah'])
                        sel_antenna_name = sel_antenna['name']
                        st.success(f"📡 Антена (авто): {sel_antenna_name} (+{antenna_price} грн)")

                # Камера
                camera_price = 0
                camera_name = "Вбудована"
                if sel_video['system_type'] == 'Analog':
                    cam_items = [c for c in all_components if c['category'] == 'Камери']
                    sel_cam_raw = st.selectbox("📷 Оберіть камеру", [f"{c['name']} (+{c['price_uah']} грн)" for c in cam_items])
                    sel_cam = next(c for c in cam_items if c['name'] == sel_cam_raw.split(" (+")[0])
                    camera_price = float(sel_cam['price_uah'])
                    camera_name = sel_cam['name']

            with col2:
                st.subheader("📊 Підсумок конфігурації")
                base_p = float(sel_p['base_price'])
                total = base_p + spec_price + float(sel_ctrl['price_uah']) + float(sel_video['price_uah']) + antenna_price + camera_price
                
                st.write(f"**База {sel_p_name}:** {base_p:,.0f} грн")
                st.write(f"**Обладнання ({sel_role}):** {spec_price:,.0f} грн")
                st.write(f"**Керування:** {sel_ctrl['name']} ({sel_ctrl['price_uah']} грн)")
                st.write(f"**Відео:** {sel_video['name']} ({sel_video['price_uah']} грн)")
                if antenna_price > 0: st.write(f"**Антена:** {sel_antenna_name} ({antenna_price} грн)")
                if camera_price > 0: st.write(f"**Камера:** {camera_name} ({camera_price} грн)")
                
                st.divider()
                st.header(f"💵 Разом: {total:,.2f} грн")
                
                if st.button("📄 Сформувати короткий звіт"):
                    report = f"ЗБІРКА: {sel_p_name} ({sel_role})\nБаза: {base_p} грн\nКерування: {sel_ctrl['name']}\nВідео: {sel_video['name']}\nРАЗОМ: {total} грн"
                    st.code(report)

    except Exception as e:
        st.error(f"Помилка: {e}")

with st.sidebar:
    if st.button("🔄 Оновити дані"):
        st.cache_resource.clear()
        st.rerun()
