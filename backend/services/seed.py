"""Seed mock business data (Instagram/Facebook-first businesses)."""
from datetime import datetime, timezone

_COVERS = [
    "https://images.pexels.com/photos/29854540/pexels-photo-29854540.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "https://images.pexels.com/photos/19193275/pexels-photo-19193275.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "https://images.pexels.com/photos/2079450/pexels-photo-2079450.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "https://images.pexels.com/photos/1855214/pexels-photo-1855214.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "https://images.pexels.com/photos/1058277/pexels-photo-1058277.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "https://images.pexels.com/photos/3184405/pexels-photo-3184405.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
]


def _cover(i: int) -> str:
    return _COVERS[i % len(_COVERS)]


BUSINESSES = [
    # Restaurants / Cafes
    {"name": "Saffron & Smoke", "category": "Restaurant", "city": "Mumbai", "country": "India",
     "bio": "Modern Indian small plates. Reservations via DM.", "followers": 24800, "engagement_rate": 3.8,
     "posts_last_30": 22, "instagram": "saffronandsmoke", "facebook": "saffronandsmoke",
     "website": None, "phone": "+91 98200 12345", "has_online_orders": False, "verified": True},
    {"name": "Grain & Grind Coffee", "category": "Cafe", "city": "Bengaluru", "country": "India",
     "bio": "Third-wave cafe, single-origin beans, cozy corner spot.", "followers": 8900, "engagement_rate": 4.5,
     "posts_last_30": 18, "instagram": "grainandgrind", "facebook": None,
     "website": None, "phone": "+91 88888 44422", "has_online_orders": False, "verified": False},
    {"name": "Tokyo Bites Ramen", "category": "Restaurant", "city": "Delhi", "country": "India",
     "bio": "Handmade tonkotsu ramen. Dine-in & takeaway.", "followers": 61200, "engagement_rate": 5.2,
     "posts_last_30": 25, "instagram": "tokyobitesdelhi", "facebook": "tokyobites",
     "website": None, "phone": "+91 98888 77712", "has_online_orders": False, "verified": True},
    {"name": "Casa Verde Kitchen", "category": "Restaurant", "city": "Lisbon", "country": "Portugal",
     "bio": "Plant-forward Mediterranean. Chef-owned.", "followers": 12500, "engagement_rate": 2.9,
     "posts_last_30": 12, "instagram": "casaverdekitchen", "facebook": "casaverdekitchen",
     "website": "https://casaverde.pt", "phone": "+351 21 555 1234", "has_online_orders": True, "verified": True},
    {"name": "Brew Street Cafe", "category": "Cafe", "city": "Austin", "country": "USA",
     "bio": "Local roaster & pastry bar. Community first.", "followers": 4200, "engagement_rate": 3.1,
     "posts_last_30": 9, "instagram": "brewstreetatx", "facebook": None,
     "website": None, "phone": "+1 512 555 0198", "has_online_orders": False, "verified": False},

    # Fashion
    {"name": "Indigo Thread Studio", "category": "Fashion", "city": "Jaipur", "country": "India",
     "bio": "Hand block-printed contemporary womenswear.", "followers": 42800, "engagement_rate": 4.8,
     "posts_last_30": 20, "instagram": "indigothreadstudio", "facebook": "indigothread",
     "website": None, "phone": "+91 90000 12321", "has_online_orders": False, "verified": True},
    {"name": "North & Wren", "category": "Fashion", "city": "London", "country": "UK",
     "bio": "Minimal capsule wardrobes. Made in small runs.", "followers": 88400, "engagement_rate": 3.2,
     "posts_last_30": 15, "instagram": "northandwren", "facebook": "northandwren",
     "website": "https://northandwren.co", "phone": None, "has_online_orders": True, "verified": True},
    {"name": "Mira Label", "category": "Fashion", "city": "Barcelona", "country": "Spain",
     "bio": "Slow fashion. Linen and cotton, always.", "followers": 15600, "engagement_rate": 4.1,
     "posts_last_30": 14, "instagram": "miralabel", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": False},

    # Beauty
    {"name": "Bloom Skin Studio", "category": "Beauty", "city": "Pune", "country": "India",
     "bio": "Facials, chemical peels, and laser treatments.", "followers": 18700, "engagement_rate": 3.6,
     "posts_last_30": 16, "instagram": "bloomskinstudio", "facebook": "bloomskinstudio",
     "website": None, "phone": "+91 98111 22233", "has_online_orders": False, "verified": True},
    {"name": "Luxe Nail Atelier", "category": "Beauty", "city": "New York", "country": "USA",
     "bio": "Editorial nail art. By appointment only.", "followers": 34200, "engagement_rate": 5.5,
     "posts_last_30": 24, "instagram": "luxenailatelier", "facebook": None,
     "website": None, "phone": "+1 646 555 3412", "has_online_orders": False, "verified": True},
    {"name": "Halo Brow Bar", "category": "Beauty", "city": "Melbourne", "country": "Australia",
     "bio": "Brows, lashes, and cosmetic tattooing.", "followers": 9800, "engagement_rate": 2.7,
     "posts_last_30": 11, "instagram": "halobrowbar", "facebook": "halobrow",
     "website": None, "phone": "+61 3 5555 9800", "has_online_orders": False, "verified": False},

    # Fitness
    {"name": "Iron Ridge Strength", "category": "Fitness", "city": "Denver", "country": "USA",
     "bio": "Barbell and powerlifting gym. Coached programs.", "followers": 6400, "engagement_rate": 3.8,
     "posts_last_30": 13, "instagram": "ironridgestrength", "facebook": "ironridge",
     "website": None, "phone": "+1 303 555 4411", "has_online_orders": False, "verified": False},
    {"name": "Flow Yoga Collective", "category": "Fitness", "city": "Bali", "country": "Indonesia",
     "bio": "Vinyasa, yin, and breathwork by the beach.", "followers": 51200, "engagement_rate": 4.9,
     "posts_last_30": 26, "instagram": "flowyogacollective", "facebook": "flowyoga",
     "website": None, "phone": None, "has_online_orders": False, "verified": True},

    # Photography
    {"name": "Amelia Wren Photo", "category": "Photography", "city": "Paris", "country": "France",
     "bio": "Wedding and lifestyle photographer.", "followers": 22400, "engagement_rate": 3.4,
     "posts_last_30": 8, "instagram": "ameliawrenphoto", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": True},
    {"name": "Rohit Kapoor Studios", "category": "Photography", "city": "Delhi", "country": "India",
     "bio": "Commercial product & fashion photography.", "followers": 11500, "engagement_rate": 2.4,
     "posts_last_30": 6, "instagram": "rohitkapoorstudios", "facebook": "rohitkapoorstudios",
     "website": "https://rohitkapoor.in", "phone": "+91 98111 87654", "has_online_orders": False, "verified": False},

    # Handmade / Home
    {"name": "Clay & Kiln Ceramics", "category": "Handmade", "city": "Kyoto", "country": "Japan",
     "bio": "Wheel-thrown stoneware and tea sets.", "followers": 17800, "engagement_rate": 5.1,
     "posts_last_30": 12, "instagram": "clayandkiln", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": True},
    {"name": "Wildthread Weavers", "category": "Handmade", "city": "Oaxaca", "country": "Mexico",
     "bio": "Handloomed textiles from artisan collectives.", "followers": 28900, "engagement_rate": 4.6,
     "posts_last_30": 17, "instagram": "wildthreadweavers", "facebook": "wildthreadweavers",
     "website": None, "phone": None, "has_online_orders": False, "verified": True},

    # Wellness
    {"name": "Kavi Ayurveda", "category": "Wellness", "city": "Kerala", "country": "India",
     "bio": "Panchakarma retreats and daily consultations.", "followers": 8600, "engagement_rate": 3.2,
     "posts_last_30": 10, "instagram": "kaviayurveda", "facebook": "kaviayurveda",
     "website": None, "phone": "+91 90000 99988", "has_online_orders": False, "verified": False},
    {"name": "Sun Salt Sauna", "category": "Wellness", "city": "Reykjavik", "country": "Iceland",
     "bio": "Cold plunge + sauna therapy sessions.", "followers": 5400, "engagement_rate": 4.2,
     "posts_last_30": 9, "instagram": "sunsaltsauna", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": False},

    # Food (specialty)
    {"name": "Sourdough Society", "category": "Food", "city": "Melbourne", "country": "Australia",
     "bio": "Wild yeast breads and pastries. Pre-order weekly.", "followers": 31200, "engagement_rate": 6.1,
     "posts_last_30": 21, "instagram": "sourdoughsociety", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": True},
    {"name": "Cocoa Nib Chocolates", "category": "Food", "city": "Brussels", "country": "Belgium",
     "bio": "Bean-to-bar single origin chocolates.", "followers": 14700, "engagement_rate": 3.9,
     "posts_last_30": 11, "instagram": "cocoanibchocolates", "facebook": "cocoanibchocolates",
     "website": None, "phone": None, "has_online_orders": False, "verified": False},

    # Tech / Services
    {"name": "PixelPilot Studio", "category": "Tech", "city": "Berlin", "country": "Germany",
     "bio": "Product design and no-code MVPs for startups.", "followers": 4900, "engagement_rate": 2.1,
     "posts_last_30": 5, "instagram": "pixelpilotstudio", "facebook": None,
     "website": "https://pixelpilot.studio", "phone": None, "has_online_orders": False, "verified": False},
    {"name": "Loop Marketing Co", "category": "Tech", "city": "Toronto", "country": "Canada",
     "bio": "Performance marketing for DTC brands.", "followers": 7800, "engagement_rate": 2.8,
     "posts_last_30": 7, "instagram": "loopmarketingco", "facebook": "loopmarketingco",
     "website": None, "phone": "+1 416 555 2211", "has_online_orders": False, "verified": False},

    # Extra
    {"name": "The Petal Room", "category": "Handmade", "city": "Amsterdam", "country": "Netherlands",
     "bio": "Boutique florist. Weddings & events.", "followers": 9600, "engagement_rate": 4.3,
     "posts_last_30": 14, "instagram": "thepetalroom", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": True},
    {"name": "Ember Barbershop", "category": "Beauty", "city": "Chicago", "country": "USA",
     "bio": "Classic cuts, hot towel shaves.", "followers": 3700, "engagement_rate": 2.6,
     "posts_last_30": 7, "instagram": "emberbarbershop", "facebook": "emberbarbershop",
     "website": None, "phone": "+1 312 555 8899", "has_online_orders": False, "verified": False},
    {"name": "Verde Juicery", "category": "Food", "city": "Los Angeles", "country": "USA",
     "bio": "Cold-pressed juices and cleanses.", "followers": 21400, "engagement_rate": 3.5,
     "posts_last_30": 16, "instagram": "verdejuicery", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": False},
    {"name": "Bond Street Tailors", "category": "Fashion", "city": "London", "country": "UK",
     "bio": "Bespoke suiting since 1978. By appointment.", "followers": 6100, "engagement_rate": 1.9,
     "posts_last_30": 4, "instagram": "bondstreettailors", "facebook": "bondstreettailors",
     "website": None, "phone": "+44 20 5555 7100", "has_online_orders": False, "verified": False},
    {"name": "Ocean Ride Surf", "category": "Fitness", "city": "Lisbon", "country": "Portugal",
     "bio": "Surf lessons and coastal camps.", "followers": 12800, "engagement_rate": 4.4,
     "posts_last_30": 13, "instagram": "oceanridesurf", "facebook": None,
     "website": None, "phone": "+351 91 555 0202", "has_online_orders": False, "verified": True},
    {"name": "Little Vine Bakery", "category": "Cafe", "city": "Toronto", "country": "Canada",
     "bio": "French pastries and hand-laminated croissants.", "followers": 19800, "engagement_rate": 5.4,
     "posts_last_30": 19, "instagram": "littlevinebakery", "facebook": None,
     "website": None, "phone": "+1 647 555 1010", "has_online_orders": False, "verified": True},
    {"name": "Studio Nova Interiors", "category": "Tech", "city": "Copenhagen", "country": "Denmark",
     "bio": "Residential & retail interior design studio.", "followers": 8300, "engagement_rate": 3.1,
     "posts_last_30": 8, "instagram": "studionovainteriors", "facebook": None,
     "website": None, "phone": None, "has_online_orders": False, "verified": False},
]


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


async def seed_businesses(db) -> None:
    count = await db.businesses.count_documents({})
    if count >= len(BUSINESSES):
        return
    now = datetime.now(timezone.utc).isoformat()
    docs = []
    for i, b in enumerate(BUSINESSES):
        slug = _slug(b["name"])
        docs.append({
            "id": slug,
            "slug": slug,
            "cover_image": _cover(i),
            "created_at": now,
            **b,
        })
    # upsert each
    for doc in docs:
        await db.businesses.update_one({"slug": doc["slug"]}, {"$set": doc}, upsert=True)
