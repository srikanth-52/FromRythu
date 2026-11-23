"""
FromRythu (RYTHU_DIRECT) - Interactive Streamlit Application
Connects directly to the Django backend database and models.
Run via: streamlit run streamlit_app.py
"""

import os
import django
from datetime import date, datetime

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone

from accounts.models import User
from farmers.models import FarmerProfile
from customers.models import CustomerProfile
from products.models import Product, Category, PriceHistory, Review
from inventory.models import StockRecord
from orders.models import Cart, CartItem, Order, OrderItem
from payments.models import Payment
from messaging.models import Message

# Page configuration
st.set_page_config(
    page_title="FromRythu - Direct Selling Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
        padding: 1.5rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(27,67,50,0.15);
    }
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        border-left: 5px solid #2d6a4f;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Top Banner
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800;">🌾 FromRythu</h1>
            <p style="margin: 0.2rem 0 0; opacity: 0.9; font-size: 1.05rem;">
                Farmer-to-Customer Direct Selling Marketplace • Streamlit Interactive Hub
            </p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.15); padding: 0.5rem 1rem; border-radius: 10px;">
            <span style="font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;">ZERO MIDDLEMEN</span><br>
            <small style="opacity: 0.9;">100% Direct Payouts</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=400&q=80", use_container_width=True)
st.sidebar.markdown("### 🧭 Portal Navigation")

