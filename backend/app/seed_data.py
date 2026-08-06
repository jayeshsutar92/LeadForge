"""Manual seed script for LeadForge.

Usage:
    cd backend
    python -m app.seed_data

Seeds a default admin user and 30 sample businesses into the database.
Skips records that already exist (idempotent).
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.business import Business
from app.models.user import User

ADMIN_EMAIL = "jayeshsutar76@gmail.com"
ADMIN_PASSWORD = "admin123"
ADMIN_NAME = "Admin"

SAMPLE_BUSINESSES: list[dict] = [
    {"slug": "spice-garden-mumbai", "name": "Spice Garden", "category": "Restaurant", "city": "Mumbai", "country": "India", "bio": "Authentic Indian cuisine since 1995", "followers": 45000, "engagement_rate": 3.8, "instagram": "https://instagram.com/spicegarden", "cover_image": "", "posts_last_30": 18},
    {"slug": "cafe-mocha-pune", "name": "Café Mocha", "category": "Cafe", "city": "Pune", "country": "India", "bio": "Artisan coffee & pastries", "followers": 12000, "engagement_rate": 4.2, "instagram": "https://instagram.com/cafemocha", "cover_image": "", "posts_last_30": 22},
    {"slug": "urban-threads-delhi", "name": "Urban Threads", "category": "Fashion", "city": "Delhi", "country": "India", "bio": "Contemporary streetwear brand", "followers": 85000, "engagement_rate": 5.1, "website": "https://urbanthreads.in", "instagram": "https://instagram.com/urbanthreads", "cover_image": "", "posts_last_30": 25},
    {"slug": "glow-studio-bangalore", "name": "Glow Studio", "category": "Beauty", "city": "Bangalore", "country": "India", "bio": "Premium salon & skincare", "followers": 32000, "engagement_rate": 3.5, "instagram": "https://instagram.com/glowstudio", "cover_image": "", "posts_last_30": 14},
    {"slug": "iron-forge-gym-hyderabad", "name": "Iron Forge Gym", "category": "Fitness", "city": "Hyderabad", "country": "India", "bio": "Strength & conditioning centre", "followers": 28000, "engagement_rate": 4.0, "instagram": "https://instagram.com/ironforgegym", "cover_image": "", "posts_last_30": 20},
    {"slug": "pixel-frame-photography-mumbai", "name": "Pixel Frame Photography", "category": "Photography", "city": "Mumbai", "country": "India", "bio": "Wedding & portrait photography", "followers": 55000, "engagement_rate": 3.2, "instagram": "https://instagram.com/pixelframe", "cover_image": "", "posts_last_30": 10},
    {"slug": "clay-craft-jaipur", "name": "Clay Craft", "category": "Handmade", "city": "Jaipur", "country": "India", "bio": "Handmade pottery & ceramics", "followers": 18000, "engagement_rate": 5.5, "instagram": "https://instagram.com/claycraft", "cover_image": "", "posts_last_30": 12},
    {"slug": "zen-wellness-goa", "name": "Zen Wellness", "category": "Wellness", "city": "Goa", "country": "India", "bio": "Yoga retreats & holistic healing", "followers": 42000, "engagement_rate": 4.8, "instagram": "https://instagram.com/zenwellness", "cover_image": "", "posts_last_30": 16},
    {"slug": "tech-pulse-bangalore", "name": "TechPulse", "category": "Tech", "city": "Bangalore", "country": "India", "bio": "SaaS product studio", "followers": 9000, "engagement_rate": 2.1, "website": "https://techpulse.io", "instagram": "https://instagram.com/techpulse", "cover_image": "", "posts_last_30": 8},
    {"slug": "farm-fresh-delhi", "name": "Farm Fresh", "category": "Food", "city": "Delhi", "country": "India", "bio": "Organic produce delivery", "followers": 21000, "engagement_rate": 3.9, "instagram": "https://instagram.com/farmfresh", "cover_image": "", "posts_last_30": 19},
    {"slug": "tandoori-nights-london", "name": "Tandoori Nights", "category": "Restaurant", "city": "London", "country": "UK", "bio": "Award-winning Indian restaurant", "followers": 67000, "engagement_rate": 4.5, "instagram": "https://instagram.com/tandoorinights", "cover_image": "", "posts_last_30": 24},
    {"slug": "brew-brothers-new-york", "name": "Brew Brothers", "category": "Cafe", "city": "New York", "country": "USA", "bio": "Specialty coffee roasters", "followers": 38000, "engagement_rate": 3.7, "instagram": "https://instagram.com/brewbrothers", "cover_image": "", "posts_last_30": 21},
    {"slug": "silk-route-fashion-dubai", "name": "Silk Route Fashion", "category": "Fashion", "city": "Dubai", "country": "UAE", "bio": "Luxury ethnic wear", "followers": 120000, "engagement_rate": 6.2, "instagram": "https://instagram.com/silkroutefashion", "cover_image": "", "posts_last_30": 30},
    {"slug": "radiance-beauty-bar-singapore", "name": "Radiance Beauty Bar", "category": "Beauty", "city": "Singapore", "country": "Singapore", "bio": "Korean beauty treatments", "followers": 25000, "engagement_rate": 4.1, "instagram": "https://instagram.com/radiancebb", "cover_image": "", "posts_last_30": 15},
    {"slug": "peak-performance-sydney", "name": "Peak Performance", "category": "Fitness", "city": "Sydney", "country": "Australia", "bio": "CrossFit & functional training", "followers": 52000, "engagement_rate": 3.0, "website": "https://peakperformance.com.au", "instagram": "https://instagram.com/peakperf", "cover_image": "", "posts_last_30": 17},
    {"slug": "lens-stories-tokyo", "name": "Lens Stories", "category": "Photography", "city": "Tokyo", "country": "Japan", "bio": "Editorial & commercial photography", "followers": 73000, "engagement_rate": 2.8, "instagram": "https://instagram.com/lensstories", "cover_image": "", "posts_last_30": 9},
    {"slug": "artisan-weave-bali", "name": "Artisan Weave", "category": "Handmade", "city": "Bali", "country": "Indonesia", "bio": "Hand-woven textiles & accessories", "followers": 14000, "engagement_rate": 5.0, "instagram": "https://instagram.com/artisanweave", "cover_image": "", "posts_last_30": 11},
    {"slug": "serenity-spa-phuket", "name": "Serenity Spa", "category": "Wellness", "city": "Phuket", "country": "Thailand", "bio": "Traditional Thai wellness retreats", "followers": 31000, "engagement_rate": 4.3, "instagram": "https://instagram.com/serenityspa", "cover_image": "", "posts_last_30": 13},
    {"slug": "code-lab-berlin", "name": "Code Lab", "category": "Tech", "city": "Berlin", "country": "Germany", "bio": "Dev agency & code school", "followers": 7500, "engagement_rate": 1.9, "website": "https://codelab.de", "instagram": "https://instagram.com/codelab", "cover_image": "", "posts_last_30": 6},
    {"slug": "harvest-bowl-toronto", "name": "Harvest Bowl", "category": "Food", "city": "Toronto", "country": "Canada", "bio": "Plant-based meal prep & delivery", "followers": 19000, "engagement_rate": 4.6, "instagram": "https://instagram.com/harvestbowl", "cover_image": "", "posts_last_30": 23},
    {"slug": "masala-magic-chennai", "name": "Masala Magic", "category": "Restaurant", "city": "Chennai", "country": "India", "bio": "South Indian coastal cuisine", "followers": 35000, "engagement_rate": 3.4, "instagram": "https://instagram.com/masalamagic", "cover_image": "", "posts_last_30": 16},
    {"slug": "the-grind-cafe-austin", "name": "The Grind", "category": "Cafe", "city": "Austin", "country": "USA", "bio": "Local roast coffee house", "followers": 11000, "engagement_rate": 4.9, "instagram": "https://instagram.com/thegrindaustin", "cover_image": "", "posts_last_30": 20},
    {"slug": "noir-fashion-paris", "name": "Noir Fashion", "category": "Fashion", "city": "Paris", "country": "France", "bio": "Minimalist French streetwear", "followers": 98000, "engagement_rate": 5.7, "instagram": "https://instagram.com/noirfashion", "cover_image": "", "posts_last_30": 28},
    {"slug": "pure-skin-los-angeles", "name": "Pure Skin", "category": "Beauty", "city": "Los Angeles", "country": "USA", "bio": "Celebrity skincare clinic", "followers": 150000, "engagement_rate": 6.8, "instagram": "https://instagram.com/pureskinla", "cover_image": "", "posts_last_30": 26},
    {"slug": "summit-fitness-denver", "name": "Summit Fitness", "category": "Fitness", "city": "Denver", "country": "USA", "bio": "Altitude training facility", "followers": 22000, "engagement_rate": 3.3, "instagram": "https://instagram.com/summitfitness", "cover_image": "", "posts_last_30": 14},
    {"slug": "shutter-co-cape-town", "name": "Shutter & Co.", "category": "Photography", "city": "Cape Town", "country": "South Africa", "bio": "Lifestyle & travel photography", "followers": 41000, "engagement_rate": 3.6, "instagram": "https://instagram.com/shutterco", "cover_image": "", "posts_last_30": 12},
    {"slug": "earth-pottery-amsterdam", "name": "Earth Pottery", "category": "Handmade", "city": "Amsterdam", "country": "Netherlands", "bio": "Sustainable ceramic studio", "followers": 16000, "engagement_rate": 4.4, "instagram": "https://instagram.com/earthpottery", "cover_image": "", "posts_last_30": 10},
    {"slug": "inner-peace-retreat-rishikesh", "name": "Inner Peace Retreat", "category": "Wellness", "city": "Rishikesh", "country": "India", "bio": "Meditation & ayurveda centre", "followers": 58000, "engagement_rate": 5.3, "instagram": "https://instagram.com/innerpeaceretreat", "cover_image": "", "posts_last_30": 18},
    {"slug": "neon-labs-san-francisco", "name": "Neon Labs", "category": "Tech", "city": "San Francisco", "country": "USA", "bio": "AI-powered design tools", "followers": 15000, "engagement_rate": 2.5, "website": "https://neonlabs.ai", "instagram": "https://instagram.com/neonlabs", "cover_image": "", "posts_last_30": 7},
    {"slug": "golden-spoon-bangkok", "name": "Golden Spoon", "category": "Food", "city": "Bangkok", "country": "Thailand", "bio": "Thai street food catering", "followers": 27000, "engagement_rate": 4.7, "instagram": "https://instagram.com/goldenspoon", "cover_image": "", "posts_last_30": 22},
]


async def seed(session: AsyncSession) -> None:
    """Insert seed data. Skips duplicates."""

    # ── Admin user ─────────────────────────────────────────────────────
    existing_admin = await session.execute(
        select(User).where(User.email == ADMIN_EMAIL)
    )
    if existing_admin.scalar_one_or_none() is None:
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            full_name=ADMIN_NAME,
            role="admin",
        )
        session.add(admin)
        await session.commit()
        print(f"[SEED] Admin user created: {ADMIN_EMAIL}")
    else:
        print(f"[SEED] Admin user already exists: {ADMIN_EMAIL}")

    # ── Sample businesses ──────────────────────────────────────────────
    created = 0
    for biz_data in SAMPLE_BUSINESSES:
        existing = await session.execute(
            select(Business).where(Business.slug == biz_data["slug"])
        )
        if existing.scalar_one_or_none() is not None:
            continue
        business = Business(**biz_data)
        session.add(business)
        created += 1

    if created:
        await session.commit()
    print(f"[SEED] Created {created} businesses ({len(SAMPLE_BUSINESSES) - created} already existed)")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed(session)
    print("[SEED] Done.")


if __name__ == "__main__":
    asyncio.run(main())
