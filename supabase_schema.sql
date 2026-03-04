-- ============================================================================
-- Drone Configurator Database Schema (Refactored)
-- ============================================================================
-- Changes:
-- 1) Added platforms table
-- 2) Extended components with system_type + compatibility_tags
-- 3) Added role-aware platform rules via allowed_roles
-- 4) Added starter data for compatibility filtering
-- ============================================================================

-- Safe reset (development)
DROP TABLE IF EXISTS components CASCADE;
DROP TABLE IF EXISTS platforms CASCADE;

-- ============================================================================
-- TABLE: platforms
-- ============================================================================
CREATE TABLE platforms (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_price NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (base_price >= 0),
    allowed_roles TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_platforms_name ON platforms(name);
CREATE INDEX idx_platforms_allowed_roles_gin ON platforms USING GIN (allowed_roles);

-- ============================================================================
-- TABLE: components
-- ============================================================================
CREATE TABLE components (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,                      -- квадрік / літак / перехоплювач ...
    category TEXT NOT NULL,                  -- мотори / рами / АКБ / камера / ...
    system_type TEXT NOT NULL DEFAULT 'Universal', -- Analog / DJI / Walksnail / ELRS / Universal
    compatibility_tags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[], -- ['10"','13"','Малий літак']
    price_uah NUMERIC(10,2) NOT NULL CHECK (price_uah >= 0),
    stock_status BOOLEAN NOT NULL DEFAULT TRUE,
    url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_components_type ON components(type);
CREATE INDEX idx_components_category ON components(category);
CREATE INDEX idx_components_system_type ON components(system_type);
CREATE INDEX idx_components_stock_status ON components(stock_status);
CREATE INDEX idx_components_tags_gin ON components USING GIN (compatibility_tags);
CREATE INDEX idx_components_type_category ON components(type, category);

-- ============================================================================
-- Timestamp trigger
-- ============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_platforms_updated_at
BEFORE UPDATE ON platforms
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_components_updated_at
BEFORE UPDATE ON components
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================================
-- Sample data: platforms
-- ============================================================================
INSERT INTO platforms (name, base_price, allowed_roles) VALUES
('10"', 3500.00, ARRAY['Камікадзе','Бомбер','Розвідник']),
('13"', 5200.00, ARRAY['Камікадзе','Бомбер']),
('Малий літак', 7800.00, ARRAY['Розвідник','Бомбер']),
('Квадрокоптер', 4200.00, ARRAY['Камікадзе','Бомбер','Розвідник']);

-- ============================================================================
-- Sample data: components
-- ============================================================================
-- Frames
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('Рама Carbon 10', 'квадрік', 'Рами', 'Universal', ARRAY['10"','Квадрокоптер'], 2400, TRUE, 'https://store.example/frame-10'),
('Рама Carbon 13', 'квадрік', 'Рами', 'Universal', ARRAY['13"','Квадрокоптер'], 3100, TRUE, 'https://store.example/frame-13'),
('Фюзеляж Малий літак', 'літак', 'Рами', 'Universal', ARRAY['Малий літак'], 4900, TRUE, 'https://store.example/plane-small');

-- Motors
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('Motor X 3115', 'квадрік', 'Мотори', 'Universal', ARRAY['10"','13"','Квадрокоптер'], 1200, TRUE, 'https://store.example/motor-3115'),
('Motor X 4006', 'літак', 'Мотори', 'Universal', ARRAY['Малий літак'], 1450, TRUE, 'https://store.example/motor-4006');

-- Video TX / RX
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('Analog VTX 1.6W', 'квадрік', 'Відео', 'Analog', ARRAY['10"','13"','Квадрокоптер'], 1800, TRUE, 'https://store.example/vtx-analog'),
('DJI O3 Air Unit', 'квадрік', 'Відео', 'DJI', ARRAY['10"','13"','Квадрокоптер'], 9500, TRUE, 'https://store.example/dji-o3'),
('Walksnail Avatar HD', 'квадрік', 'Відео', 'Walksnail', ARRAY['10"','13"','Квадрокоптер'], 7900, TRUE, 'https://store.example/walksnail');

-- Cameras (mandatory for Analog flow)
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('Phoenix 2 Analog Camera', 'квадрік', 'Камери', 'Analog', ARRAY['10"','13"','Квадрокоптер'], 1300, TRUE, 'https://store.example/cam-analog-phoenix'),
('Ratel 2 Analog Camera', 'квадрік', 'Камери', 'Analog', ARRAY['10"','13"','Квадрокоптер'], 1600, TRUE, 'https://store.example/cam-analog-ratel');

-- Thermal
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('Тепловізор Mini Thermal', 'квадрік', 'Тепловізор', 'Universal', ARRAY['10"','13"','Квадрокоптер'], 11500, TRUE, 'https://store.example/thermal-mini');

-- Batteries (must be filtered by selected platform name tag)
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('АКБ 6S 4000mAh', 'квадрік', 'АКБ', 'Universal', ARRAY['10"','Квадрокоптер'], 2900, TRUE, 'https://store.example/batt-6s-4ah'),
('АКБ 6S 8000mAh', 'квадрік', 'АКБ', 'Universal', ARRAY['13"','Квадрокоптер'], 4200, TRUE, 'https://store.example/batt-6s-8ah'),
('АКБ Li-Ion 6S 12000mAh', 'літак', 'АКБ', 'Universal', ARRAY['Малий літак'], 5100, TRUE, 'https://store.example/batt-liion-12ah');

-- Role-dependent items
INSERT INTO components (name, type, category, system_type, compatibility_tags, price_uah, stock_status, url) VALUES
('Плата ініціації v2', 'квадрік', 'Плата ініціації', 'Universal', ARRAY['10"','13"','Квадрокоптер'], 2100, TRUE, 'https://store.example/init-board'),
('Система скиду Drop-M1', 'квадрік', 'Система скиду', 'Universal', ARRAY['10"','13"','Квадрокоптер','Малий літак'], 3400, TRUE, 'https://store.example/drop-system');

-- ============================================================================
-- RLS
-- ============================================================================
ALTER TABLE platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE components ENABLE ROW LEVEL SECURITY;

CREATE POLICY "platforms public read"
    ON platforms FOR SELECT
    USING (TRUE);

CREATE POLICY "platforms auth insert"
    ON platforms FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "platforms auth update"
    ON platforms FOR UPDATE
    USING (auth.role() = 'authenticated');

CREATE POLICY "platforms auth delete"
    ON platforms FOR DELETE
    USING (auth.role() = 'authenticated');

CREATE POLICY "components public read"
    ON components FOR SELECT
    USING (TRUE);

CREATE POLICY "components auth insert"
    ON components FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "components auth update"
    ON components FOR UPDATE
    USING (auth.role() = 'authenticated');

CREATE POLICY "components auth delete"
    ON components FOR DELETE
    USING (auth.role() = 'authenticated');

-- ============================================================================
-- Useful validation queries
-- ============================================================================
-- SELECT name, allowed_roles FROM platforms;
-- SELECT name, category, compatibility_tags FROM components WHERE category='АКБ';
-- SELECT * FROM components WHERE compatibility_tags @> ARRAY['10"'];
