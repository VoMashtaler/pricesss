"""
Drone Configurator - Refactored Version
========================================
Step-by-step configurator with role-based logic and compatibility filtering

Architecture:
1. Platform selection (from platforms table)
2. Role selection (depends on platform.allowed_roles)
3. Component selection (filtered by compatibility_tags and role rules)
4. Automatic additions/restrictions based on role
5. Dynamic pricing (platform.base_price + selected components)
"""

import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
from datetime import datetime
from typing import Dict, List, Optional, Set
import hashlib

# ============================================================================
# CONFIGURATION & INITIALIZATION
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
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Ошибка Supabase: {str(e)}")
        st.stop()

supabase = init_supabase()

# ============================================================================
# SESSION STATE INITIALIZATION
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
# DATABASE FUNCTIONS
# ============================================================================

def get_all_platforms() -> pd.DataFrame:
    """Fetch all platforms from database."""
    try:
        response = supabase.table('platforms').select('*').execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Ошибка загрузки платформ: {str(e)}")
        return pd.DataFrame()

def get_components_for_category(
    category: str, 
    platform_name: Optional[str] = None,
    system_type: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch components filtered by:
    - category
    - compatibility_tags (must contain platform_name if provided)
    - system_type (if provided)
    """
    try:
        query = supabase.table('components').select('*').eq('category', category).eq('stock_status', True)
        
        if system_type and system_type != 'Universal':
            query = query.filter('system_type', 'in', f'({system_type},Universal)')
        
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Filter by platform compatibility tags if platform_name provided
        if platform_name:
            df = df[df['compatibility_tags'].apply(
                lambda tags: platform_name in tags if isinstance(tags, list) else False
            )]
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки компонентов: {str(e)}")
        return pd.DataFrame()

def get_component_by_id(component_id: int):
    """Fetch single component by ID."""
    try:
        response = supabase.table('components').select('*').eq('id', component_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"❌ Ошибка: {str(e)}")
        return None

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
        st.error(f"❌ Ошибка добавления компонента: {str(e)}")
        return False

# ============================================================================
# BUSINESS LOGIC - ROLE-BASED RULES
# ============================================================================

def apply_role_automation(role: str, platform_name: str):
    """
    Apply automatic component additions/restrictions based on role.
    
    Rules:
    - Камікадзе: Add "Плата ініціації" automatically
    - Бомбер: Add "Система скиду" automatically, hide "Плата ініціації"
    - Розвідник: No special rules
    """
    if role == "Камікадзе":
        # Find and add "Плата ініціації"
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
            st.warning(f"⚠️ Не удалось добавить Плату ініціації: {str(e)}")
    
    elif role == "Бомбер":
        # Find and add "Система скиду"
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
            st.warning(f"⚠️ Не удалось добавить Систему скиду: {str(e)}")

def is_category_allowed(category: str, role: str) -> bool:
    """
    Check if category should be shown based on role.
    
    Restrictions:
    - Бомбер: Hide "Плата ініціації"
    """
    if role == "Бомбер" and category == "Плата ініціації":
        return False
    return True

def get_forbidden_categories(video_system: Optional[str]) -> Set[str]:
    """
    Get categories that should be hidden based on video system choice.
    
    Rules:
    - DJI: Hide "Тепловізор" category
    """
    forbidden = set()
    
    if video_system == "DJI":
        forbidden.add("Тепловізор")
    
    return forbidden

def is_camera_required(video_system: Optional[str]) -> bool:
    """Check if camera selection is mandatory based on video system."""
    return video_system == "Analog"

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render application header."""
    st.markdown("""
    <h1 style="text-align: center; color: #00D9FF; text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);">
    🚁 Drone Configurator Pro
    </h1>
    <p style="text-align: center; color: #AAA;">Умный выбор компонентов на основе платформы и роли</p>
    """, unsafe_allow_html=True)

def render_step_1_platform():
    """Step 1: Platform Selection"""
    st.markdown('<h2 class="step-header">📍 Шаг 1: Выберите платформу</h2>', 
                unsafe_allow_html=True)
    
    platforms_df = get_all_platforms()
    
    if platforms_df.empty:
        st.warning("⚠️ Платформ не найдено в базе данных")
        return
    
    st.markdown(
        '<div class="step-info">💡 Выберите платформу, которую вы хотите собрать</div>',
        unsafe_allow_html=True
    )
    
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
            st.metric("Базовая цена", f"{plat['base_price']:.2f} ₴")
        with col2:
            st.metric("Доступные роли", len(plat['allowed_roles']))
        
        return plat
    
    return None

def render_step_2_role(platform_data: dict):
    """Step 2: Role Selection (depends on platform.allowed_roles)"""
    st.markdown('<h2 class="step-header">👤 Шаг 2: Выберите роль</h2>', 
                unsafe_allow_html=True)
    
    if not platform_data:
        st.info("ℹ️ Сначала выберите платформу")
        return None
    
    allowed_roles = platform_data.get('allowed_roles', [])
    
    if not allowed_roles:
        st.warning("⚠️ Для этой платформы нет доступных ролей")
        return None
    
    role_descriptions = {
        "Камікадзе": "Атакующий дрон с плата инициации для подрыва",
        "Бомбер": "Дрон для сброса грузов с система скиду",
        "Розвідник": "Разведывательный дрон для видеонаблюдения"
    }
    
    st.markdown(
        '<div class="step-info">💡 Выберите роль дрона для автоматического добавления необходимых компонентов</div>',
        unsafe_allow_html=True
    )
    
    cols = st.columns(len(allowed_roles))
    
    for idx, role in enumerate(allowed_roles):
        with cols[idx]:
            role_class = f"role-{role.lower().replace(' ', '-')}"
            badge_class = {
                "Камікадзе": "role-kamikaze",
                "Бомбер": "role-bomber", 
                "Розвідник": "role-scout"
            }.get(role, "")
            
            # Button-like radio selection
            if st.button(f"{role}\n\n*{role_descriptions.get(role, '')}*", 
                        use_container_width=True, key=f"role_{role}"):
                st.session_state.selected_role = role
                st.rerun()
    
    if st.session_state.selected_role in allowed_roles:
        st.success(f"✅ Выбрана роль: **{st.session_state.selected_role}**")
        
        # Apply role automation
        apply_role_automation(st.session_state.selected_role, platform_data['name'])
        
        return st.session_state.selected_role
    
    return None

def render_step_3_components(platform_name: str, role: str):
    """Step 3 & 4: Progressive component selection with filtering"""
    
    st.markdown('<h2 class="step-header">🔧 Шаг 3: Выберите компоненты</h2>', 
                unsafe_allow_html=True)
    
    st.markdown(
        '<div class="step-info">💡 Компоненты автоматически фильтруются по совместимости с выбранной платформой</div>',
        unsafe_allow_html=True
    )
    
    # Category order
    category_order = [
        "Рами", "Мотори", "Рама Elrs", "Контролер польоту",
        "Відео", "Камери", "АКБ", "Тепловізор",
        "Система скиду"
    ]
    
    # Get all available categories for this platform
    try:
        response = supabase.table('components').select('category').eq('stock_status', True).execute()
        all_categories = list(set([c['category'] for c in response.data if c]))
    except:
        all_categories = []
    
    # Filter categories by order and filters
    available_categories = [cat for cat in category_order if cat in all_categories]
    
    for category in available_categories:
        # Check if category is hidden
        forbidden = get_forbidden_categories(st.session_state.video_system)
        if category in forbidden:
            continue
        
        # Check role restrictions
        if not is_category_allowed(category, role):
            continue
        
        st.markdown(f"#### {category}")
        
        # Get filtered components
        components_df = get_components_for_category(
            category=category,
            platform_name=platform_name,
            system_type=st.session_state.video_system if category == "Відео" else None
        )
        
        if components_df.empty:
            st.caption("ℹ️ Нет компонентов этой категории")
            continue
        
        # For Відео category, show system_type selector
        if category == "Відео":
            st.markdown("**Выберите систему передачи видео:**")
            
            video_systems = components_df['system_type'].unique().tolist()
            selected_video = st.radio(
                "Система видео:",
                options=video_systems,
                key=f"video_system_{category}",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            if selected_video != st.session_state.video_system:
                st.session_state.video_system = selected_video
                st.rerun()
            
            # Re-filter based on selected system_type
            components_df = components_df[
                (components_df['system_type'] == selected_video) |
                (components_df['system_type'] == 'Universal')
            ]
        
        # Display components
        for _, comp in components_df.iterrows():
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{comp['name']}**")
                if comp['url']:
                    st.caption(f"[🔗 Магазин]({comp['url']})")
            
            with col2:
                st.markdown(f"**{comp['price_uah']:.2f} ₴**")
            
            with col3:
                current_qty = 1 if comp['id'] in st.session_state.cart else 0
                qty = st.number_input(
                    "К-во",
                    min_value=0,
                    max_value=5,
                    value=current_qty,
                    step=1,
                    key=f"qty_{comp['id']}",
                    label_visibility="collapsed"
                )
            
            with col4:
                if qty > 0 and comp['id'] not in st.session_state.cart:
                    if st.button("➕", key=f"add_{comp['id']}", use_container_width=True):
                        st.session_state.cart[comp['id']] = {
                            'name': comp['name'],
                            'price': float(comp['price_uah'])
                        }
                        st.rerun()
                elif qty == 0 and comp['id'] in st.session_state.cart:
                    if st.button("🗑️", key=f"remove_{comp['id']}", use_container_width=True):
                        del st.session_state.cart[comp['id']]
                        st.rerun()
                elif qty > 0:
                    st.caption(f"✅ В заказе")
        
        st.divider()

def render_cart(platform_data: dict):
    """Render shopping cart with platform base price."""
    
    st.markdown('<h2 class="step-header">🛒 Ваш заказ</h2>', 
                unsafe_allow_html=True)
    
    if not platform_data:
        st.info("ℹ️ Выберите платформу для начала")
        return
    
    base_price = float(platform_data['base_price'])
    components_total = sum(item['price'] for item in st.session_state.cart.values())
    grand_total = base_price + components_total
    
    st.markdown("### Разбор цены")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Стартовая цена (платформа)", f"{base_price:.2f} ₴")
    
    with col2:
        st.metric("Компоненты", f"{components_total:.2f} ₴")
    
    with col3:
        st.metric("Итого", f"{grand_total:.2f} ₴")
    
    st.markdown(f'<div class="price-box"><div class="price-total">{grand_total:.2f} ₴</div></div>',
                unsafe_allow_html=True)
    
    if st.session_state.cart:
        st.markdown("### Состав заказа")
        
        order_items = []
        for comp_id, item in st.session_state.cart.items():
            order_items.append({
                'Компонент': item['name'],
                'Цена': f"{item['price']:.2f} ₴"
            })
        
        order_df = pd.DataFrame(order_items)
        st.dataframe(order_df, use_container_width=True, hide_index=True)
        
        if st.session_state.auto_added:
            st.markdown("#### ✨ Автоматически добавлены:")
            for auto_item in st.session_state.auto_added:
                st.caption(f"• {auto_item['name']} (роль: {auto_item['role']})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Очистить заказ", use_container_width=True):
                st.session_state.cart = {}
                st.session_state.auto_added = []
                st.rerun()
        
        with col2:
            if st.button("📥 Экспорт в Excel", use_container_width=True):
                from io import BytesIO
                
                export_items = order_df.copy()
                export_items['Тип'] = 'Компонент'
                
                # Add summary row
                summary_row = pd.DataFrame({
                    'Компонент': ['ИТОГО'],
                    'Цена': [f"{grand_total:.2f} ₴"],
                    'Тип': ['Итог']
                })
                
                export_items = pd.concat([export_items, summary_row], ignore_index=True)
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    export_items.to_excel(writer, index=False, sheet_name='Заказ')
                
                st.download_button(
                    label="📥 Скачать Excel",
                    data=output.getvalue(),
                    file_name=f"drone_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    else:
        st.info("🛒 Заказ пуст. Добавьте компоненты для расчета стоимости")

# ============================================================================
# ADMIN PANEL
# ============================================================================

def render_admin_panel():
    """Admin panel for managing components."""
    
    st.markdown('<h2 class="step-header">⚙️ Панель администратора</h2>', 
                unsafe_allow_html=True)
    
    tabs = st.tabs(["➕ Добавить компонент", "📝 Редактировать", "🗑️ Удалить"])
    
    with tabs[0]:
        st.markdown("### Новый компонент")
        
        with st.form("add_component_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Название*")
                comp_type = st.selectbox("Тип*", ["квадрік", "літак", "перехоплювач"])
                category = st.text_input("Категория*")
                system_type = st.selectbox(
                    "Система*",
                    ["Universal", "Analog", "DJI", "Walksnail", "ELRS"]
                )
            
            with col2:
                price_uah = st.number_input("Цена (UAH)*", min_value=0.0, step=0.01)
                stock_status = st.checkbox("В наличии", value=True)
                url = st.text_input("URL")
            
            compatibility_tags = st.multiselect(
                "Тег совместимости*",
                ["10\"", "13\"", "Малий літак", "Квадрокоптер", "Universal"]
            )
            
            submitted = st.form_submit_button("💾 Добавить", use_container_width=True)
            
            if submitted:
                if name and category and compatibility_tags:
                    if add_component(name, comp_type, category, system_type,
                                    compatibility_tags, price_uah, stock_status, url):
                        st.success("✅ Компонент добавлен!")
                        st.rerun()
                else:
                    st.error("❌ Заполните обязательные поля")

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar with auth and info."""
    
    with st.sidebar:
        st.markdown("## 🔐 Авторизация")
        
        if not st.session_state.is_admin:
            password = st.text_input("Пароль администратора:", type="password")
            
            if st.button("🔓 Войти", use_container_width=True):
                stored_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
                if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
                    st.session_state.is_admin = True
                    st.success("✅ Авторизовано!")
                    st.rerun()
                else:
                    st.error("❌ Неверный пароль")
        else:
            st.success("👑 Администратор")
            if st.button("🔒 Выход", use_container_width=True):
                st.session_state.is_admin = False
                st.rerun()
        
        st.divider()
        
        st.markdown("## 📊 Статистика")
        platforms_df = get_all_platforms()
        st.metric("Платформ", len(platforms_df))

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    render_sidebar()
    render_header()
    
    if st.session_state.is_admin:
        render_admin_panel()
    else:
        # Step-by-step configurator flow
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
