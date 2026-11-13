from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from farmers.models import FarmerProfile
from customers.models import CustomerProfile
from products.models import Category, Product
from inventory.models import StockRecord
from orders.models import Cart, CartItem, Order, OrderItem

User = get_user_model()

class FromRythuMarketplaceTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Farmer setup
        self.farmer_user = User.objects.create_user(
            username='test_farmer',
            password='password123',
            role='farmer',
            is_verified=True
        )
        self.farmer_profile = FarmerProfile.objects.create(
            user=self.farmer_user,
            farm_name='Test Natural Farm',
            farm_location='Nalgonda Road',
            primary_crops='Paddy, Pulses'
        )

        # Customer setup
        self.customer_user = User.objects.create_user(
            username='test_customer',
            password='password123',
            role='customer',
            is_verified=True
        )
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user,
            default_delivery_address='Hitec City, Hyderabad'
        )

        # Category and Product setup
        self.category = Category.objects.create(name='Grains & Rice', slug='grains-rice')
        self.product = Product.objects.create(
            farmer=self.farmer_user,
            category=self.category,
            name='Desi Sona Masoori Rice',
            slug='desi-sona-masoori-rice',
            unit='kg',
            price_per_unit=60.0,
            mrp=80.0,
            min_order_quantity=1.0,
            description='Pure single origin grain.'
        )

        # Inward initial stock
        StockRecord.objects.create(
            product=self.product,
            transaction_type='IN',
            quantity=100.0,
            created_by=self.farmer_user
        )

    def test_product_stock_calculation(self):
        """Test that available stock equals stock in minus stock out."""
        self.assertEqual(self.product.available_stock, 100.0)

        # Stock out 25kg
        StockRecord.objects.create(
            product=self.product,
            transaction_type='OUT',
            quantity=25.0,
            created_by=self.farmer_user
        )
        self.assertEqual(self.product.available_stock, 75.0)

    def test_direct_savings_percentage(self):
        """Test direct consumer savings vs retail MRP."""
        # price=60, mrp=80 -> saving = ((80-60)/80)*100 = 25%
        self.assertEqual(self.product.direct_savings_percentage, 25)

    def test_farmer_dashboard_access_protection(self):
        """Customer should not be able to view farmer portal dashboard."""
        self.client.login(username='test_customer', password='password123')
        response = self.client.get(reverse('farmers:dashboard'))
        # Should redirect to role redirect or customer portal
        self.assertEqual(response.status_code, 302)

    def test_customer_cart_and_checkout(self):
        """Test adding produce to cart and checking out."""
        self.client.login(username='test_customer', password='password123')
        
        # Add to cart
        add_response = self.client.post(
            reverse('orders:add_to_cart', args=[self.product.id]),
            {'quantity': 5.0}
        )
        self.assertEqual(add_response.status_code, 302)

        cart = Cart.objects.get(customer=self.customer_user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.total_price, 300.0) # 5 * 60

        # Perform checkout
        checkout_response = self.client.post(
            reverse('orders:checkout'),
            {
                'shipping_full_name': 'Test Customer',
                'shipping_phone': '9876543210',
                'shipping_address': 'Flat 101, Test Road',
                'shipping_city': 'Hyderabad',
                'shipping_state': 'Telangana',
                'shipping_pincode': '500081',
                'payment_method': 'COD'
            }
        )
        self.assertEqual(checkout_response.status_code, 302)

        # Verify order exists
        order = Order.objects.filter(customer=self.customer_user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, 300.0)

        # Stock should now be reduced by 5 units
        self.assertEqual(self.product.available_stock, 95.0)
