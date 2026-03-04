import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Drone Configurator", layout="wide")

# Підключення
@st.cache_resource
def get_db():
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])

db = get_db()

st.title("🚁 Drone Configurator Pro")

try:
    # 1. Завантаження даних
    p_res = db.table("platforms").select("*").execute()
    c_res = db.table("components").select("*").execute()
    
    if p_res.data and c_res.data:
        platforms = p_res.data
        all_components = c_res.data
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Вибір Платформи
            p_names = [p['name'] for p in platforms]
            sel_p_name = st.selectbox("📍 Оберіть платформу", p_names)
            sel_p = next(p for p in platforms if p['name'] == sel_p_name)
            
            # Логіка ролей: прибираємо розвідку для великих рам
            available_roles = [r for r in sel_p['allowed_roles'] if r != "Розвідник"]
            sel_role = st.selectbox("👤 Роль борту", available_roles)
            
            # Авто-нарахування за спецобладнання
            spec_price = 0
            spec_name = ""
            if sel_role == "Камікадзе":
                spec_price = 1200
                spec_name = "Плата ініціації"
            elif sel_role == "Бомбер":
                spec_price = 2000
                spec_name = "Система скиду + поворотка"

            st.markdown(f"**Обладнання:** {spec_name} (+{spec_price} грн)")
            
            # Крок 1: Керування
            ctrl_items = [c for c in all_components if c['category'] == 'Керування']
            sel_ctrl_raw = st.selectbox("📡 Керування", [f"{c['name']} (+{c['price_uah']} грн)" for c in ctrl_items])
            sel_ctrl = next(c for c in ctrl_items if sel_ctrl_raw.startswith(c['name']))

            # Крок 2: Відео
            video_items = [c for c in all_components if c['category'] == 'Відео']
            sel_video_raw = st.selectbox("📺 Відеосистема", [f"{c['name']} (+{c['price_uah']} грн)" for c in video_items])
            sel_video = next(c for c in video_items if sel_video_raw.startswith(c['name']))

            # Крок 3: Антена (Автоматична привязка по частоті)
            antenna_price = 0
            sel_antenna = None
            if sel_video['system_type'] == 'Analog':
                # Шукаємо антену, яка має ту саму частоту в назві, що і відеопередавач
                # Наприклад, відео "1.2-1.3Ghz" -> антена "1.2-1.3Ghz"
                v_freq = sel_video['name'].split(' ')[0] 
                antennas = [c for c in all_components if c['category'] == 'Антени' and v_freq in c['name']]
                if antennas:
                    sel_antenna = antennas[0]
                    antenna_price = sel_antenna['price_uah']
                    st.success(f"✅ Антена підібрана: {sel_antenna['name']} (+{antenna_price} грн)")
                else:
                    st.warning("⚠️ Відповідну антену не знайдено в базі")
            else:
                st.info("ℹ️ Для цифрових систем антена зазвичай у комплекті")

            # Крок 4: Камера (тільки для Аналогу)
            camera_price = 0
            if sel_video['system_type'] == 'Analog':
                cam_items = [c for c in all_components if c['category'] == 'Камери']
                sel_cam_raw = st.selectbox("📷 Камера", [f"{c['name']} (+{c['price_uah']} грн)" for c in cam_items])
                sel_cam = next(c for c in cam_items if sel_cam_raw.startswith(c['name']))
                camera_price = sel_cam['price_uah']
            else:
                st.write("📷 Камера входить у вартість цифрового модуля")

        with col2:
            st.subheader("📊 Підсумок збірки")
            base_p = float(sel_p['base_price'])
            total = base_p + spec_price + float(sel_ctrl['price_uah']) + float(sel_video['price_uah']) + float(antenna_price) + float(camera_price)
            
            st.write(f"**База {sel_p_name}:** {base_p} грн")
            st.write(f"**Роль ({sel_role}):** {spec_price} грн")
            st.write(f"**Керування:** {sel_ctrl['price_uah']} грн")
            st.write(f"**Відео:** {sel_video['price_uah']} грн")
            if antenna_price > 0: st.write(f"**Антена:** {antenna_price} грн")
            if camera_price > 0: st.write(f"**Камера:** {camera_price} грн")
            
            st.divider()
            st.header(f"💵 Разом: {total:,.2f} грн")

except Exception as e:
    st.error(f"Помилка логіки: {e}")

if st.sidebar.button("🔄 Оновити дані"):
    st.cache_resource.clear()
    st.rerun()
