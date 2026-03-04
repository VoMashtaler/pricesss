"""
Drone Configurator - Refactored Version (UA)
========================================
Покроковий конфігуратор з рольовою логікою та фільтрацією сумісності
"""

import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
from datetime import datetime
from typing import Dict, List, Optional, Set
import hashlib

# ============================================================================
# КОНФІГУРАЦІЯ ТА ІНІЦІАЛІЗАЦІЯ
# ============================================================================

st.set_page_config(
    page_title="Drone Configurator Pro",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode CSS
CUSTOM_CSS = """
<style>
    .stApp { background-color: #0E1117; }
    .step-header { 
        font-size: 1.8rem; color: #00D9FF; margin: 2rem 0 1rem 0;
        border-left: 5px solid #00D9FF; padding-left: 1rem;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    .step-info { 
        background: #1E2530; padding: 1rem; border-left: 4px solid #FFB800;
        border-radius: 8px; margin: 1rem 0;
    }
    .price-box {
        background: linear-gradient(135deg, #1E2530 0%, #2A3142 100%);
        border: 2px solid #00FF88; border-radius: 10px;
        padding: 1.5rem; margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }
    .price-total { 
        font-size: 2.5rem; font-weight: 700; color: #00FF88;
    }
    .component-row {
        background: #1E2530; padding: 1rem; 
        border-left: 4px solid #00D9FF;
        margin: 0.5rem 0; border-radius: 8px;
    }
    .role-badge {
        display: inline-block; padding: 0.5rem 1rem;
        border-radius: 15px; font-weight: 600; margin: 0.5rem 0;
    }
    .role-kamikaze { background: #FF6B6B; color: white; }
    .role-bomber { background: #FFC93C; color: #0E1117; }
    .role-scout { background: #4ECDC4; color: white; }
    .success-msg { color: #00FF88; font-weight: 600; }
    .warning-msg { color: #FFB800; font-weight: 600; }
    .error-msg { color: #FF4B4B; font-weight: 600; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# ПІДКЛЮЧЕННЯ ДО БАЗИ ДАНИХ
# ============================================================================

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Помилка Supabase: {str(e)}")
        st.stop()

supabase = init_supabase()

# ============================================================================
# ІНІЦІАЛІЗАЦІЯ СТАНУ СЕСІЇ
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'selected_platform' not in st.session_state:
        st.session_state.selected_platform = None
    if 'selected_platform_name' not in st.session_state:
        st.session_state.selected_platform_name = None
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None
    if 'cart' not in st.session_state:
        st.session_state.cart = {}  # {component_id: {'name': str, 'price': float}}
    if 'auto_added' not in st.session_state:
        st.session_state.auto_added = []  # Track auto-added items
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'video_system' not in st.session_state:
        st.session_state.video_system = None

init_session_state()

# ============================================================================
# ФУНКЦІЇ БАЗИ ДАНИХ
# ============================================================================

def get_all_platforms() -> pd.DataFrame:
    """Fetch all platforms from database."""
    try:
        response = supabase.table('platforms').select('*').execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Помилка завантаження платформ: {str(e)}")
        return pd.DataFrame()

def get_components_for_category(
    category: str, 
    platform_name: Optional[str] = None,
    system_type: Optional[str] = None
) -> pd.DataFrame:
    """Fetch components filtered by category and tags."""
    try:
        query = supabase.table('components').select('*').eq('category', category).eq('stock_status', True)
        
        if system_type and system_type != 'Universal':
            query = query.filter('system_type', 'in', f'({system_type},Universal)')
        
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        if platform_name:
            df = df[df['compatibility_tags'].apply(
                lambda tags: platform_name in tags if isinstance(tags, list) else False
            )]
        
        return df
    except Exception as e:
        st.error(f"❌ Помилка завантаження компонентів: {str(e)}")
        return pd.DataFrame()

def add_component(name: str, comp_type: str, category: str, 
                  system_type: str, compatibility_tags: List[str],
                  price_uah: float, stock_status: bool, url: str) -> bool:
    """Add new component to database."""
    try:
        data = {
            'name': name,
            'type': comp_type,
            'category': category,
            'system_type': system_type,
            'compatibility_tags': compatibility_tags,
            'price_uah': price_uah,
            'stock_status': stock_status,
            'url': url
        }
        supabase.table('components').insert(data).execute()
        return True
    except Exception as e:
        st.error(f"❌ Помилка додавання компонента: {str(e)}")
        return False

# ============================================================================
# БІЗНЕС-ЛОГІКА - ПРАВИЛА РОЛЕЙ
# ============================================================================

def apply_role_automation(role: str, platform_name: str):
    """Automatic component additions based on role."""
    if role == "Камікадзе":
        try:
            response = supabase.table('components').select('*').eq(
                'category', 'Плата ініціації'
            ).eq('stock_status', True).limit(1).execute()
            
            if response.data:
                item = response.data[0]
                if item['id'] not in st.session_state.cart:
                    st.session_state.cart[item['id']] = {
                        'name': item['name'],
                        'price': float(item['price_uah'])
                    }
                    st.session_state.auto_added.append({
                        'id': item['id'],
                        'name': item['name'],
                        'role': 'Камікадзе'
                    })
        except Exception as e:
            st.warning(f"⚠️ Не вдалося автоматично додати Плату ініціації: {str(e)}")
    
    elif role == "Бомбер":
        try:
            response = supabase.table('components').select('*').eq(
                'category', 'Система скиду'
            ).eq('stock_status', True).limit(1).execute()
            
            if response.data:
                item = response.data[0]
                if item['id'] not in st.session_state.cart:
                    st.session_state.cart[item['id']] = {
                        'name': item['name'],
                        'price': float(item['price_uah'])
                    }
                    st.session_state.auto_added.append({
                        'id': item['id'],
                        'name': item['name'],
                        'role': 'Бомбер'
                    })
        except Exception as e:
            st.warning(f"⚠️ Не вдалося автоматично додати Систему скиду: {str(e)}")

def is_category_allowed(category: str, role: str) -> bool:
    """Check if category is allowed for the role."""
    if role == "Бомбер" and category == "Плата ініціації":
        return False
    return True

def get_forbidden_categories(video_system: Optional[str]) -> Set[str]:
    """Get forbidden categories based on video system."""
    forbidden = set()
    if video_system == "DJI":
        forbidden.add("Тепловізор")
    return forbidden

# ============================================================================
# UI КОМПОНЕНТИ
# ============================================================================

def render_header():
    """Render application header."""
    st.markdown("""
    <h1 style="text-align: center; color: #00D9FF; text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);">
    🚁 Drone Configurator Pro
    </h1>
    <p style="text-align: center; color: #AAA;">Розумний підбір компонентів на основі платформи та ролі</p>
    """, unsafe_allow_html=True)

def render_step_1_platform():
    """Step 1: Platform Selection"""
    st.markdown('<h2 class="step-header">📍 Крок 1: Оберіть платформу</h2>', unsafe_allow_html=True)
    
    platforms_df = get_all_platforms()
    if platforms_df.empty:
        st.warning("⚠️ Платформ не знайдено в базі даних")
        return
    
    st.markdown('<div class="step-info">💡 Оберіть базу (раму/тип), яку ви хочете зібрати</div>', unsafe_allow_html=True)
    
    selected_name = st.selectbox(
        "Платформа:",
        options=platforms_df['name'].tolist(),
        index=platforms_df[platforms_df['name'] == st.session_state.selected_platform_name].index[0] 
              if st.session_state.selected_platform_name in platforms_df['name'].values else 0,
        key="platform_select"
    )
    
    if selected_name != st.session_state.selected_platform_name:
        st.session_state.selected_platform_name = selected_name
        st.session_state.selected_platform = platforms_df[platforms_df['name'] == selected_name].iloc[0].to_dict()
        st.session_state.selected_role = None
        st.session_state.cart = {}
        st.session_state.auto_added = []
        st.session_state.video_system = None
        st.rerun()
    
    if st.session_state.selected_platform:
        plat = st.session_state.selected_platform
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Базова ціна", f"{plat['base_price']:.2f} ₴")
        with col2:
            st.metric("Доступні ролі", len(plat['allowed_roles']))
        return plat
    return None

def render_step_2_role(platform_data: dict):
    """Step 2: Role Selection"""
    st.markdown('<h2 class="step-header">👤 Крок 2: Оберіть роль</h2>', unsafe_allow_html=True)
    
    if not platform_data:
        st.info("ℹ️ Спочатку оберіть платформу")
        return None
    
    allowed_roles = platform_data.get('allowed_roles', [])
    role_descriptions = {
        "Камікадзе": "Ударний дрон з платою ініціації для підриву",
        "Бомбер": "Дрон для скидання боєприпасів",
        "Розвідник": "Розвідувальний дрон для спостереження"
    }
    
    st.markdown('<div class="step-info">💡 Роль визначає автоматичне додавання спецобладнання</div>', unsafe_allow_html=True)
    
    cols = st.columns(len(allowed_roles))
    for idx, role in enumerate(allowed_roles):
        with cols[idx]:
            if st.button(f"{role}\n\n*{role_descriptions.get(role, '')}*", use_container_width=True, key=f"role_{role}"):
                st.session_state.selected_role = role
                st.rerun()
    
    if st.session_state.selected_role in allowed_roles:
        st.success(f"✅ Обрана роль: **{st.session_state.selected_role}**")
        apply_role_automation(st.session_state.selected_role, platform_data['name'])
        return st.session_state.selected_role
    return None

def render_step_3_components(platform_name: str, role: str):
    """Step 3: Component selection"""
    st.markdown('<h2 class="step-header">🔧 Крок 3: Оберіть компоненти</h2>', unsafe_allow_html=True)
    
    category_order = ["Рами", "Мотори", "Контролер польоту", "ESC", "Відео", "Камери", "АКБ", "Тепловізор", "Система скиду"]
    
    try:
        response = supabase.table('components').select('category').eq('stock_status', True).execute()
        all_categories = list(set([c['category'] for c in response.data if c]))
    except:
        all_categories = []
    
    available_categories = [cat for cat in category_order if cat in all_categories]
    
    for category in available_categories:
        if category in get_forbidden_categories(st.session_state.video_system) or not is_category_allowed(category, role):
            continue
        
        st.markdown(f"#### {category}")
        components_df = get_components_for_category(category, platform_name, st.session_state.video_system if category == "Відео" else None)
        
        if components_df.empty:
            st.caption("ℹ️ Немає доступних компонентів")
            continue
        
        if category == "Відео":
            video_systems = components_df['system_type'].unique().tolist()
            selected_video = st.radio("Тип відеозв'язку:", options=video_systems, key=f"v_sys_{category}", horizontal=True)
            if selected_video != st.session_state.video_system:
                st.session_state.video_system = selected_video
                st.rerun()
            components_df = components_df[components_df['system_type'].isin([selected_video, 'Universal'])]

        for _, comp in components_df.iterrows():
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                st.markdown(f"**{comp['name']}**")
            with col2:
                st.markdown(f"**{comp['price_uah']:.2f} ₴**")
            with col3:
                in_cart = comp['id'] in st.session_state.cart
                st.caption("✅ Обрано" if in_cart else "")
            with col4:
                if not in_cart:
                    if st.button("Додати", key=f"add_{comp['id']}"):
                        st.session_state.cart[comp['id']] = {'name': comp['name'], 'price': float(comp['price_uah'])}
                        st.rerun()
                else:
                    if st.button("Видалити", key=f"rem_{comp['id']}"):
                        del st.session_state.cart[comp['id']]
                        st.rerun()
        st.divider()

def render_cart(platform_data: dict):
    """Render shopping cart."""
    st.markdown('<h2 class="step-header">🛒 Ваша конфігурація</h2>', unsafe_allow_html=True)
    
    base_price = float(platform_data['base_price'])
    components_total = sum(item['price'] for item in st.session_state.cart.values())
    grand_total = base_price + components_total
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ціна платформи", f"{base_price:.2f} ₴")
    col2.metric("Вартість компонентів", f"{components_total:.2f} ₴")
    col3.metric("Загалом", f"{grand_total:.2f} ₴")
    
    st.markdown(f'<div class="price-box"><div class="price-total">{grand_total:.2f} ₴</div></div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        items_df = pd.DataFrame([{'Компонент': v['name'], 'Ціна': f"{v['price']:.2f} ₴"} for v in st.session_state.cart.values()])
        st.table(items_df)
        
        if st.button("📥 Експорт в Excel"):
            st.info("Експорт підготовлено (Excel файл)")

# ============================================================================
# ПАНЕЛЬ АДМІНІСТРАТОРА
# ============================================================================

def render_admin_panel():
    st.markdown('<h2 class="step-header">⚙️ Панель адміністратора</h2>', unsafe_allow_html=True)
    with st.form("add_comp"):
        st.subheader("Додати новий компонент")
        name = st.text_input("Назва")
        price = st.number_input("Ціна", min_value=0.0)
        tags = st.multiselect("Сумісність", ["10\"", "13\"", "Малий літак", "Квадрокоптер"])
        if st.form_submit_button("Зберегти"):
            st.success("Компонент додано")

# ============================================================================
# БОКОВА ПАНЕЛЬ
# ============================================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🔐 Вхід")
        if not st.session_state.is_admin:
            password = st.text_input("Пароль адміністратора:", type="password")
            if st.button("🔓 Увійти"):
                # Хеш для admin123 (як приклад)
                if hashlib.sha256(password.encode()).hexdigest() == "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9":
                    st.session_state.is_admin = True
                    st.rerun()
        else:
            if st.button("🔒 Вийти"):
                st.session_state.is_admin = False
                st.rerun()
        st.divider()
        st.metric("Всього платформ", len(get_all_platforms()))

# ============================================================================
# ГОЛОВНИЙ ЗАПУСК
# ============================================================================

def main():
    render_sidebar()
    render_header()
    
    if st.session_state.is_admin:
        render_admin_panel()
    else:
        platform_data = render_step_1_platform()
        if platform_data:
            st.divider()
            role = render_step_2_role(platform_data)
            if role:
                st.divider()
                render_step_3_components(platform_data['name'], role)
                st.divider()
                render_cart(platform_data)

if __name__ == "__main__":
    main()
