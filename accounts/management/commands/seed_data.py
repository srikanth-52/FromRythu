from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from farmers.models import FarmerProfile
from customers.models import CustomerProfile
from products.models import Category, Product, PriceHistory, Review
from inventory.models import StockRecord
from orders.models import Order, OrderItem
from payments.models import Payment
from messaging.models import Message

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the FromRythu database with realistic demo farmers, customers, products, stock, and orders"

    def handle(self, *args, **options):
        self.stdout.write("Starting FromRythu data seeding...")

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@fromrythu.com',
                'first_name': 'Rythu',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write("Created Admin user: admin / admin123")

        # 2. Farmers
        farmers_data = [
            {
                'username': 'farmer_ramesh',
                'first_name': 'Ramesh',
                'last_name': 'Reddy',
                'email': 'ramesh.reddy@naturalfarms.in',
                'phone': '9848022334',
                'city': 'Nalgonda',
                'state': 'Telangana',
                'farm_name': 'Sri Venkateswara Natural Farms',
                'farm_location': 'Sy No. 42, Miryalaguda Road, Nalgonda',
                'village': 'Chityala',
                'district': 'Nalgonda',
                'size': 8.5,
                'crops': 'BPT 5204 Sona Masoori Paddy, Desi Red Gram, Cotton',
                'experience': 14,
                'type': 'Natural',
                'upi': 'rameshreddy@oksbi',
                'approved': True,
                'bio': 'Third generation farmer dedicated to Subhash Palekar Natural Farming (SPNF) techniques. No urea, no synthetic pesticides. Fresh from black soil lands.'
            },
            {
                'username': 'farmer_venkat',
                'first_name': 'Venkat',
                'last_name': 'Rao',
                'email': 'venkat.annapurna@gmail.com',
                'phone': '9949112233',
                'city': 'Warangal',
                'state': 'Telangana',
                'farm_name': 'Annapurna Organic Agri Collective',
                'farm_location': 'Hanamkonda Highway, Warangal Rural',
                'village': 'Dharmasagar',
                'district': 'Warangal',
                'size': 12.0,
                'crops': 'Korralu (Foxtail Millet), Teja Red Chilli, Salem Turmeric',
                'experience': 9,
                'type': 'Organic',
                'upi': 'annapurna.agro@icici',
                'approved': True,
                'bio': 'Certified organic farm focusing on traditional indigenous millets and GI-tagged Guntur/Warangal Teja chillies.'
            },
            {
                'username': 'farmer_laxmi',
                'first_name': 'Laxmi',
                'last_name': 'Devi',
                'email': 'laxmi.rythu@farmfresh.org',
                'phone': '9440556677',
                'city': 'Medak',
                'state': 'Telangana',
                'farm_name': 'Prakruthi Rythu Mahila Farm',
                'farm_location': 'Narsapur Forest Border, Medak',
                'village': 'Narsapur',
                'district': 'Medak',
                'size': 4.5,
                'crops': 'Country Farm Tomatoes, Green Chillies, Palak, Banganapalli Mangoes',
                'experience': 7,
                'type': 'Organic',
                'upi': 'prakruthifarms@upi',
                'approved': True,
                'bio': 'Women-led collective cultivating chemical-free seasonal vegetables and heirloom fruit varieties.'
            }
        ]

        farmers_map = {}
        for fd in farmers_data:
            user, u_created = User.objects.get_or_create(
                username=fd['username'],
                defaults={
                    'email': fd['email'],
                    'first_name': fd['first_name'],
                    'last_name': fd['last_name'],
                    'role': 'farmer',
                    'phone_number': fd['phone'],
                    'city': fd['city'],
                    'state': fd['state'],
                    'address': fd['farm_location'],
                    'is_verified': fd['approved'],
                }
            )
            if u_created:
                user.set_password('farmer123')
                user.save()

            profile, _ = FarmerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'farm_name': fd['farm_name'],
                    'farm_location': fd['farm_location'],
                    'village': fd['village'],
                    'district': fd['district'],
                    'state': fd['state'],
                    'farm_size_acres': fd['size'],
                    'primary_crops': fd['crops'],
                    'farming_experience_years': fd['experience'],
                    'farming_type': fd['type'],
                    'upi_id': fd['upi'],
                    'is_approved': fd['approved'],
                    'bio': fd['bio'],
                }
            )
            farmers_map[fd['username']] = user
            self.stdout.write(f"Farmer ready: {fd['username']} / farmer123")

        # 3. Customers
        customers_data = [
            {
                'username': 'customer_anita',
                'first_name': 'Anita',
                'last_name': 'Sharma',
                'email': 'anita.sharma@gmail.com',
                'phone': '9885012345',
                'address': 'Flat 402, Green Meadows, Madhapur, Hitec City',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'pincode': '500081',
            },
            {
                'username': 'customer_rajesh',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
                'email': 'rajesh.k@rediffmail.com',
                'phone': '9177890123',
                'address': 'Plot 12, West Marredpally',
                'city': 'Secunderabad',
                'state': 'Telangana',
                'pincode': '500026',
            }
        ]

        customers_map = {}
        for cd in customers_data:
            user, u_created = User.objects.get_or_create(
                username=cd['username'],
                defaults={
                    'email': cd['email'],
                    'first_name': cd['first_name'],
                    'last_name': cd['last_name'],
                    'role': 'customer',
                    'phone_number': cd['phone'],
                    'city': cd['city'],
                    'state': cd['state'],
                    'pincode': cd['pincode'],
                    'address': cd['address'],
                    'is_verified': True,
                }
            )
            if u_created:
                user.set_password('customer123')
                user.save()

            CustomerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'default_delivery_address': cd['address'],
                    'city': cd['city'],
                    'state': cd['state'],
                    'pincode': cd['pincode'],
                }
            )
            customers_map[cd['username']] = user
            self.stdout.write(f"Customer ready: {cd['username']} / customer123")

        # 4. Categories
        categories_data = [
            {'name': 'Grains & Paddy', 'icon': 'bi-flower1', 'desc': 'Pure aged Sona Masoori, Basmati, and single-origin raw paddy straight from fields.'},
            {'name': 'Pulses & Dal', 'icon': 'bi-circle', 'desc': 'Unpolished, naturally dried Toor Dal, Moong, Urad, and Chana with complete protein intact.'},
            {'name': 'Millets & Superfoods', 'icon': 'bi-shield-check', 'desc': 'Gluten-free traditional ancient millets: Foxtail (Korralu), Finger millet (Ragi), Little millet.'},
            {'name': 'Fresh Farm Vegetables', 'icon': 'bi-basket2', 'desc': 'Morning-harvested crisp farm vegetables delivered within 24 hours of plucking.'},
            {'name': 'Spices & Condiments', 'icon': 'bi-fire', 'desc': 'Sun-dried Guntur Teja red chillies, raw Salem turmeric, coriander, and native spices.'},
            {'name': 'Cotton & Commercial', 'icon': 'bi-box-seam', 'desc': 'Direct farmer bulk raw cotton lint, organic oilseeds, and commercial agricultural produce.'},
        ]

        categories_map = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=c['name'],
                defaults={'icon_class': c['icon'], 'description': c['desc']}
            )
            categories_map[c['name']] = cat

        # 5. Products
        products_data = [
            {
                'farmer': farmers_map['farmer_ramesh'],
                'category': categories_map['Grains & Paddy'],
                'name': 'BPT 5204 Sona Masoori Raw Rice (Aged 1 Year)',
                'variety': 'BPT 5204 Samba Masoori',
                'unit': 'bag_25kg',
                'price': 1450.0,
                'mrp': 1850.0,
                'min_qty': 1.0,
                'is_organic': True,
                'featured': True,
                'stock': 85.0,
                'image_url': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80',
                'desc': 'Authentic single-origin Sona Masoori rice harvested from Krishna basin black soils. Aged for 12 months for soft, non-sticky cooking.'
            },
            {
                'farmer': farmers_map['farmer_ramesh'],
                'category': categories_map['Pulses & Dal'],
                'name': 'Desi Natural Red Gram (Unpolished Toor Dal)',
                'variety': 'TDRG-4 Native',
                'unit': 'kg',
                'price': 155.0,
                'mrp': 195.0,
                'min_qty': 2.0,
                'is_organic': True,
                'featured': True,
                'stock': 120.0,
                'image_url': 'https://images.unsplash.com/photo-1596797882870-8c33deeac224?auto=format&fit=crop&w=600&q=80',
                'desc': 'Sun-dried native red gram split in traditional wooden chakkis without artificial polishing, oil coating, or sulfur bleaching.'
            },
            {
                'farmer': farmers_map['farmer_venkat'],
                'category': categories_map['Millets & Superfoods'],
                'name': 'Organic Foxtail Millet (Korralu)',
                'variety': 'SIA 3088 Desi',
                'unit': 'kg',
                'price': 95.0,
                'mrp': 130.0,
                'min_qty': 1.0,
                'is_organic': True,
                'featured': True,
                'stock': 200.0,
                'image_url': 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=600&q=80',
                'desc': 'Fiber-dense, low-glycemic foxtail millet grown purely under dryland rainfed organic conditions in Warangal.'
            },
            {
                'farmer': farmers_map['farmer_venkat'],
                'category': categories_map['Spices & Condiments'],
                'name': 'Teja Hot Red Chilli (Whole Dried)',
                'variety': 'Guntur Teja (S17)',
                'unit': 'kg',
                'price': 240.0,
                'mrp': 310.0,
                'min_qty': 1.0,
                'is_organic': True,
                'featured': False,
                'stock': 150.0,
                'image_url': 'https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80',
                'desc': 'Fiery aroma, rich natural red color, and high capsaicin content. Sun-dried on hygienic tarpaulins.'
            },
            {
                'farmer': farmers_map['farmer_laxmi'],
                'category': categories_map['Fresh Farm Vegetables'],
                'name': 'Vine-Ripened Country Tomatoes (Naatu Tamata)',
                'variety': 'Desi Pusa Naatu',
                'unit': 'kg',
                'price': 35.0,
                'mrp': 50.0,
                'min_qty': 3.0,
                'is_organic': True,
                'featured': True,
                'stock': 350.0,
                'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80',
                'desc': 'Tangy, juicy heirloom country tomatoes picked the day before delivery. Free from carbide and ripening gases.'
            },
            {
                'farmer': farmers_map['farmer_ramesh'],
                'category': categories_map['Cotton & Commercial'],
                'name': 'Clean Raw Cotton Lint (First Pick Quality)',
                'variety': 'Long Staple 32mm',
                'unit': 'quintal',
                'price': 7200.0,
                'mrp': 7900.0,
                'min_qty': 1.0,
                'is_organic': False,
                'featured': False,
                'stock': 25.0,
                'image_url': 'https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=600&q=80',
                'desc': 'Premium white staple cotton harvested directly from irrigated black cotton soil fields in Nalgonda.'
            }
        ]

        created_products = []
        for p in products_data:
            prod, p_created = Product.objects.get_or_create(
                name=p['name'],
                farmer=p['farmer'],
                defaults={
                    'category': p['category'],
                    'variety': p['variety'],
                    'unit': p['unit'],
                    'price_per_unit': p['price'],
                    'mrp': p['mrp'],
                    'min_order_quantity': p['min_qty'],
                    'is_organic': p['is_organic'],
                    'featured': p['featured'],
                    'description': p['desc'],
                    'image_url_fallback': p['image_url'],
                    'harvest_date': date.today() - timedelta(days=12),
                    'is_active': True,
                }
            )
            created_products.append(prod)

            # Initial stock inward record
            if not StockRecord.objects.filter(product=prod).exists():
                StockRecord.objects.create(
                    product=prod,
                    transaction_type='IN',
                    quantity=p['stock'],
                    batch_no=f"BATCH-2026-NOV-{prod.id}",
                    notes="Harvest stock registered by farmer",
                    created_by=p['farmer']
                )

            # Price history entry
            if not PriceHistory.objects.filter(product=prod).exists():
                PriceHistory.objects.create(
                    product=prod,
                    old_price=p['price'] + 30,
                    new_price=p['price'],
                    reason="Seasonal harvest abundance price drop",
                    changed_by=p['farmer']
                )

        # 6. Sample Order
        customer = customers_map['customer_anita']
        if not Order.objects.filter(customer=customer).exists():
            prod1 = created_products[0]  # Sona Masoori
            prod2 = created_products[4]  # Naatu Tomatoes

            subtotal = (prod1.price_per_unit * 1) + (prod2.price_per_unit * 5)
            delivery = 0.0
            order = Order.objects.create(
                customer=customer,
                total_amount=subtotal,
                delivery_fee=delivery,
                final_amount=subtotal + delivery,
                status='accepted',
                payment_status='completed',
                shipping_full_name='Anita Sharma',
                shipping_phone='9885012345',
                shipping_address='Flat 402, Green Meadows, Madhapur, Hitec City',
                shipping_city='Hyderabad',
                shipping_state='Telangana',
                shipping_pincode='500081',
                delivery_instructions='Please ring bell twice and leave at doorstep if unavailable.'
            )

            OrderItem.objects.create(
                order=order,
                product=prod1,
                farmer=prod1.farmer,
                product_name=prod1.name,
                unit=prod1.unit,
                unit_price=prod1.price_per_unit,
                quantity=1.0,
                subtotal=prod1.price_per_unit * 1,
                item_status='accepted'
            )

            OrderItem.objects.create(
                order=order,
                product=prod2,
                farmer=prod2.farmer,
                product_name=prod2.name,
                unit=prod2.unit,
                unit_price=prod2.price_per_unit,
                quantity=5.0,
                subtotal=prod2.price_per_unit * 5,
                item_status='packed'
            )

            Payment.objects.create(
                order=order,
                payment_method='UPI',
                amount=subtotal + delivery,
                status='completed',
                paid_at=timezone.now(),
                payment_notes='Verified via UPI transaction ref'
            )

            # Deduct stock for the order
            StockRecord.objects.create(
                product=prod1,
                transaction_type='OUT',
                quantity=1.0,
                batch_no=f"ORD-{order.order_number}",
                notes="Order fulfillment",
                created_by=customer
            )
            StockRecord.objects.create(
                product=prod2,
                transaction_type='OUT',
                quantity=5.0,
                batch_no=f"ORD-{order.order_number}",
                notes="Order fulfillment",
                created_by=customer
            )

            # Sample reviews
            Review.objects.get_or_create(
                product=prod1,
                customer=customer,
                defaults={'rating': 5, 'comment': 'Exceptional Sona Masoori! Cooked so fluffy with that genuine village fragrance. Highly recommend Ramesh garu!'}
            )

            # Sample message
            Message.objects.get_or_create(
                sender=customer,
                receiver=prod1.farmer,
                defaults={
                    'product': prod1,
                    'order': order,
                    'content': 'Namaste Ramesh garu! When will the next new crop batch of Sona Masoori arrive? Loved the quality!'
                }
            )

            Message.objects.get_or_create(
                sender=prod1.farmer,
                receiver=customer,
                defaults={
                    'product': prod1,
                    'order': order,
                    'content': 'Namaste Anita garu! Glad you enjoyed the rice. The upcoming Rabi harvest will be ready by end of December.'
                }
            )

        self.stdout.write(self.style.SUCCESS("FromRythu database successfully seeded!"))

