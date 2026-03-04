import bcrypt
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drone Configurator",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark-mode CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* global background */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    .block-container { padding-top: 2rem; }
    /* table links */
    a { color: #58a6ff; }
    /* metric cards */
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 8px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
DRONE_TYPES = [
    "7-дюймовий камікадзе",
    "5-дюймовий FPV квадрік",
    "Фіксований літак",
    "Перехоплювач",
    "Кастомний набір",
]

CATEGORIES = ["Мотори", "Стеки (ESC+FC)", "Рами", "Акумулятори", "Камери", "Відеопередавачі", "Антени", "Інше"]

# Presets: drone type → list of category names that are typically included
PRESETS: dict[str, list[str]] = {
    "7-дюймовий камікадзе":    ["Мотори", "Стеки (ESC+FC)", "Рами", "Акумулятори", "Камери"],
    "5-дюймовий FPV квадрік":  ["Мотори", "Стеки (ESC+FC)", "Рами", "Акумулятори", "Камери", "Відеопередавачі"],
    "Фіксований літак":        ["Мотори", "Рами", "Акумулятори", "Камери"],
    "Перехоплювач":            ["Мотори", "Стеки (ESC+FC)", "Рами", "Акумулятори", "Антени"],
    "Кастомний набір":         [],
}

# ── Supabase client (cached) ──────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ── Data helpers ──────────────────────────────────────────────────────────────

def load_components() -> pd.DataFrame:
    """Fetch all components from Supabase and return as a DataFrame."""
    client = get_supabase_client()
    response = client.table("components").select("*").order("category").execute()
    if not response.data:
        return pd.DataFrame(columns=["id", "name", "type", "category", "price_uah", "stock_status", "url"])
    df = pd.DataFrame(response.data)
    df["price_uah"] = pd.to_numeric(df["price_uah"], errors="coerce").fillna(0)
    df["stock_status"] = df["stock_status"].astype(bool)
    return df


def add_component(name: str, comp_type: str, category: str, price_uah: float, stock_status: bool, url: str) -> None:
    client = get_supabase_client()
    client.table("components").insert(
        {
            "name": name,
            "type": comp_type,
            "category": category,
            "price_uah": price_uah,
            "stock_status": stock_status,
            "url": url,
        }
    ).execute()


def update_components_bulk(rows: list[dict]) -> None:
    """Upsert a list of component dicts (must include 'id')."""
    client = get_supabase_client()
    client.table("components").upsert(rows).execute()


def delete_component(component_id: int) -> None:
    client = get_supabase_client()
    client.table("components").delete().eq("id", component_id).execute()


# ── Agent stub ────────────────────────────────────────────────────────────────

def sync_prices() -> str:
    """
    Placeholder for the future price-sync agent.
    In production this will trigger a web-scraping / parsing pipeline.
    """
    return "⚠️ Price agent offline"


# ── Auth helper ───────────────────────────────────────────────────────────────

def check_admin_password(entered: str) -> bool:
    """Verify the entered password against the bcrypt hash stored in secrets."""
    stored_hash: str = st.secrets.get("ADMIN_PASSWORD_HASH", "")
    if not stored_hash:
        return False
    return bcrypt.checkpw(entered.encode(), stored_hash.encode())


# ── Sidebar ───────────────────────────────────────────────────────────────────

def sidebar() -> bool:
    """Render sidebar and return True if user is authenticated as admin."""
    with st.sidebar:
        st.title("🚁 Drone Configurator")
        st.divider()

        st.subheader("🔐 Admin Login")
        pw = st.text_input("Password", type="password", key="admin_pw")
        login_btn = st.button("Login", use_container_width=True)

        is_admin = st.session_state.get("is_admin", False)

        if login_btn:
            if check_admin_password(pw):
                st.session_state["is_admin"] = True
                is_admin = True
                st.success("Access granted ✅")
            else:
                st.error("Wrong password")

        if is_admin:
            if st.button("Logout", use_container_width=True):
                st.session_state["is_admin"] = False
                is_admin = False

        st.divider()
        st.caption("Agent status")
        if st.button("🔄 Sync prices", use_container_width=True):
            st.info(sync_prices())

    return is_admin


# ── Cart helpers ──────────────────────────────────────────────────────────────

def get_cart() -> dict[int, int]:
    """Return {component_id: quantity} dict stored in session_state."""
    return st.session_state.setdefault("cart", {})


def add_to_cart(component_id: int, qty: int = 1) -> None:
    cart = get_cart()
    cart[component_id] = cart.get(component_id, 0) + qty


def remove_from_cart(component_id: int) -> None:
    cart = get_cart()
    cart.pop(component_id, None)


def clear_cart() -> None:
    st.session_state["cart"] = {}


# ── Guest view ────────────────────────────────────────────────────────────────

def guest_view(df: pd.DataFrame) -> None:
    st.header("🛒 Конфігуратор дронів")

    col_type, col_clear = st.columns([4, 1])
    with col_type:
        drone_type = st.selectbox("Тип апарату", DRONE_TYPES, key="drone_type")
    with col_clear:
        st.write("")
        if st.button("🗑 Очистити", use_container_width=True):
            clear_cart()
            st.rerun()

    # Apply preset on drone type change — ask for confirmation before clearing
    if st.session_state.get("last_drone_type") != drone_type:
        if get_cart():
            if not st.session_state.get("confirm_type_change"):
                st.warning(
                    f"Зміна типу апарату очистить поточний кошик. "
                    f"Натисніть **Підтвердити** для переходу до «{drone_type}»."
                )
                if st.button("✅ Підтвердити зміну типу", key="confirm_type_btn"):
                    st.session_state["confirm_type_change"] = True
                    st.rerun()
                return
        st.session_state["confirm_type_change"] = False
        st.session_state["last_drone_type"] = drone_type
        clear_cart()
        preset_cats = PRESETS.get(drone_type, [])
        if preset_cats and not df.empty:
            for cat in preset_cats:
                cat_rows = df[(df["category"] == cat) & df["stock_status"]]
                if not cat_rows.empty:
                    default_row = cat_rows.iloc[0]
                    add_to_cart(int(default_row["id"]))

    st.divider()

    # ── Component browser ──
    col_browse, col_cart = st.columns([3, 2])

    with col_browse:
        st.subheader("📦 Доступні компоненти")
        filter_cat = st.multiselect("Фільтр за категорією", CATEGORIES, key="cat_filter")
        filter_stock = st.checkbox("Тільки в наявності", value=True, key="stock_filter")

        view = df.copy()
        if filter_cat:
            view = view[view["category"].isin(filter_cat)]
        if filter_stock:
            view = view[view["stock_status"]]

        if view.empty:
            st.info("Немає компонентів за вибраними фільтрами.")
        else:
            for _, row in view.iterrows():
                cid = int(row["id"])
                in_cart = cid in get_cart()
                badge = "✅" if row["stock_status"] else "❌"
                with st.expander(f"{badge} **{row['name']}** — {row['price_uah']:,.0f} грн  [{row['category']}]"):
                    if row["url"]:
                        st.markdown(f"🔗 [Купити]({row['url']})")
                    st.caption(f"Тип: {row['type']}")
                    qty_key = f"qty_{cid}"
                    qty = st.number_input("Кількість", min_value=1, max_value=99, value=1, key=qty_key)
                    if in_cart:
                        if st.button("➖ Видалити з кошика", key=f"rm_{cid}"):
                            remove_from_cart(cid)
                            st.rerun()
                    else:
                        if st.button("➕ Додати до кошика", key=f"add_{cid}"):
                            add_to_cart(cid, int(qty))
                            st.rerun()

    with col_cart:
        st.subheader("🧮 Кошик")
        cart = get_cart()
        if not cart:
            st.info("Кошик порожній.")
        else:
            cart_rows = []
            total = 0.0
            for cid, qty in cart.items():
                match = df[df["id"] == cid]
                if match.empty:
                    continue
                row = match.iloc[0]
                subtotal = row["price_uah"] * qty
                total += subtotal
                link = f"[{row['name']}]({row['url']})" if row["url"] else row["name"]
                cart_rows.append(
                    {
                        "Компонент": link,
                        "Категорія": row["category"],
                        "Ціна, грн": f"{row['price_uah']:,.0f}",
                        "К-сть": qty,
                        "Сума, грн": f"{subtotal:,.0f}",
                    }
                )

            cart_df = pd.DataFrame(cart_rows)
            st.markdown(cart_df.to_markdown(index=False), unsafe_allow_html=True)
            st.divider()
            st.metric("💰 Загальна сума", f"{total:,.0f} грн")


# ── Admin view ────────────────────────────────────────────────────────────────

def admin_view(df: pd.DataFrame) -> None:
    st.header("⚙️ Адмін-панель")

    tab_add, tab_edit, tab_delete = st.tabs(["➕ Додати", "✏️ Масове редагування", "🗑 Видалити"])

    # ── Add ──
    with tab_add:
        st.subheader("Додати новий компонент")
        with st.form("add_form"):
            name = st.text_input("Назва")
            comp_type = st.selectbox("Тип апарату", ["квадрік", "літак", "перехоплювач"])
            category = st.selectbox("Категорія", CATEGORIES)
            price_uah = st.number_input("Ціна (грн)", min_value=0.0, step=10.0)
            stock_status = st.checkbox("В наявності", value=True)
            url = st.text_input("URL магазину")
            submitted = st.form_submit_button("💾 Зберегти")

        if submitted:
            if not name.strip():
                st.error("Назва не може бути порожньою.")
            else:
                add_component(name.strip(), comp_type, category, price_uah, stock_status, url.strip())
                st.success(f"Компонент «{name}» додано!")
                st.rerun()

    # ── Bulk edit ──
    with tab_edit:
        st.subheader("Масове редагування цін")
        if df.empty:
            st.info("Немає компонентів для редагування.")
        else:
            editable_cols = ["id", "name", "type", "category", "price_uah", "stock_status", "url"]
            edit_df = df[editable_cols].copy()
            edited = st.data_editor(
                edit_df,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "name": st.column_config.TextColumn("Назва"),
                    "type": st.column_config.SelectboxColumn("Тип", options=["квадрік", "літак", "перехоплювач"]),
                    "category": st.column_config.SelectboxColumn("Категорія", options=CATEGORIES),
                    "price_uah": st.column_config.NumberColumn("Ціна (грн)", min_value=0, step=10),
                    "stock_status": st.column_config.CheckboxColumn("В наявності"),
                    "url": st.column_config.LinkColumn("URL"),
                },
                key="bulk_editor",
            )
            if st.button("💾 Зберегти зміни", key="save_bulk"):
                rows = edited.to_dict(orient="records")
                update_components_bulk(rows)
                st.success("Зміни збережено!")
                st.rerun()

    # ── Delete ──
    with tab_delete:
        st.subheader("Видалити компонент")
        if df.empty:
            st.info("Немає компонентів для видалення.")
        else:
            options = {f"{row['name']} (id={row['id']})": int(row["id"]) for _, row in df.iterrows()}
            selected_label = st.selectbox("Оберіть компонент", list(options.keys()), key="del_select")
            if st.button("🗑 Видалити", type="primary", key="del_btn"):
                delete_component(options[selected_label])
                st.success(f"Компонент «{selected_label}» видалено.")
                st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    is_admin = sidebar()

    try:
        df = load_components()
    except Exception as exc:
        st.error(f"Помилка підключення до бази даних: {exc}")
        st.stop()

    if is_admin:
        admin_view(df)
        st.divider()
        st.subheader("📋 Всі компоненти")
        st.dataframe(df, use_container_width=True)
    else:
        guest_view(df)


if __name__ == "__main__":
    main()
