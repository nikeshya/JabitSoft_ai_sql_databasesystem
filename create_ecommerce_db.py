"""
create_ecommerce_db.py
======================
Creates a complete ecommerce SQLite database based on the provided schema.

Tables  : 12 (exact schema as specified)
Records : ~50 per table where applicable
Language: English only

Run:
    python create_ecommerce_db.py
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_FILE = "ecommerce.db"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def random_datetime(days_ago_start=365, days_ago_end=0):
    """Return a random datetime string between two day offsets from today."""
    start = datetime.now() - timedelta(days=days_ago_start)
    end   = datetime.now() - timedelta(days=days_ago_end)
    diff  = int((end - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, diff))).strftime("%Y-%m-%d %H:%M:%S")

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# =============================================================================
def create_database():

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cur  = conn.cursor()

    print("\n" + "=" * 60)
    print("   ECOMMERCE DATABASE BUILDER")
    print("=" * 60)

    # =========================================================================
    # TABLE 1: user_roles
    # =========================================================================
    print("\n[1/12] Creating table: user_roles ...")
    cur.execute("""
        CREATE TABLE user_roles (
            id          INTEGER     PRIMARY KEY AUTOINCREMENT,
            role_name   VARCHAR(50) NOT NULL,
            created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP   NULL
        )
    """)

    cur.executemany(
        "INSERT INTO user_roles (role_name, created_at, updated_at) VALUES (?, ?, ?)",
        [
            ("Admin",    "2023-01-01 00:00:00", None),
            ("Customer", "2023-01-01 00:00:00", None),
        ]
    )
    print("   Inserted: 2 roles  (Admin, Customer)")

    # =========================================================================
    # TABLE 2: users  (50 records)
    # =========================================================================
    print("\n[2/12] Creating table: users ...")
    cur.execute("""
        CREATE TABLE users (
            id           INTEGER      PRIMARY KEY AUTOINCREMENT,
            role_id      INTEGER      NOT NULL REFERENCES user_roles(id),
            full_name    VARCHAR(150) NOT NULL,
            email        VARCHAR(150) NOT NULL UNIQUE,
            password     VARCHAR(255) NOT NULL,
            phone_number VARCHAR(20),
            status       VARCHAR(20)  DEFAULT 'active'
                             CHECK(status IN ('active', 'inactive', 'block')),
            created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP    NULL
        )
    """)

    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
        "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
        "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
        "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol",
        "Amanda", "Melissa", "Deborah", "Andrew", "Joshua", "Kevin", "Brian",
        "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
        "Martin", "Thompson", "Young", "Robinson"
    ]

    statuses = ["active"] * 35 + ["inactive"] * 10 + ["block"] * 5
    random.shuffle(statuses)

    users_data = []
    for i, fname in enumerate(first_names):
        lname  = random.choice(last_names)
        role   = 1 if i == 0 else 2
        email  = f"{fname.lower()}.{lname.lower()}{i}@example.com"
        phone  = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        status = statuses[i]
        ca     = random_datetime(500, 30)
        users_data.append((role, f"{fname} {lname}", email, f"hashed_pw_{i+1:03d}", phone, status, ca, None))

    cur.executemany("""
        INSERT INTO users (role_id, full_name, email, password, phone_number, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)
    print(f"   Inserted: {len(users_data)} users")

    # =========================================================================
    # TABLE 3: categories  (20 records — 8 parent + 12 sub-categories)
    # =========================================================================
    print("\n[3/12] Creating table: categories ...")
    cur.execute("""
        CREATE TABLE categories (
            id             INTEGER      PRIMARY KEY AUTOINCREMENT,
            category_name  VARCHAR(100) NOT NULL,
            url_slug       TEXT         NOT NULL UNIQUE,
            parent_cat_id  INTEGER      NULL REFERENCES categories(id),
            status         VARCHAR(20)  DEFAULT 'active'
                               CHECK(status IN ('active', 'inactive')),
            created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP    NULL
        )
    """)

    # (name, slug, parent_cat_id, status)
    categories = [
        # Parent categories
        ("Electronics",       "electronics",        None, "active"),   # id=1
        ("Clothing",          "clothing",           None, "active"),   # id=2
        ("Books",             "books",              None, "active"),   # id=3
        ("Home and Kitchen",  "home-kitchen",       None, "active"),   # id=4
        ("Sports and Fitness","sports-fitness",     None, "active"),   # id=5
        ("Beauty and Personal","beauty-personal",   None, "active"),   # id=6
        ("Toys and Games",    "toys-games",         None, "active"),   # id=7
        ("Automotive",        "automotive",         None, "inactive"), # id=8
        # Sub-categories
        ("Mobile Phones",     "mobile-phones",      1,    "active"),   # id=9
        ("Laptops",           "laptops",            1,    "active"),   # id=10
        ("Headphones",        "headphones",         1,    "active"),   # id=11
        ("Smart Watches",     "smart-watches",      1,    "active"),   # id=12
        ("Mens Clothing",     "mens-clothing",      2,    "active"),   # id=13
        ("Womens Clothing",   "womens-clothing",    2,    "active"),   # id=14
        ("Kids Clothing",     "kids-clothing",      2,    "active"),   # id=15
        ("Fiction",           "fiction-books",      3,    "active"),   # id=16
        ("Non-Fiction",       "non-fiction-books",  3,    "active"),   # id=17
        ("Cookware",          "cookware",           4,    "active"),   # id=18
        ("Gym Equipment",     "gym-equipment",      5,    "active"),   # id=19
        ("Skincare",          "skincare",           6,    "active"),   # id=20
    ]

    cur.executemany("""
        INSERT INTO categories (category_name, url_slug, parent_cat_id, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, [(c[0], c[1], c[2], c[3], NOW) for c in categories])
    print(f"   Inserted: {len(categories)} categories  (8 parent + 12 sub-categories)")

    # =========================================================================
    # TABLE 4: products  (50 records)
    # =========================================================================
    print("\n[4/12] Creating table: products ...")
    cur.execute("""
        CREATE TABLE products (
            id             INTEGER      PRIMARY KEY AUTOINCREMENT,
            product_name   VARCHAR(200) NOT NULL,
            url_slug       VARCHAR(200) NOT NULL UNIQUE,
            category_id    INTEGER      NOT NULL REFERENCES categories(id),
            description    TEXT,
            price          REAL         NOT NULL,
            stock_quantity INTEGER      DEFAULT 0,
            status         VARCHAR(20)  DEFAULT 'active'
                               CHECK(status IN ('active', 'inactive')),
            created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP    NULL
        )
    """)

    # (product_name, url_slug, category_id, description, price, stock, status)
    products_data = [
        # Mobile Phones (cat_id = 9)
        ("Apple iPhone 15 Pro 256GB",         "apple-iphone-15-pro-256gb",           9,  "Apple iPhone 15 Pro with A17 Pro chip and titanium design",                             999.99,  80, "active"),
        ("Samsung Galaxy S24 Ultra",          "samsung-galaxy-s24-ultra",            9,  "Samsung flagship with 200MP camera and built-in S Pen",                                1199.99,  60, "active"),
        ("Google Pixel 8 Pro",                "google-pixel-8-pro",                  9,  "Google Pixel 8 Pro with Tensor G3 chip and 50MP camera system",                         799.99,  70, "active"),
        ("OnePlus 12 5G",                     "oneplus-12-5g",                       9,  "OnePlus 12 with Snapdragon 8 Gen 3 and 100W fast charging",                             699.99, 100, "active"),
        ("Motorola Edge 50 Pro",              "motorola-edge-50-pro",                9,  "Motorola Edge 50 Pro with 144Hz pOLED display and 68W charging",                        549.99,  90, "active"),
        ("Sony Xperia 1 VI",                  "sony-xperia-1-vi",                    9,  "Sony Xperia 1 VI with 4K OLED display and Zeiss optics",                               1299.99,  40, "active"),
        ("Nothing Phone 2a",                  "nothing-phone-2a",                    9,  "Nothing Phone 2a with Glyph Interface and MediaTek Dimensity 7200 Pro",                  349.99, 120, "active"),
        # Laptops (cat_id = 10)
        ("Apple MacBook Air M3 13-inch",      "apple-macbook-air-m3-13",            10,  "MacBook Air with M3 chip, 8GB RAM, 256GB SSD and 18-hour battery",                    1099.99,  40, "active"),
        ("Dell XPS 15 OLED",                  "dell-xps-15-oled",                   10,  "Dell XPS 15 with 3.5K OLED display, Intel Core i9 and RTX 4070",                      1899.99,  20, "active"),
        ("HP Spectre x360 14",                "hp-spectre-x360-14",                 10,  "HP Spectre x360 convertible laptop with Intel Core Ultra 7 and 16GB RAM",              1399.99,  35, "active"),
        ("Lenovo ThinkPad X1 Carbon",         "lenovo-thinkpad-x1-carbon",          10,  "Lenovo ThinkPad X1 Carbon Gen 12, ultra-light business laptop with 32GB RAM",          1599.99,  25, "active"),
        ("ASUS ROG Zephyrus G16",             "asus-rog-zephyrus-g16",              10,  "Gaming laptop with RTX 4080, Intel Core i9 and 240Hz OLED display",                   2499.99,  18, "active"),
        # Headphones (cat_id = 11)
        ("Sony WH-1000XM5",                   "sony-wh-1000xm5",                    11,  "Industry-leading noise cancellation with 30-hour battery life",                         379.99, 100, "active"),
        ("Bose QuietComfort Ultra",           "bose-quietcomfort-ultra",             11,  "Bose QuietComfort Ultra with Immersive Audio and CustomTune sound calibration",          429.99,  80, "active"),
        ("Apple AirPods Max",                 "apple-airpods-max",                   11,  "Apple AirPods Max with Adaptive Transparency and Personalized Spatial Audio",            549.99,  60, "active"),
        ("Jabra Evolve2 85",                  "jabra-evolve2-85",                    11,  "Jabra Evolve2 85 professional headset with hybrid ANC and 37-hour battery",             499.99,  50, "active"),
        # Smart Watches (cat_id = 12)
        ("Apple Watch Series 9 GPS 45mm",     "apple-watch-series-9-gps-45mm",      12,  "Apple Watch S9 with Double Tap gesture and on-device Siri",                             429.99,  70, "active"),
        ("Samsung Galaxy Watch 7",            "samsung-galaxy-watch-7",              12,  "Samsung Galaxy Watch 7 with BioActive sensor and AI health insights",                    299.99,  90, "active"),
        ("Garmin Fenix 7 Pro",                "garmin-fenix-7-pro",                  12,  "Garmin Fenix 7 Pro with solar charging, multiband GPS and 22-day battery",              799.99,  45, "active"),
        ("Fitbit Charge 6",                   "fitbit-charge-6",                     12,  "Fitbit Charge 6 with built-in GPS, ECG app and Google Maps support",                    159.99, 110, "active"),
        # Mens Clothing (cat_id = 13)
        ("Levis 511 Slim Fit Jeans",          "levis-511-slim-fit-jeans",           13,  "Classic slim fit jeans in stretch denim with 5-pocket styling",                           69.99, 200, "active"),
        ("Ralph Lauren Classic Polo Shirt",   "ralph-lauren-classic-polo",          13,  "100% cotton mesh polo shirt with embroidered pony logo",                                   98.99, 300, "active"),
        ("Brooks Brothers Non-Iron Shirt",    "brooks-brothers-non-iron-shirt",     13,  "Non-iron Supima cotton dress shirt in slim fit",                                          129.99, 180, "active"),
        ("Nike Dri-FIT Running T-Shirt",      "nike-dri-fit-running-tshirt",        13,  "Nike Dri-FIT moisture-wicking running t-shirt for men",                                    35.99, 400, "active"),
        ("Dockers Classic Chino Pants",       "dockers-classic-chino-pants",        13,  "Dockers Signature Khaki slim-fit chino pants in stretch fabric",                           59.99, 220, "active"),
        # Womens Clothing (cat_id = 14)
        ("Zara Floral Midi Dress",            "zara-floral-midi-dress",             14,  "Flowing floral print midi dress with V-neck and adjustable tie waist",                     79.99, 150, "active"),
        ("H&M Wrap Blouse",                   "hm-wrap-blouse",                     14,  "Satin-finish wrap blouse with long sleeves and tie detail",                                29.99, 250, "active"),
        ("Calvin Klein Blazer",               "calvin-klein-blazer",                14,  "Single-button ponte fabric blazer in a fitted silhouette",                                149.99, 100, "active"),
        ("Anthropologie Maxi Skirt",          "anthropologie-maxi-skirt",           14,  "Flowy maxi skirt with elastic waistband and side pockets",                                 89.99, 130, "active"),
        ("Adidas Womens Track Jacket",        "adidas-womens-track-jacket",         14,  "Adidas moisture-wicking track jacket with zip pockets",                                    64.99, 175, "active"),
        # Fiction Books (cat_id = 16)
        ("The Midnight Library",              "the-midnight-library",               16,  "Matt Haig — Between life and death there is a library with infinite possibilities",         14.99, 500, "active"),
        ("Tomorrow and Tomorrow and Tomorrow","tomorrow-and-tomorrow-and-tomorrow", 16,  "Gabrielle Zevin — A story of love, creativity and the video game industry",                17.99, 400, "active"),
        ("Fourth Wing",                       "fourth-wing",                        16,  "Rebecca Yarros — Fantasy dragon rider novel, number 1 New York Times bestseller",          24.99, 350, "active"),
        # Non-Fiction Books (cat_id = 17)
        ("Atomic Habits",                     "atomic-habits",                      17,  "James Clear — Build good habits and break bad ones through tiny changes",                   16.99, 600, "active"),
        ("The Psychology of Money",           "the-psychology-of-money",            17,  "Morgan Housel — Timeless lessons on wealth, greed and happiness",                          18.99, 480, "active"),
        ("Outlive The Science of Longevity",  "outlive-science-longevity",          17,  "Dr. Peter Attia — The revolutionary science of living longer and better",                  27.99, 320, "active"),
        # Cookware / Home (cat_id = 18)
        ("Le Creuset Signature Dutch Oven",   "le-creuset-signature-dutch-oven",    18,  "5.5 quart enameled cast iron Dutch oven, oven-safe to 500 degrees Fahrenheit",           399.99,  60, "active"),
        ("Instant Pot Duo 7-in-1 6Qt",        "instant-pot-duo-7in1-6qt",           18,  "7-in-1 electric pressure cooker, slow cooker, rice cooker and steamer",                    99.99, 150, "active"),
        ("All-Clad Stainless Steel Pan Set",  "allclad-stainless-pan-set",          18,  "All-Clad D3 3-piece stainless steel cookware set, oven and dishwasher safe",              599.99,  40, "active"),
        ("Vitamix 5200 Blender",              "vitamix-5200-blender",               18,  "Vitamix 5200 professional blender with variable speed and 64oz container",                 449.99,  55, "active"),
        # Gym Equipment (cat_id = 19)
        ("Bowflex SelectTech 552 Dumbbells",  "bowflex-selecttech-552",             19,  "Adjustable dumbbells replacing 15 sets of weights, range 5 to 52.5 lbs each",             429.99,  50, "active"),
        ("Peloton Yoga Mat",                  "peloton-yoga-mat",                   19,  "Extra-thick 5mm premium yoga mat with alignment lines and non-slip texture",                98.99, 300, "active"),
        ("Rogue Fitness Pull-Up Bar",         "rogue-fitness-pull-up-bar",          19,  "Rogue Monster wall-mounted pull-up bar with steel construction",                           349.99,  35, "active"),
        ("TRX All-in-One Suspension Trainer", "trx-all-in-one-suspension",          19,  "TRX All-in-One system with 300 plus exercises and door anchor included",                   199.99,  80, "active"),
        # Skincare / Beauty (cat_id = 20)
        ("The Ordinary Hyaluronic Acid 2%",   "the-ordinary-hyaluronic-acid",       20,  "Multi-depth hydration serum with Hyaluronic Acid 2% and Vitamin B5, 30ml",                  9.99, 700, "active"),
        ("CeraVe Moisturizing Cream",         "cerave-moisturizing-cream",          20,  "CeraVe 16oz moisturizing cream for normal to dry skin with essential ceramides",             19.99, 500, "active"),
        ("Paulas Choice 2% BHA Exfoliant",    "paulas-choice-2pct-bha",             20,  "Skin Perfecting 2% BHA liquid exfoliant for unclogging pores and blackheads",               34.99, 350, "active"),
        ("Tatcha The Water Cream",            "tatcha-the-water-cream",             20,  "Water-burst moisturizer with Japanese wild rose and hadasei-3 complex",                      68.99, 200, "active"),
        # Toys (cat_id = 7)
        ("LEGO Technic McLaren Formula 1",    "lego-technic-mclaren-f1",             7,  "LEGO Technic McLaren Formula 1 Race Car with 1432 pieces, officially licensed",            199.99,  80, "active"),
        ("Hasbro Monopoly Classic Edition",   "hasbro-monopoly-classic",             7,  "Hasbro Monopoly classic board game for 2 to 8 players, ages 8 and up",                      24.99, 300, "active"),
        ("Ravensburger 3000-Piece Puzzle",    "ravensburger-3000-piece-puzzle",      7,  "Ravensburger 3000-piece jigsaw puzzle with world map design, 48 x 32 inches",               39.99, 120, "active"),
    ]

    cur.executemany("""
        INSERT INTO products (product_name, url_slug, category_id, description, price, stock_quantity, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], NOW) for p in products_data])
    print(f"   Inserted: {len(products_data)} products")

    # =========================================================================
    # TABLE 5: product_variants  (~120 records)
    # =========================================================================
    print("\n[5/12] Creating table: product_variants ...")
    cur.execute("""
        CREATE TABLE product_variants (
            id             INTEGER     PRIMARY KEY AUTOINCREMENT,
            product_id     INTEGER     NOT NULL REFERENCES products(id),
            color          VARCHAR(50) NULL,
            size           VARCHAR(20) NULL,
            price          REAL        NOT NULL,
            stock_quantity INTEGER     DEFAULT 0,
            created_at     TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP   NULL
        )
    """)

    variants = []

    # Phone variants — color and storage size combinations
    phone_ids    = [1, 2, 3, 4, 5, 6, 7]
    phone_colors = ["Midnight Black", "Titanium Silver", "Deep Blue", "Space Gray", "Starlight White", "Forest Green"]

    for pid in phone_ids:
        base_price = cur.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()[0]
        for size in ["128GB", "256GB"]:
            multiplier = 1.0 if size == "128GB" else 1.18
            for color in random.sample(phone_colors, 3):
                variants.append((pid, color, size, round(base_price * multiplier, 2), random.randint(10, 60)))

    # Clothing variants — size and color combinations
    clothing_ids  = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    cloth_colors  = ["Red", "Navy Blue", "Black", "White", "Olive Green", "Charcoal Grey", "Burgundy", "Sky Blue", "Cream", "Pink"]
    cloth_sizes   = ["XS", "S", "M", "L", "XL", "XXL"]

    for pid in clothing_ids:
        base_price = cur.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()[0]
        for size in random.sample(cloth_sizes, 4):
            for color in random.sample(cloth_colors, 2):
                variants.append((pid, color, size, base_price, random.randint(5, 60)))

    # Headphone variants — color only
    for pid in [13, 14, 15, 16]:
        base_price = cur.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()[0]
        for color in ["Midnight Black", "Platinum Silver", "Navy Blue"]:
            variants.append((pid, color, None, base_price, random.randint(15, 50)))

    # Smart watch variants — color and case size
    for pid in [17, 18, 19, 20]:
        base_price = cur.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()[0]
        for size in ["41mm", "45mm"]:
            adj_price = base_price if size == "41mm" else round(base_price * 1.05, 2)
            for color in ["Midnight", "Starlight", "Product Red"]:
                variants.append((pid, color, size, adj_price, random.randint(10, 40)))

    cur.executemany("""
        INSERT INTO product_variants (product_id, color, size, price, stock_quantity, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [(v[0], v[1], v[2], v[3], v[4], NOW) for v in variants])

    total_variants = cur.execute("SELECT COUNT(*) FROM product_variants").fetchone()[0]
    print(f"   Inserted: {total_variants} product variants")

    # =========================================================================
    # TABLE 6: shipping_addresses  (50 records — one per user)
    # =========================================================================
    print("\n[6/12] Creating table: shipping_addresses ...")
    cur.execute("""
        CREATE TABLE shipping_addresses (
            id           INTEGER     PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER     NOT NULL REFERENCES users(id),
            full_address TEXT        NOT NULL,
            state        VARCHAR(100),
            city         VARCHAR(100),
            zip_code     VARCHAR(20),
            created_at   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP   NULL
        )
    """)

    us_locations = [
        ("California",    "Los Angeles",    "90001"), ("California",    "San Francisco",  "94102"),
        ("California",    "San Diego",      "92101"), ("Texas",         "Houston",        "77001"),
        ("Texas",         "Austin",         "73301"), ("Texas",         "Dallas",         "75201"),
        ("New York",      "New York City",  "10001"), ("New York",      "Buffalo",        "14201"),
        ("Florida",       "Miami",          "33101"), ("Florida",       "Orlando",        "32801"),
        ("Illinois",      "Chicago",        "60601"), ("Washington",    "Seattle",        "98101"),
        ("Massachusetts", "Boston",         "02101"), ("Arizona",       "Phoenix",        "85001"),
        ("Colorado",      "Denver",         "80201"), ("Georgia",       "Atlanta",        "30301"),
        ("Nevada",        "Las Vegas",      "89101"), ("Oregon",        "Portland",       "97201"),
        ("Pennsylvania",  "Philadelphia",   "19101"), ("Ohio",          "Columbus",       "43201"),
    ]
    street_names = ["Main St", "Oak Ave", "Maple Rd", "Cedar Ln", "Elm St",
                    "Park Blvd", "Lake Dr", "Hill Rd", "Forest Ave", "River Rd"]

    addresses = []
    for uid in range(1, 51):
        loc    = random.choice(us_locations)
        number = random.randint(100, 9999)
        street = random.choice(street_names)
        apt    = f", Apt {random.randint(1, 50)}" if random.random() > 0.6 else ""
        full   = f"{number} {street}{apt}, {loc[1]}, {loc[0]}"
        addresses.append((uid, full, loc[0], loc[1], loc[2]))

    cur.executemany("""
        INSERT INTO shipping_addresses (user_id, full_address, state, city, zip_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [(a[0], a[1], a[2], a[3], a[4], NOW) for a in addresses])
    print(f"   Inserted: {len(addresses)} shipping addresses")

    # =========================================================================
    # TABLE 7: offers  (20 records)
    # =========================================================================
    print("\n[7/12] Creating table: offers ...")
    cur.execute("""
        CREATE TABLE offers (
            id              INTEGER     PRIMARY KEY AUTOINCREMENT,
            coupon_code     VARCHAR(50) NOT NULL UNIQUE,
            discount_type   VARCHAR(20) NOT NULL CHECK(discount_type IN ('fixed', 'rate')),
            discount_value  REAL        NOT NULL,
            start_date      DATE        NOT NULL,
            end_date        DATE        NOT NULL,
            description     TEXT,
            status          VARCHAR(20) DEFAULT 'active'
                                CHECK(status IN ('active', 'inactive')),
            created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # (coupon_code, discount_type, discount_value, start_date, end_date, description, status)
    offers = [
        ("WELCOME10",   "fixed",  10.00, "2024-01-01", "2025-12-31", "Welcome offer — $10 off for new users",               "active"),
        ("SAVE10PCT",   "rate",   10.00, "2024-01-01", "2025-06-30", "10 percent off on all orders",                        "active"),
        ("FLAT25",      "fixed",  25.00, "2024-03-01", "2025-03-31", "Flat $25 off on orders above $99",                    "active"),
        ("SUMMER20",    "rate",   20.00, "2024-06-01", "2024-08-31", "Summer sale — 20 percent off storewide",              "inactive"),
        ("BLACKFRI30",  "rate",   30.00, "2024-11-28", "2024-11-30", "Black Friday — 30 percent off",                       "inactive"),
        ("MOBILE50",    "fixed",  50.00, "2024-01-01", "2025-12-31", "$50 off on mobile phones",                            "active"),
        ("FASHION15",   "rate",   15.00, "2024-01-01", "2025-09-30", "15 percent off on all clothing items",                "active"),
        ("BOOKS5",      "fixed",   5.00, "2024-01-01", "2025-12-31", "$5 off on books",                                     "active"),
        ("FIRSTORDER",  "rate",    5.00, "2024-01-01", "2025-12-31", "5 percent off on your first purchase",                "active"),
        ("FLASH40",     "rate",   40.00, "2024-12-01", "2024-12-02", "Flash sale — 40 percent off for 24 hours",            "inactive"),
        ("SPORTS10",    "rate",   10.00, "2024-01-01", "2025-06-30", "10 percent off on sports and fitness products",       "active"),
        ("BEAUTY15",    "rate",   15.00, "2024-01-01", "2025-12-31", "15 percent off on beauty products",                   "active"),
        ("LAPTOP100",   "fixed", 100.00, "2024-01-01", "2025-12-31", "$100 off on laptops",                                 "active"),
        ("SPRING15",    "rate",   15.00, "2024-03-20", "2024-06-20", "Spring refresh — 15 percent off",                     "inactive"),
        ("AUDIO25",     "fixed",  25.00, "2024-01-01", "2025-12-31", "$25 off on headphones",                               "active"),
        ("WATCH10",     "rate",   10.00, "2024-01-01", "2025-12-31", "10 percent off on smartwatches",                      "active"),
        ("HOME20",      "fixed",  20.00, "2024-01-01", "2025-12-31", "$20 off on home and kitchen products",                "active"),
        ("TOYS15",      "fixed",  15.00, "2024-01-01", "2025-12-31", "$15 off on toys and games",                           "active"),
        ("NEWYEAR12",   "rate",   12.00, "2025-01-01", "2025-01-07", "New Year — 12 percent off sitewide",                  "inactive"),
        ("VIP35",       "rate",   35.00, "2024-01-01", "2025-12-31", "VIP member exclusive — 35 percent off",               "active"),
    ]

    cur.executemany("""
        INSERT INTO offers (coupon_code, discount_type, discount_value, start_date, end_date, description, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [(o[0], o[1], o[2], o[3], o[4], o[5], o[6], NOW) for o in offers])
    print(f"   Inserted: {len(offers)} coupon offers")

    # =========================================================================
    # TABLE 8: orders  (50 records)
    # =========================================================================
    print("\n[8/12] Creating table: orders ...")
    cur.execute("""
        CREATE TABLE orders (
            id                      INTEGER      PRIMARY KEY AUTOINCREMENT,
            order_number            VARCHAR(30)  NOT NULL UNIQUE,
            user_id                 INTEGER      NOT NULL REFERENCES users(id),
            total_amount            REAL         NOT NULL,
            discount_amount         REAL         DEFAULT 0,
            gross_amount            REAL         NOT NULL,
            shipping_amount         REAL         DEFAULT 0,
            net_amount              REAL         NOT NULL,
            status                  VARCHAR(20)  DEFAULT 'placed'
                                        CHECK(status IN ('placed', 'processing', 'shipping', 'delivered', 'cancelled')),
            payment_status          VARCHAR(20)  DEFAULT 'not_paid'
                                        CHECK(payment_status IN ('paid', 'not_paid')),
            payment_type            VARCHAR(20)  DEFAULT 'cod'
                                        CHECK(payment_type IN ('netbanking', 'upi', 'cod')),
            payment_transaction_id  VARCHAR(100) NULL,
            coupon_code             VARCHAR(50)  NULL,
            created_at              TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            updated_at              TIMESTAMP    NULL
        )
    """)

    order_statuses = (["placed"] * 8 + ["processing"] * 10 + ["shipping"] * 10
                      + ["delivered"] * 18 + ["cancelled"] * 4)
    payment_types  = ["upi"] * 20 + ["netbanking"] * 18 + ["cod"] * 12
    coupon_pool    = ([None] * 30 + ["SAVE10PCT", "FLAT25", "WELCOME10", "MOBILE50",
                       "FASHION15", "BOOKS5", "SPORTS10", "AUDIO25", "WATCH10",
                       "HOME20", "FIRSTORDER", "VIP35", "LAPTOP100", "BEAUTY15",
                       "TOYS15", None, None, None, None, None])
    random.shuffle(order_statuses)
    random.shuffle(payment_types)
    random.shuffle(coupon_pool)

    customer_ids = list(range(2, 51))

    orders_data = []
    for i in range(50):
        uid      = random.choice(customer_ids)
        total    = round(random.uniform(15.00, 2500.00), 2)
        coupon   = coupon_pool[i]
        discount = round(random.uniform(5.00, min(total * 0.35, 150.00)), 2) if coupon else 0.0
        gross    = round(total - discount, 2)
        shipping = 0.00 if gross >= 50.00 else 5.99
        net      = round(gross + shipping, 2)
        status   = order_statuses[i]
        ptype    = payment_types[i]
        pstatus  = ("paid" if ptype in ("upi", "netbanking")
                    else ("paid" if status == "delivered" else "not_paid"))
        txn_id   = f"TXN{random.randint(100000000, 999999999)}" if pstatus == "paid" else None
        order_num = f"ORD-2024-{str(i + 1).zfill(5)}"
        created  = random_datetime(365, 0)

        orders_data.append((order_num, uid, total, discount, gross, shipping,
                             net, status, pstatus, ptype, txn_id, coupon, created, None))

    cur.executemany("""
        INSERT INTO orders (
            order_number, user_id, total_amount, discount_amount, gross_amount,
            shipping_amount, net_amount, status, payment_status, payment_type,
            payment_transaction_id, coupon_code, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders_data)
    print(f"   Inserted: {len(orders_data)} orders")

    # =========================================================================
    # TABLE 9: order_items  (1–4 items per order)
    # =========================================================================
    print("\n[9/12] Creating table: order_items ...")
    cur.execute("""
        CREATE TABLE order_items (
            id                  INTEGER      PRIMARY KEY AUTOINCREMENT,
            order_id            INTEGER      NOT NULL REFERENCES orders(id),
            product_id          INTEGER      NOT NULL REFERENCES products(id),
            product_variant_id  INTEGER      NULL     REFERENCES product_variants(id),
            product_name        VARCHAR(200) NOT NULL,
            color               VARCHAR(50)  NULL,
            size                VARCHAR(20)  NULL,
            price               REAL         NOT NULL,
            quantity            INTEGER      NOT NULL DEFAULT 1,
            total_amount        REAL         NOT NULL,
            created_at          TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    all_products = cur.execute("SELECT id, product_name, price FROM products").fetchall()
    all_variants = cur.execute("SELECT id, product_id, color, size, price FROM product_variants").fetchall()
    variants_by_product = {}
    for v in all_variants:
        variants_by_product.setdefault(v[1], []).append(v)

    order_items_data = []
    for order_id in range(1, 51):
        num_items = random.randint(1, 4)
        chosen    = random.sample(all_products, min(num_items, len(all_products)))
        for prod in chosen:
            pid, pname, base_price = prod
            qty    = random.randint(1, 3)
            color  = None
            size   = None
            price  = base_price
            var_id = None
            if pid in variants_by_product and variants_by_product[pid]:
                var    = random.choice(variants_by_product[pid])
                var_id = var[0]
                color  = var[2]
                size   = var[3]
                price  = var[4]
            total = round(price * qty, 2)
            order_items_data.append((order_id, pid, var_id, pname, color, size, price, qty, total, NOW))

    cur.executemany("""
        INSERT INTO order_items (
            order_id, product_id, product_variant_id, product_name,
            color, size, price, quantity, total_amount, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, order_items_data)
    print(f"   Inserted: {len(order_items_data)} order items")

    # =========================================================================
    # TABLE 10: order_shipping_addresses  (50 records — one per order)
    # =========================================================================
    print("\n[10/12] Creating table: order_shipping_addresses ...")
    cur.execute("""
        CREATE TABLE order_shipping_addresses (
            id                  INTEGER     PRIMARY KEY AUTOINCREMENT,
            order_id            INTEGER     NOT NULL REFERENCES orders(id),
            shipping_address_id INTEGER     NULL REFERENCES shipping_addresses(id),
            full_address        TEXT        NOT NULL,
            state               VARCHAR(100),
            city                VARCHAR(100),
            zip_code            VARCHAR(20),
            created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
        )
    """)

    osa_data = []
    for order_id in range(1, 51):
        uid  = cur.execute("SELECT user_id FROM orders WHERE id=?", (order_id,)).fetchone()[0]
        addr = cur.execute("""
            SELECT id, full_address, state, city, zip_code
            FROM shipping_addresses WHERE user_id=? LIMIT 1
        """, (uid,)).fetchone()
        if addr:
            osa_data.append((order_id, addr[0], addr[1], addr[2], addr[3], addr[4]))

    cur.executemany("""
        INSERT INTO order_shipping_addresses
            (order_id, shipping_address_id, full_address, state, city, zip_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [(r[0], r[1], r[2], r[3], r[4], r[5], NOW) for r in osa_data])
    print(f"   Inserted: {len(osa_data)} order shipping addresses")

    # =========================================================================
    # TABLE 11: carts  (50 records)
    # =========================================================================
    print("\n[11/12] Creating table: carts ...")
    cur.execute("""
        CREATE TABLE carts (
            id                  INTEGER     PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER     NOT NULL REFERENCES users(id),
            product_id          INTEGER     NULL REFERENCES products(id),
            product_variant_id  INTEGER     NULL REFERENCES product_variants(id),
            quantity            INTEGER     NOT NULL DEFAULT 1,
            created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            updated_at          TIMESTAMP   NULL
        )
    """)

    carts_data = []
    for _ in range(50):
        uid  = random.randint(2, 50)
        prod = random.choice(all_products)
        pid  = prod[0]
        var  = (random.choice(variants_by_product[pid])
                if pid in variants_by_product and variants_by_product[pid] else None)
        carts_data.append((uid, pid, var[0] if var else None, random.randint(1, 3)))

    cur.executemany("""
        INSERT INTO carts (user_id, product_id, product_variant_id, quantity, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, [(c[0], c[1], c[2], c[3], NOW) for c in carts_data])
    print(f"   Inserted: {len(carts_data)} cart items")

    # =========================================================================
    # TABLE 12: wishlist  (50 records)
    # =========================================================================
    print("\n[12/12] Creating table: wishlist ...")
    cur.execute("""
        CREATE TABLE wishlist (
            id                  INTEGER     PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER     NOT NULL REFERENCES users(id),
            product_id          INTEGER     NOT NULL REFERENCES products(id),
            product_variant_id  INTEGER     NULL REFERENCES product_variants(id),
            created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
        )
    """)

    wish_data = []
    wish_seen = set()
    attempts  = 0
    while len(wish_data) < 50 and attempts < 1000:
        attempts += 1
        uid = random.randint(2, 50)
        pid = random.choice(all_products)[0]
        if (uid, pid) in wish_seen:
            continue
        wish_seen.add((uid, pid))
        var_id = None
        if pid in variants_by_product and variants_by_product[pid]:
            var_id = random.choice(variants_by_product[pid])[0]
        wish_data.append((uid, pid, var_id))

    cur.executemany("""
        INSERT INTO wishlist (user_id, product_id, product_variant_id, created_at)
        VALUES (?, ?, ?, ?)
    """, [(w[0], w[1], w[2], NOW) for w in wish_data])
    print(f"   Inserted: {len(wish_data)} wishlist items")

    # =========================================================================
    # structure_description — AI knowledge layer
    # Every table and column gets a plain-English description so the AI
    # understands the schema without guessing.
    # =========================================================================
    print("\n[+]  Populating structure_description (AI knowledge layer) ...")
    cur.execute("""
        CREATE TABLE structure_description (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT    NOT NULL
        )
    """)

    descriptions = [
        # Tables
        ("user_roles",
         "Defines the two system roles: Admin (full platform access) and Customer (buyer)."),
        ("users",
         "All registered accounts. role_id determines if the user is an Admin or Customer. "
         "Status can be active, inactive, or block."),
        ("categories",
         "Product taxonomy. Supports nested sub-categories through parent_cat_id. "
         "A NULL parent_cat_id means it is a top-level category."),
        ("products",
         "Main product catalog. Each product belongs to one category. "
         "Price is in USD. Variants may override the base price."),
        ("product_variants",
         "Color and size combinations for products. Each variant carries its own price and stock count."),
        ("carts",
         "Active shopping cart items — products a user has added but not yet checked out."),
        ("shipping_addresses",
         "Saved delivery addresses linked to user accounts."),
        ("orders",
         "Customer purchase orders. Stores the full financial breakdown: "
         "total_amount minus discount_amount equals gross_amount; "
         "gross_amount plus shipping_amount equals net_amount."),
        ("order_items",
         "Individual line items within an order. Snapshots the product name, color, "
         "size and price at purchase time so the record is preserved even if the product changes later."),
        ("order_shipping_addresses",
         "Delivery address snapshot copied at the moment an order is placed, "
         "ensuring the address is preserved even if the user later edits their saved address."),
        ("wishlist",
         "Products saved by users for future purchase consideration."),
        ("offers",
         "Discount coupon codes. discount_type=fixed subtracts a flat dollar amount; "
         "discount_type=rate subtracts a percentage of the order total."),
        ("structure_description",
         "AI metadata table. Stores plain-English descriptions for every table and column "
         "so the AI can generate accurate SQL without guessing at the schema meaning."),

        # user_roles columns
        ("user_roles.id",          "Primary key."),
        ("user_roles.role_name",   "Role label: Admin or Customer."),
        ("user_roles.created_at",  "Timestamp when the role was created."),
        ("user_roles.updated_at",  "Timestamp of the last update; NULL if never updated."),

        # users columns
        ("users.id",           "Unique user identifier — primary key."),
        ("users.role_id",      "Foreign key to user_roles — 1 means Admin, 2 means Customer."),
        ("users.full_name",    "Customer full display name."),
        ("users.email",        "Login email address. Must be unique across all users."),
        ("users.password",     "SENSITIVE — bcrypt-hashed password. Never expose or query this column."),
        ("users.phone_number", "Contact phone number including country code."),
        ("users.status",       "Account state: active allows login, inactive is disabled by admin, block means the user is banned."),

        # categories columns
        ("categories.id",            "Unique category identifier — primary key."),
        ("categories.category_name", "Display name shown to customers, for example Mobile Phones."),
        ("categories.url_slug",      "URL-safe identifier, for example mobile-phones. Must be unique."),
        ("categories.parent_cat_id", "NULL for top-level categories. Contains the parent category ID for sub-categories."),
        ("categories.status",        "active means visible to shoppers; inactive means hidden from the store."),

        # products columns
        ("products.id",             "Unique product identifier — primary key."),
        ("products.product_name",   "Full display name of the product."),
        ("products.url_slug",       "SEO-friendly URL identifier, for example apple-iphone-15-pro-256gb. Must be unique."),
        ("products.category_id",    "Foreign key to the categories table."),
        ("products.description",    "Detailed product description for the product listing page."),
        ("products.price",          "Base price in USD. Individual variants may have different prices."),
        ("products.stock_quantity", "Units in stock for the base product without any variant."),
        ("products.status",         "active means listed and purchasable; inactive means hidden from the store."),

        # product_variants columns
        ("product_variants.id",             "Unique variant identifier — primary key."),
        ("product_variants.product_id",     "Foreign key to the products table."),
        ("product_variants.color",          "Color option such as Midnight Black. NULL if color does not apply."),
        ("product_variants.size",           "Size option such as 256GB or L or XL. NULL if size does not apply."),
        ("product_variants.price",          "Variant-specific price in USD. May differ from the base product price."),
        ("product_variants.stock_quantity", "Units available for this specific color and size combination."),

        # carts columns
        ("carts.user_id",            "Foreign key — which user this cart item belongs to."),
        ("carts.product_id",         "Foreign key — which product is in the cart."),
        ("carts.product_variant_id", "Foreign key — which color or size variant was selected. NULL for the base product."),
        ("carts.quantity",           "Number of units the user intends to purchase."),

        # shipping_addresses columns
        ("shipping_addresses.user_id",      "Foreign key — which user this address belongs to."),
        ("shipping_addresses.full_address", "Complete street address including unit or apartment number."),
        ("shipping_addresses.state",        "US state name."),
        ("shipping_addresses.city",         "City name."),
        ("shipping_addresses.zip_code",     "US ZIP code."),

        # orders columns
        ("orders.order_number",           "Human-readable unique order reference such as ORD-2024-00001."),
        ("orders.user_id",                "Foreign key — which customer placed this order."),
        ("orders.total_amount",           "Sum of all item prices before any discount is applied."),
        ("orders.discount_amount",        "Dollar amount deducted via a coupon or promotional offer."),
        ("orders.gross_amount",           "total_amount minus discount_amount."),
        ("orders.shipping_amount",        "Delivery charge in USD. Free (0.00) for orders at or above $50."),
        ("orders.net_amount",             "Final amount charged to the customer — gross_amount plus shipping_amount."),
        ("orders.status",                 "Order lifecycle: placed then processing then shipping then delivered, or cancelled."),
        ("orders.payment_status",         "paid means funds have been received; not_paid means payment is still pending."),
        ("orders.payment_type",           "Method used to pay: upi, netbanking, or cod (cash on delivery)."),
        ("orders.payment_transaction_id", "Bank or gateway transaction reference ID for paid orders. NULL for unpaid."),
        ("orders.coupon_code",            "Coupon applied at checkout. References the coupon_code column in the offers table."),

        # order_items columns
        ("order_items.order_id",           "Foreign key to the orders table."),
        ("order_items.product_id",         "Foreign key to the products table."),
        ("order_items.product_variant_id", "Foreign key to product_variants — the exact variant that was ordered."),
        ("order_items.product_name",       "Snapshot of the product name at order time. Preserved even if the product is renamed later."),
        ("order_items.color",              "Snapshot of the color selected at the time the order was placed."),
        ("order_items.size",               "Snapshot of the size selected at the time the order was placed."),
        ("order_items.price",              "Unit price at the time the order was placed."),
        ("order_items.quantity",           "Number of units ordered for this line item."),
        ("order_items.total_amount",       "price multiplied by quantity for this specific line item."),

        # order_shipping_addresses columns
        ("order_shipping_addresses.order_id",            "Foreign key to the orders table."),
        ("order_shipping_addresses.shipping_address_id", "Reference to the original record in shipping_addresses."),
        ("order_shipping_addresses.full_address",        "Snapshot of the full delivery address at order time."),
        ("order_shipping_addresses.state",               "State from the address snapshot."),
        ("order_shipping_addresses.city",                "City from the address snapshot."),
        ("order_shipping_addresses.zip_code",            "ZIP code from the address snapshot."),

        # wishlist columns
        ("wishlist.user_id",            "Foreign key — which user saved this product."),
        ("wishlist.product_id",         "Foreign key — which product was saved to the wishlist."),
        ("wishlist.product_variant_id", "Foreign key — specific variant saved. NULL if no variant was selected."),

        # offers columns
        ("offers.coupon_code",    "Unique alphanumeric code the customer enters at checkout, for example SAVE10PCT."),
        ("offers.discount_type",  "fixed subtracts a flat dollar amount; rate subtracts a percentage of the order total."),
        ("offers.discount_value", "The amount to deduct: 25 means $25 off when type is fixed, or 25 percent off when type is rate."),
        ("offers.start_date",     "Date from which the coupon becomes valid for use."),
        ("offers.end_date",       "Expiry date — the coupon cannot be used after this date."),
        ("offers.status",         "active means the coupon is usable; inactive means it has expired or been manually disabled."),
    ]

    cur.executemany(
        "INSERT OR REPLACE INTO structure_description (name, description) VALUES (?, ?)",
        descriptions
    )
    print(f"   Inserted: {len(descriptions)} AI descriptions")

    # =========================================================================
    # COMMIT AND PRINT FINAL SUMMARY
    # =========================================================================
    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("   DATABASE CREATED SUCCESSFULLY")
    print(f"   File : {os.path.abspath(DB_FILE)}")
    print("=" * 60)
    print(f"\n   {'Table':<40} {'Records':>7}")
    print("   " + "-" * 49)

    conn2 = sqlite3.connect(DB_FILE)
    tables = [
        "user_roles", "users", "categories", "products",
        "product_variants", "carts", "shipping_addresses", "offers",
        "orders", "order_items", "order_shipping_addresses",
        "wishlist", "structure_description",
    ]
    grand_total = 0
    for t in tables:
        count = conn2.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        grand_total += count
        print(f"   {t:<40} {count:>7}")

    print("   " + "-" * 49)
    print(f"   {'TOTAL RECORDS':<40} {grand_total:>7}")
    conn2.close()

    print("\n   Example questions to ask the AI:")
    print('   "How many active users are there?"')
    print('   "What are the top 5 best-selling products?"')
    print('   "Show total revenue from all delivered orders."')
    print('   "Which orders are currently in shipping status?"')
    print('   "List all active coupon codes with their discount values."')
    print('   "What is the average net order value?"')
    print('   "Which product appears most often in wishlists?"')
    print('   "How many orders were paid by UPI vs cash on delivery?"')
    print('   "Show all customers from California with their order count."')
    print()


# =============================================================================
if __name__ == "__main__":
    create_database()
