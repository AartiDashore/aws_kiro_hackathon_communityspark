import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "communityspark.db")


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Create all tables and seed sample data on first run."""
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS businesses (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            description TEXT,
            story     TEXT,
            category  TEXT NOT NULL,
            address   TEXT NOT NULL,
            phone     TEXT,
            website   TEXT,
            image_url TEXT,
            is_approved INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS deals (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id              INTEGER REFERENCES businesses(id),
            title                    TEXT NOT NULL,
            description              TEXT,
            discount_percent         INTEGER,
            original_price           REAL,
            deal_price               REAL,
            expires_at               TEXT NOT NULL,
            is_active                INTEGER DEFAULT 1,
            urgency_threshold_hours  REAL DEFAULT NULL,
            created_at               TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER REFERENCES businesses(id),
            rating      INTEGER CHECK(rating BETWEEN 1 AND 5),
            comment     TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );
    """)

    # Seed sample businesses only if table is empty
    cursor = await db.execute("SELECT COUNT(*) FROM businesses")
    count = (await cursor.fetchone())[0]

    if count == 0:
        await db.executescript("""
            INSERT INTO businesses (name, description, story, category, address, phone, is_approved) VALUES
            (
                'Mama Rosa''s Kitchen',
                'Authentic Mexican home cooking made fresh daily',
                'I started this restaurant to share the recipes my grandmother taught me in Oaxaca. Every dish tells a story of our family and our heritage. I want every customer to feel like they are sitting at our family table.',
                'Food & Dining',
                '123 Mission St, San Francisco, CA',
                '(415) 555-0101',
                1
            ),
            (
                'Crown & Glory Salon',
                'Natural hair care for all textures and curl patterns',
                'After years of struggling to find a salon that truly understood my hair, I trained myself and opened a space where everyone belongs. No judgment, just beautiful hair and a community that lifts each other up.',
                'Beauty & Wellness',
                '456 Fillmore St, San Francisco, CA',
                '(415) 555-0202',
                1
            ),
            (
                'The Corner Bookshop',
                'Curated books by and about communities of color',
                'Books changed my life. I want them to change others. This shop centers voices that mainstream bookstores overlook — stories that deserve to be told and read.',
                'Arts & Culture',
                '789 Valencia St, San Francisco, CA',
                '(415) 555-0303',
                1
            ),
            (
                'Golden Thread Tailor',
                'Bespoke alterations and traditional garment making',
                'My family has been tailoring clothes for three generations. I brought that craft from Vietnam to this city, and I am proud to serve this community with the same care and precision my parents taught me.',
                'Services',
                '321 Clement St, San Francisco, CA',
                '(415) 555-0404',
                1
            ),
            (
                'Spice Route Market',
                'Imported spices, grains, and pantry goods from around the world',
                'When I moved here I could not find the ingredients that reminded me of home. So I opened a store for everyone who knows that feeling — a place where your home flavors are always in stock.',
                'Retail',
                '654 Irving St, San Francisco, CA',
                '(415) 555-0505',
                1
            );

            INSERT INTO deals (business_id, title, description, discount_percent, original_price, deal_price, expires_at, is_active) VALUES
            (1, 'Lunch Special', 'Any entree + drink + dessert combo', 25, 18.00, 13.50, datetime('now', '+6 hours'), 1),
            (2, 'New Client Discount', 'First visit wash, cut and style', 30, 85.00, 59.50, datetime('now', '+2 days'), 1),
            (3, 'Buy 2 Get 1 Free', 'Mix and match any titles in store', 33, 15.00, 10.00, datetime('now', '+1 day'), 1),
            (5, 'Weekend Flash Sale', '20% off all imported spices', 20, NULL, NULL, datetime('now', '+12 hours'), 1);

            INSERT INTO reviews (business_id, rating, comment) VALUES
            (1, 5, 'The tamales are incredible. Tastes exactly like home cooking.'),
            (1, 4, 'Amazing food, always fresh. The service is warm and welcoming.'),
            (2, 5, 'Finally a salon that knows how to handle natural hair. Will not go anywhere else.'),
            (3, 5, 'Such a wonderful selection. Found books I could not find anywhere else in the city.'),
            (4, 5, 'Perfect alterations every single time. True craftsmanship.');
        """)

    await db.commit()
    await db.close()
