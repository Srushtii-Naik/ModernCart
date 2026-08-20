"""
Management command that populates the database with demo categories
and 15 sample products (each with a generated placeholder image), so
the store looks complete immediately after `migrate`.

Usage:
    python manage.py load_sample_products
"""
import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


CATEGORIES = [
    {'name': 'Electronics', 'icon': 'fa-laptop', 'color': (37, 99, 235)},
    {'name': 'Fashion', 'icon': 'fa-shirt', 'color': (236, 72, 153)},
    {'name': 'Home & Living', 'icon': 'fa-couch', 'color': (16, 185, 129)},
    {'name': 'Sports & Outdoors', 'icon': 'fa-dumbbell', 'color': (245, 158, 11)},
    {'name': 'Beauty & Personal Care', 'icon': 'fa-spa', 'color': (168, 85, 247)},
]

PRODUCTS = [
    {
        'name': 'Wireless Noise-Cancelling Headphones', 'category': 'Electronics',
        'price': 7999, 'old_price': 9999,
        'short_description': 'Premium over-ear headphones with active noise cancellation.',
        'description': 'Immerse yourself in rich, detailed sound with 40-hour battery life, plush memory-foam ear cushions and adaptive active noise cancellation that adjusts to your environment in real time.',
        'features': 'Active Noise Cancellation\n40-hour battery life\nBluetooth 5.3\nQuick charge: 10 min = 5 hours\nBuilt-in mic for calls',
        'rating': 4.7, 'reviews_count': 328, 'featured': True,
    },
    {
        'name': 'Smart Fitness Watch', 'category': 'Electronics',
        'price': 5499, 'old_price': None,
        'short_description': 'Track workouts, sleep and heart rate around the clock.',
        'description': 'A sleek fitness companion with a bright AMOLED display, continuous heart-rate monitoring, sleep tracking and 15 built-in sport modes. Water resistant up to 50 metres.',
        'features': 'AMOLED touch display\n7-day battery life\nHeart rate & SpO2 monitor\n15 sport modes\n5 ATM water resistance',
        'rating': 4.5, 'reviews_count': 214, 'featured': True,
    },
    {
        'name': 'Portable Bluetooth Speaker', 'category': 'Electronics',
        'price': 2499, 'old_price': 3199,
        'short_description': 'Compact speaker with room-filling 360° sound.',
        'description': 'Take your music anywhere with this rugged, IPX7 waterproof speaker delivering deep bass and crisp highs, plus 12 hours of playtime on a single charge.',
        'features': '360° immersive sound\nIPX7 waterproof\n12-hour battery\nBuilt-in power bank\nPair two speakers for stereo',
        'rating': 4.4, 'reviews_count': 156, 'featured': False,
    },
    {
        'name': 'Mechanical Keyboard', 'category': 'Electronics',
        'price': 4299, 'old_price': None,
        'short_description': 'Tactile mechanical keyboard for work and gaming.',
        'description': 'A responsive mechanical keyboard with hot-swappable switches, per-key RGB backlighting and a durable aluminum frame built for thousands of hours of typing.',
        'features': 'Hot-swappable switches\nPer-key RGB lighting\nAluminum top plate\nUSB-C detachable cable\nN-key rollover',
        'rating': 4.6, 'reviews_count': 189, 'featured': True,
    },
    {
        'name': '4K Action Camera', 'category': 'Electronics',
        'price': 8999, 'old_price': 10999,
        'short_description': 'Capture stunning 4K adventures, waterproof to 10m.',
        'description': 'Shoot smooth 4K60 footage with advanced image stabilization, a rugged waterproof shell and a companion app for instant editing and sharing.',
        'features': '4K60 video recording\nBuilt-in image stabilization\nWaterproof to 10m\nVoice control\nWi-Fi & Bluetooth sharing',
        'rating': 4.3, 'reviews_count': 97, 'featured': False,
    },
    {
        'name': 'Classic Denim Jacket', 'category': 'Fashion',
        'price': 2999, 'old_price': 3999,
        'short_description': 'Timeless denim jacket for every season.',
        'description': 'A wardrobe staple crafted from premium washed denim with a comfortable regular fit, sturdy brass buttons and a soft cotton lining.',
        'features': '100% premium cotton denim\nRegular fit\nBrass button closure\nMachine washable\nAvailable in 5 sizes',
        'rating': 4.5, 'reviews_count': 142, 'featured': True,
    },
    {
        'name': 'Running Sneakers', 'category': 'Fashion',
        'price': 3499, 'old_price': None,
        'short_description': 'Lightweight sneakers built for everyday runs.',
        'description': 'Engineered with a breathable knit upper and responsive cushioned midsole, these sneakers keep you comfortable through every mile.',
        'features': 'Breathable knit upper\nResponsive foam midsole\nDurable rubber outsole\nReflective details\nLightweight design',
        'rating': 4.6, 'reviews_count': 261, 'featured': True,
    },
    {
        'name': 'Leather Crossbody Bag', 'category': 'Fashion',
        'price': 3299, 'old_price': 4199,
        'short_description': 'Handcrafted leather bag for everyday essentials.',
        'description': 'A minimalist crossbody bag made from full-grain leather, featuring multiple compartments and an adjustable strap for all-day comfort.',
        'features': 'Full-grain leather\nAdjustable strap\nMultiple compartments\nMagnetic closure\nFits 8" tablets',
        'rating': 4.4, 'reviews_count': 88, 'featured': False,
    },
    {
        'name': 'Classic Aviator Sunglasses', 'category': 'Fashion',
        'price': 1599, 'old_price': None,
        'short_description': 'UV-protected aviators with a timeless silhouette.',
        'description': 'These aviator sunglasses combine a lightweight metal frame with polarized, UV400-protected lenses for clear vision on sunny days.',
        'features': 'Polarized lenses\nUV400 protection\nLightweight metal frame\nSpring hinges\nIncludes protective case',
        'rating': 4.2, 'reviews_count': 73, 'featured': False,
    },
    {
        'name': 'Minimalist Table Lamp', 'category': 'Home & Living',
        'price': 1899, 'old_price': 2399,
        'short_description': 'Warm ambient lighting with a modern silhouette.',
        'description': 'A softly diffused, dimmable table lamp with a fabric shade and solid wood base — designed to bring a calm, warm glow to any room.',
        'features': 'Dimmable warm LED\nSolid wood base\nFabric shade\nTouch control\nEnergy efficient',
        'rating': 4.6, 'reviews_count': 118, 'featured': True,
    },
    {
        'name': 'Ceramic Dinnerware Set (16-piece)', 'category': 'Home & Living',
        'price': 3799, 'old_price': None,
        'short_description': 'Elegant stoneware set for 4, dishwasher safe.',
        'description': 'This 16-piece stoneware dinnerware set brings understated elegance to your table, with a durable glaze that resists chips and stains.',
        'features': 'Service for 4\nChip-resistant glaze\nMicrowave & dishwasher safe\nStackable design\nNeutral matte finish',
        'rating': 4.5, 'reviews_count': 64, 'featured': False,
    },
    {
        'name': 'Memory Foam Pillow (Set of 2)', 'category': 'Home & Living',
        'price': 1499, 'old_price': 1999,
        'short_description': 'Contoured support for a better night’s sleep.',
        'description': 'Ergonomically contoured memory foam pillows that relieve neck and shoulder pressure, wrapped in a breathable, removable cover.',
        'features': 'Contoured memory foam\nBreathable cooling cover\nRemovable, washable cover\nHypoallergenic\nSet of 2',
        'rating': 4.3, 'reviews_count': 201, 'featured': False,
    },
    {
        'name': 'Adjustable Dumbbell Set', 'category': 'Sports & Outdoors',
        'price': 6499, 'old_price': 7999,
        'short_description': 'Space-saving dumbbells that adjust from 2.5–24kg.',
        'description': 'Replace an entire rack of weights with this single adjustable dumbbell set, letting you dial in the exact resistance for every exercise.',
        'features': 'Adjustable 2.5kg–24kg per dumbbell\nQuick-turn dial system\nCompact storage tray\nDurable steel plates\nNon-slip grip handle',
        'rating': 4.7, 'reviews_count': 175, 'featured': True,
    },
    {
        'name': 'Yoga Mat Pro', 'category': 'Sports & Outdoors',
        'price': 1299, 'old_price': None,
        'short_description': 'Extra-thick, non-slip mat for yoga and pilates.',
        'description': 'A high-density, extra-thick yoga mat with a textured non-slip surface on both sides, offering superior cushioning for joints during practice.',
        'features': '6mm extra-thick cushioning\nDouble-sided non-slip texture\nLightweight & portable\nIncludes carry strap\nEco-friendly TPE material',
        'rating': 4.5, 'reviews_count': 249, 'featured': True,
    },
    {
        'name': 'Vitamin C Brightening Serum', 'category': 'Beauty & Personal Care',
        'price': 899, 'old_price': 1199,
        'short_description': 'Daily serum for a brighter, more even skin tone.',
        'description': 'A lightweight, fast-absorbing serum formulated with stabilized Vitamin C and hyaluronic acid to visibly brighten skin and lock in hydration.',
        'features': '10% stabilized Vitamin C\nHyaluronic acid hydration\nLightweight, non-greasy\nSuitable for all skin types\nCruelty-free',
        'rating': 4.4, 'reviews_count': 312, 'featured': False,
    },
]