portal = st.sidebar.radio(
    "Select Workspace:",
    [
        "📊 Admin Analytics Dashboard",
        "🌾 Farmer Portal (Harvest & Stock)",
        "🛒 Customer Marketplace & Shopping",
        "💬 Direct Messages Hub",
        "🗄️ Database Tables Explorer"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**FromRythu Quick Links:**
- Django Server: `http://127.0.0.1:8000/`
- Farmer Login: `farmer_ramesh` / `farmer123`
- Customer Login: `customer_anita` / `customer123`
""")


# ==============================================================================
# 1. ADMIN ANALYTICS DASHBOARD
# ==============================================================================
if portal == "📊 Admin Analytics Dashboard":
    st.subheader("📊 Executive Overview & Marketplace Telemetry")

    total_farmers = User.objects.filter(role='farmer').count()
    verified_farmers = User.objects.filter(role='farmer', is_verified=True).count()
    total_customers = User.objects.filter(role='customer').count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    gmv = Order.objects.aggregate(v=Sum('final_amount'))['v'] or 0.0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total GMV Revenue", f"₹{gmv:,.2f}", "+100% Direct")
    with col2:
        st.metric("Total Orders", f"{total_orders}", "Fulfilled / Active")
    with col3:
        st.metric("Registered Farmers", f"{total_farmers}", f"{verified_farmers} Verified")
    with col4:
        st.metric("Household Buyers", f"{total_customers}", "Active Consumers")
    with col5:
        st.metric("Live Harvests", f"{total_products}", "In Catalog")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("##### 🥧 Revenue by Agricultural Category")
        cat_data = OrderItem.objects.values('product__category__name').annotate(
            revenue=Sum('subtotal'),
            units=Sum('quantity')
        ).order_by('-revenue')

        if cat_data:
            df_cat = pd.DataFrame(list(cat_data))
            df_cat.rename(columns={'product__category__name': 'Category'}, inplace=True)
            df_cat['Category'] = df_cat['Category'].fillna('Uncategorized')
            fig_pie = px.pie(
                df_cat, 
                names='Category', 
                values='revenue', 
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No orders yet to plot category sales.")

    with col_chart2:
        st.markdown("##### 🏆 Best Selling Farm Produce")
        prod_data = OrderItem.objects.values('product_name').annotate(
            revenue=Sum('subtotal')
        ).order_by('-revenue')[:6]

        if prod_data:
            df_prod = pd.DataFrame(list(prod_data))
            fig_bar = px.bar(
                df_prod,
                x='revenue',
                y='product_name',
                orientation='h',
                labels={'revenue': 'Revenue (₹)', 'product_name': 'Produce'},
                color='revenue',
                color_continuous_scale='Greens'
            )
            fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No produce sales recorded yet.")

    st.markdown("---")

    # Farmer KYC Approval Console
    st.markdown("##### 👨‍🌾 Rythu Verification & KYC Management")
    farmers = FarmerProfile.objects.select_related('user').all()
    farmer_records = []
    for f in farmers:
        farmer_records.append({
            'ID': f.id,
            'Farm Name': f.farm_name,
            'Farmer': f.user.get_full_name() or f.user.username,
            'District': f.district,
            'Area (Acres)': float(f.farm_size_acres),
            'Primary Crops': f.primary_crops,
            'Farming Type': f.farming_type,
            'UPI ID': f.upi_id or 'N/A',
            'Status': '✅ Verified' if f.is_approved else '⏳ Pending KYC'
        })
    df_farmers = pd.DataFrame(farmer_records)
    st.dataframe(df_farmers, use_container_width=True)

    unapproved = farmers.filter(is_approved=False)
    if unapproved.exists():
        st.warning(f"There are {unapproved.count()} pending farmer applications requiring KYC verification.")
        f_to_approve = st.selectbox("Select Farmer to Approve:", unapproved, format_func=lambda x: f"{x.farm_name} ({x.user.username})")
        if st.button("Approve Farmer & Grant Verified Badge"):
            f_to_approve.is_approved = True
            f_to_approve.user.is_verified = True
            f_to_approve.save()
            f_to_approve.user.save()
            st.success(f"Farmer '{f_to_approve.farm_name}' approved successfully!")
            st.rerun()


# ==============================================================================
# 2. FARMER PORTAL
# ==============================================================================
elif portal == "🌾 Farmer Portal (Harvest & Stock)":
    st.subheader("🌾 Rythu Produce & Physical Inventory Console")

    farmers_list = User.objects.filter(role='farmer')
    selected_farmer_username = st.selectbox(
        "Simulate as Farmer:",
        farmers_list,
        format_func=lambda u: f"{u.farmer_profile.farm_name if hasattr(u, 'farmer_profile') else u.username} ({u.username})"
    )

    farmer_products = Product.objects.filter(farmer=selected_farmer_username)
    farmer_items = OrderItem.objects.filter(farmer=selected_farmer_username)
    farmer_rev = farmer_items.aggregate(v=Sum('subtotal'))['v'] or 0.0

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Farmer Total Revenue", f"₹{farmer_rev:,.2f}")
    with col_f2:
        st.metric("Listed Harvests", f"{farmer_products.count()}")
    with col_f3:
        st.metric("Customer Orders", f"{farmer_items.values('order').distinct().count()}")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📦 Listed Produce & Stock", "➕ Add Fresh Harvest", "🏷️ Instant Price Control", "🚚 Order Dispatches"])

    with tab1:
        prod_rows = []
        for p in farmer_products:
            prod_rows.append({
                'ID': p.id,
                'Name': p.name,
                'Variety': p.variety or 'Native',
                'Category': p.category.name if p.category else '-',
                'Price (₹)': float(p.price_per_unit),
                'Unit': p.unit,
                'Available Stock': float(p.available_stock),
                'Organic': 'Yes' if p.is_organic else 'No',
                'Status': 'Live' if p.is_active else 'Hidden'
            })
        if prod_rows:
            st.dataframe(pd.DataFrame(prod_rows), use_container_width=True)
        else:
            st.info("No produce listed yet for this farmer.")

        # Quick Stock Movement
        st.markdown("###### 📝 Inward / Outward Stock Entry")
        with st.form("quick_stock_form"):
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                target_prod = st.selectbox("Produce", farmer_products, format_func=lambda x: x.name)
            with col_s2:
                tx_type = st.selectbox("Movement Type", ["IN (Harvest Inward)", "OUT (Dispatch / Wastage)"])
            with col_s3:
                tx_qty = st.number_input("Quantity", min_value=1.0, value=20.0, step=1.0)
            with col_s4:
                batch_no = st.text_input("Batch / Lot #", value=f"LOT-{date.today().strftime('%Y%m%d')}")
            notes = st.text_input("Notes", value="Field harvest addition")
            
            if st.form_submit_button("Record Stock Movement"):
                actual_type = 'IN' if 'IN' in tx_type else 'OUT'
                StockRecord.objects.create(
                    product=target_prod,
                    transaction_type=actual_type,
                    quantity=tx_qty,
                    batch_no=batch_no,
                    notes=notes,
                    created_by=selected_farmer_username
                )
                st.success(f"Stock record logged for {target_prod.name} ({actual_type} {tx_qty} {target_prod.unit})!")
                st.rerun()

    with tab2:
        st.markdown("##### Add Fresh Harvest Produce to Catalog")
        with st.form("add_product_form"):
            c_name = st.text_input("Produce Name", placeholder="e.g. Desi Organic Toor Dal")
            c_var = st.text_input("Crop Variety", placeholder="e.g. Native Seed BPT 5204")
            c_cat = st.selectbox("Category", Category.objects.all(), format_func=lambda x: x.name)
            c_desc = st.text_area("Harvest Details & Description", "Grown in nutrient-rich black soil without chemical fertilizers.")
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                c_unit = st.selectbox("Unit", ["kg", "quintal", "bag_25kg", "bag_50kg", "bunch", "litre"])
            with col_p2:
                c_price = st.number_input("Direct Selling Price (₹)", min_value=1.0, value=75.0, step=1.0)
            with col_p3:
                c_mrp = st.number_input("Benchmark Market Retail Price (₹)", min_value=1.0, value=95.0, step=1.0)

            col_p4, col_p5 = st.columns(2)
            with col_p4:
                c_stock = st.number_input("Initial Harvest Quantity (Stock In)", min_value=1.0, value=100.0)
            with col_p5:
                c_img = st.text_input("Photo URL", value="https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80")

            c_organic = st.checkbox("Certified Organic / Zero Chemical Residue", value=True)

            if st.form_submit_button("Publish Produce Directly to Marketplace"):
                if c_name:
                    new_prod = Product.objects.create(
                        farmer=selected_farmer_username,
                        category=c_cat,
                        name=c_name,
                        variety=c_var,
                        description=c_desc,
                        unit=c_unit,
                        price_per_unit=c_price,
                        mrp=c_mrp,
                        is_organic=c_organic,
                        image_url_fallback=c_img,
                        harvest_date=date.today(),
                        is_active=True
                    )
                    StockRecord.objects.create(
                        product=new_prod,
                        transaction_type='IN',
                        quantity=c_stock,
                        batch_no=f"INITIAL-{date.today().strftime('%Y%m%d')}",
                        notes="Initial harvest published",
                        created_by=selected_farmer_username
                    )
                    st.success(f"Produce '{c_name}' published with {c_stock} {c_unit} available stock!")
                    st.rerun()

    with tab3:
        st.markdown("##### 🏷️ Instant Price Control & Live Transparency")
        if farmer_products.exists():
            p_to_price = st.selectbox("Select Produce to Adjust Price:", farmer_products, format_func=lambda x: f"{x.name} (Current: ₹{x.price_per_unit}/{x.unit})")
            old_price = float(p_to_price.price_per_unit)
            new_price = st.number_input("New Selling Rate (₹):", value=old_price, step=1.0)
            price_reason = st.text_input("Reason for Change:", value="Abundant seasonal harvest discount")
            
            if st.button("Update Price & Log History"):
                if new_price != old_price:
                    p_to_price.price_per_unit = new_price
                    p_to_price.save()
                    PriceHistory.objects.create(
                        product=p_to_price,
                        old_price=old_price,
                        new_price=new_price,
                        reason=price_reason,
                        changed_by=selected_farmer_username
                    )
                    st.success(f"Price updated from ₹{old_price} to ₹{new_price}! Logged in price history.")
                    st.rerun()

    with tab4:
        st.markdown("##### 🚚 Orders Received for Your Harvests")
        if farmer_items.exists():
            for item in farmer_items.select_related('order', 'order__customer'):
                with st.expander(f"Order #{item.order.order_number} - {item.product_name} ({item.quantity} {item.unit})"):
                    st.write(f"**Customer:** {item.order.customer.get_full_name() or item.order.customer.username} ({item.order.shipping_phone})")
                    st.write(f"**Address:** {item.order.shipping_address}, {item.order.shipping_city}")
                    st.write(f"**Amount:** ₹{item.subtotal} (Payment: {item.order.payment.payment_method if hasattr(item.order, 'payment') else 'COD'})")
                    
                    current_status = item.item_status
                    new_status = st.selectbox(
                        "Update Item Progress:",
                        ['pending', 'accepted', 'packed', 'shipped', 'delivered', 'cancelled'],
                        index=['pending', 'accepted', 'packed', 'shipped', 'delivered', 'cancelled'].index(current_status),
                        key=f"status_{item.id}"
                    )
                    if st.button("Save Progress", key=f"btn_{item.id}"):
                        item.item_status = new_status
                        item.save()
                        st.success(f"Status updated to {new_status}!")
                        st.rerun()
        else:
            st.info("No orders received yet for this farmer.")


# ==============================================================================
# 3. CUSTOMER MARKETPLACE
# ==============================================================================
elif portal == "🛒 Customer Marketplace & Shopping":
    st.subheader("🛒 Farm-Fresh Produce Direct From Rythus")

    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        cats = ['All Categories'] + [c.name for c in Category.objects.all()]
        sel_cat = st.selectbox("Category Filter:", cats)
    with col_filter2:
        organic_only = st.checkbox("Certified Organic Only", value=False)
    with col_filter3:
        max_p = st.slider("Max Price (₹)", 10, 10000, 2000, step=20)

    # Filter products
    prods = Product.objects.filter(is_active=True, price_per_unit__lte=max_p).select_related('farmer', 'category', 'farmer__farmer_profile')
    if sel_cat != 'All Categories':
        prods = prods.filter(category__name=sel_cat)
    if organic_only:
        prods = prods.filter(is_organic=True)

    st.write(f"Showing **{prods.count()}** authentic farm harvests:")

    cols = st.columns(3)
    for idx, p in enumerate(prods):
        with cols[idx % 3]:
            st.image(p.display_image, use_container_width=True)
            st.markdown(f"**{p.name}**")
            st.caption(f"🌾 Rythu: {p.farmer.farmer_profile.farm_name if hasattr(p.farmer, 'farmer_profile') else p.farmer.username} ({p.farmer.city})")
            
            saving_tag = f" (Save {p.direct_savings_percentage}%)" if p.direct_savings_percentage > 0 else ""
            st.markdown(f"### ₹{p.price_per_unit} <small style='font-size: 0.9rem; color: #64748b;'>/{p.unit}{saving_tag}</small>", unsafe_allow_html=True)
            st.write(f"Available Stock: **{p.available_stock} {p.unit}**")
            
            # Interactive Order Button
            order_qty = st.number_input("Qty:", min_value=float(p.min_order_quantity), max_value=max(float(p.min_order_quantity), float(p.available_stock)), value=float(p.min_order_quantity), step=1.0, key=f"qty_{p.id}")
            
            if st.button("🛒 Instant Direct Order", key=f"buy_{p.id}", disabled=(p.available_stock <= 0)):
                # Simulate customer order
                customer_user = User.objects.filter(role='customer').first()
                if not customer_user:
                    st.error("No customer profile found. Run 'python manage.py seed_data' first.")
                else:
                    subtotal = p.price_per_unit * order_qty
                    order = Order.objects.create(
                        customer=customer_user,
                        total_amount=subtotal,
                        delivery_fee=0.0,
                        final_amount=subtotal,
                        status='accepted',
                        payment_status='completed',
                        shipping_full_name=customer_user.get_full_name() or customer_user.username,
                        shipping_phone=customer_user.phone_number or '9885012345',
                        shipping_address=customer_user.address or 'Hitec City, Hyderabad',
                        shipping_city=customer_user.city or 'Hyderabad',
                        shipping_state='Telangana',
                        shipping_pincode='500081'
                    )
                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        farmer=p.farmer,
                        product_name=p.name,
                        unit=p.unit,
                        unit_price=p.price_per_unit,
                        quantity=order_qty,
                        subtotal=subtotal,
                        item_status='accepted'
                    )
                    StockRecord.objects.create(
                        product=p,
                        transaction_type='OUT',
                        quantity=order_qty,
                        batch_no=f"ORD-{order.order_number}",
                        notes="Direct order via Streamlit",
                        created_by=customer_user
                    )
                    Payment.objects.create(
                        order=order,
                        payment_method='UPI',
                        amount=subtotal,
                        status='completed',
                        paid_at=timezone.now()
                    )
                    st.success(f"🎉 Order #{order.order_number} confirmed! Deducted {order_qty} {p.unit} from farm stock.")
                    st.rerun()


# ==============================================================================
# 4. DIRECT MESSAGES HUB
# ==============================================================================
elif portal == "💬 Direct Messages Hub":
    st.subheader("💬 Direct Farmer-to-Customer Inquiries & Messages")

    messages_qs = Message.objects.select_related('sender', 'receiver', 'product').order_by('-created_at')
    
    col_m1, col_m2 = st.columns([1, 2])
    
    with col_m1:
        st.markdown("##### ✉️ Send Direct Message")
        all_users = User.objects.all()
        sender = st.selectbox("Sender:", all_users, format_func=lambda u: f"{u.username} ({u.role})", key="msg_sender")
        receiver = st.selectbox("Recipient:", all_users, format_func=lambda u: f"{u.username} ({u.role})", key="msg_rec")
        content = st.text_area("Message Content:", placeholder="Ask about harvest quality or dispatch timing...")
        
        if st.button("Send Direct Message"):
            if content.strip():
                Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    content=content
                )
                st.success("Message dispatched!")
                st.rerun()

    with col_m2:
        st.markdown("##### 📜 Recent Communications Log")
        for m in messages_qs[:12]:
            with st.container():
                st.markdown(f"**From:** `{m.sender.username}` ({m.sender.role}) ➔ **To:** `{m.receiver.username}` ({m.receiver.role})")
                st.caption(f"Time: {m.created_at.strftime('%Y-%m-%d %H:%M')}")
                st.info(m.content)


# ==============================================================================
# 5. DATABASE TABLES EXPLORER
# ==============================================================================
elif portal == "🗄️ Database Tables Explorer":
    st.subheader("🗄️ Live Database Tables & Relational Records")

    table_choice = st.selectbox(
        "Select Table to Inspect:",
        [
            "Users (accounts_user)",
            "Farmer Profiles (farmers_farmerprofile)",
            "Products (products_product)",
            "Inventory Stock Ledger (inventory_stockrecord)",
            "Orders (orders_order)",
            "Order Items (orders_orderitem)",
            "Price History (products_pricehistory)",
            "Payments (payments_payment)"
        ]
    )

    if "Users" in table_choice:
        users = list(User.objects.values('id', 'username', 'email', 'role', 'phone_number', 'city', 'state', 'is_verified', 'date_joined'))
        st.dataframe(pd.DataFrame(users), use_container_width=True)

    elif "Farmer Profiles" in table_choice:
        fp = list(FarmerProfile.objects.values('id', 'user__username', 'farm_name', 'district', 'state', 'farm_size_acres', 'primary_crops', 'farming_type', 'upi_id', 'is_approved'))
        st.dataframe(pd.DataFrame(fp), use_container_width=True)

    elif "Products" in table_choice:
        prods = list(Product.objects.values('id', 'name', 'farmer__username', 'category__name', 'price_per_unit', 'unit', 'is_organic', 'is_active', 'created_at'))
        st.dataframe(pd.DataFrame(prods), use_container_width=True)

    elif "Stock" in table_choice:
        stocks = list(StockRecord.objects.values('id', 'product__name', 'transaction_type', 'quantity', 'batch_no', 'notes', 'created_at'))
        st.dataframe(pd.DataFrame(stocks), use_container_width=True)

    elif "Orders" in table_choice:
        orders = list(Order.objects.values('id', 'order_number', 'customer__username', 'total_amount', 'delivery_fee', 'final_amount', 'status', 'payment_status', 'shipping_city', 'created_at'))
        st.dataframe(pd.DataFrame(orders), use_container_width=True)

    elif "Order Items" in table_choice:
        items = list(OrderItem.objects.values('id', 'order__order_number', 'product_name', 'farmer__username', 'quantity', 'unit', 'unit_price', 'subtotal', 'item_status'))
        st.dataframe(pd.DataFrame(items), use_container_width=True)

    elif "Price History" in table_choice:
        prices = list(PriceHistory.objects.values('id', 'product__name', 'old_price', 'new_price', 'reason', 'created_at'))
        st.dataframe(pd.DataFrame(prices), use_container_width=True)

    elif "Payments" in table_choice:
        pmts = list(Payment.objects.values('id', 'order__order_number', 'payment_method', 'amount', 'status', 'transaction_id', 'paid_at'))
        st.dataframe(pd.DataFrame(pmts), use_container_width=True)

