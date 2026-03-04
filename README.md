# 🚁 Drone Components Configurator & Price Calculator

A Streamlit web-app for calculating the cost of drone / aircraft build components, backed by Supabase.

---

## Features

| Role  | Capabilities |
|-------|-------------|
| **Guest** | Browse components, apply preset build kits (e.g. "7-inch kamikaze"), build a custom selection, see a live-updating price total with shop links |
| **Admin** | Add new components, bulk-edit prices via an editable table, delete components |

- Dark Mode UI
- Dynamic cart with per-item quantity and running total
- `sync_prices()` stub — ready for future price-agent integration

---

## Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io/) — frontend
- [supabase-py](https://github.com/supabase-community/supabase-py) — database client
- [Pandas](https://pandas.pydata.org/) — data manipulation

---

## Supabase Table — SQL

Run this in the Supabase **SQL Editor** to create the `components` table:

```sql
create table if not exists public.components (
    id           bigserial primary key,
    name         text        not null,
    type         text        not null,   -- 'квадрік' | 'літак' | 'перехоплювач'
    category     text        not null,   -- 'Мотори' | 'Стеки (ESC+FC)' | 'Рами' | ...
    price_uah    numeric     not null default 0,
    stock_status boolean     not null default true,
    url          text
);

-- Enable Row Level Security (recommended)
alter table public.components enable row level security;

-- Allow public read access for guests
create policy "Public read"
    on public.components for select
    using (true);

-- Allow full access for the service-role key used by the admin
create policy "Service role full access"
    on public.components for all
    using (true)
    with check (true);
```

> **Tip:** Seed the table with some sample components so the app has data to display right away.

---

## Local Setup

```bash
# 1. Clone & enter the repo
git clone https://github.com/VoMashtaler/pricesss.git
cd pricesss

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets (see next section)

# 5. Run the app
streamlit run app.py
```

---

## Configuring Secrets (API Keys)

Streamlit reads secrets from `.streamlit/secrets.toml` (never commit this file — it's in `.gitignore`).

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://<your-project-ref>.supabase.co"
SUPABASE_KEY = "<your-anon-or-service-role-key>"

# Generate with:
#   python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"
ADMIN_PASSWORD_HASH = "<bcrypt-hash>"
```

### Streamlit Cloud deployment

In your app's **Settings → Secrets**, paste the same key-value pairs (no need for the `[...]` section headers).

---

## Architecture Note — Future Agent Integration

`sync_prices()` in `app.py` currently returns `"⚠️ Price agent offline"`.
When a scraping/parsing agent is ready, replace the function body with a call to that agent's API or subprocess — no other code changes are required.