class Command(BaseCommand):
    help = 'Populates the database with sample categories and 15 demo products (with generated placeholder images).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding ModernCart demo data...'))

        category_objs = {}
        for cat in CATEGORIES:
            obj, created = Category.objects.get_or_create(
                name=cat['name'],
                defaults={'slug': slugify(cat['name']), 'icon': cat['icon']},
            )
            category_objs[cat['name']] = (obj, cat['color'])
            if created:
                self.stdout.write(f"  + Created category: {obj.name}")

        created_count = 0
        for item in PRODUCTS:
            if Product.objects.filter(name=item['name']).exists():
                continue

            category_obj, color = category_objs[item['category']]
            slug = slugify(item['name'])

            product = Product(
                name=item['name'],
                slug=slug,
                category=category_obj,
                description=item['description'],
                short_description=item['short_description'],
                features=item['features'],
                price=item['price'],
                old_price=item.get('old_price'),
                stock=random.randint(8, 60),
                rating=item['rating'],
                reviews_count=item['reviews_count'],
                is_featured=item.get('featured', False),
                is_active=True,
            )

            image_file = self._generate_placeholder_image(item['name'], color)
            if image_file:
                product.image.save(f'{slug}.png', image_file, save=False)

            product.save()
            created_count += 1
            self.stdout.write(f"  + Created product: {product.name}")

        self.stdout.write(self.style.SUCCESS(
            f'Done. {created_count} new product(s) created, {Product.objects.count()} total in database.'
        ))

    def _generate_placeholder_image(self, name, color, size=(800, 800)):
        """Generates a simple, on-brand placeholder image for a product
        using Pillow, since no external image downloads are used."""
        if not PIL_AVAILABLE:
            return None

        img = Image.new('RGB', size, color=(248, 250, 252))
        draw = ImageDraw.Draw(img)

        # Soft rounded card background
        margin = 40
        draw.rounded_rectangle(
            [margin, margin, size[0] - margin, size[1] - margin],
            radius=40, fill=color
        )

        # Draw a lighter inner circle as a simple abstract icon
        cx, cy = size[0] // 2, size[1] // 2 - 40
        r = 140
        lighter = tuple(min(255, c + 60) for c in color)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=lighter)

        # Product initials
        initials = ''.join([w[0].upper() for w in name.split()[:2]])
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 90)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), initials, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx - tw / 2, cy - th / 2 - bbox[1]), initials, fill=color, font=font)

        # Product name at the bottom of the card
        try:
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
        except Exception:
            small_font = ImageFont.load_default()

        label = name if len(name) <= 26 else name[:24] + '...'
        bbox2 = draw.textbbox((0, 0), label, font=small_font)
        tw2 = bbox2[2] - bbox2[0]
        draw.text((size[0] / 2 - tw2 / 2, size[1] - margin - 90), label, fill=(255, 255, 255), font=small_font)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return ContentFile(buffer.read())
