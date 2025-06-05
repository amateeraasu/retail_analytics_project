pip install Faker



import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import pytz


# Initializing Faker for realistic data

fake = Faker()

# Setting Date Range of 3-5 years.


NUM_STORES = 3
# Generate data for 3 to 5 years leading up to the current date (May 31, 2025)
END_DATE = datetime(2025, 5, 31)
START_DATE = END_DATE - timedelta(days=random.randint(3 * 365, 5 * 365))
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

# Giving Random Store names and Store Locations

STORE_LOCATIONS = {
    "Store_001": {"name": "The Grand Bakery - San Francisco", "city": "San Francisco", "state": "CA", "country": "United States", "country_code": "US", "timezone": "America/Los_Angeles"},
    "Store_002": {"name": "The Grand Bakery - Austin", "city": "Austin", "state": "TX", "country": "United States", "country_code": "US", "timezone": "America/Chicago"},
    "Store_003": {"name": "The Grand Bakery - New York", "city": "New York", "state": "NY", "country": "United States", "country_code": "US", "timezone": "America/New_York"}
}


# Creating Funcions for Data Timeline


def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


# Choosing specific Time Range because stores operate strictly from 11 AM to 10 PM (22:00) local time

def random_datetime_in_day(date_obj, timezone_str):
    tz = pytz.timezone(timezone_str)
    
    # Generating a random hour between 11 AM and 9 PM (21) to ensure delivery before 10 PM (22)

    hour = random.randint(11, 21) 
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    local_dt = tz.localize(datetime(date_obj.year, date_obj.month, date_obj.day,
                                    hour, minute, second))
    return local_dt.astimezone(pytz.utc) 

# Setting Randon Time for Features like "Merchant_Accepted_Time", "delivery_time", "prep_time", etc

def generate_time_sequence(order_utc_time):
    # All times in UTC
    accept_delay = timedelta(seconds=random.randint(10, 120))
    prep_time_orig_minutes = random.randint(5, 20)
    prep_time_increased = False
    increased_prep_time_val_minutes = 0
    if random.random() < 0.1: # 10% chance of increased prep time
        prep_time_increased = True
        increased_prep_time_val_minutes = random.randint(5, 10)
    total_prep_time_minutes = prep_time_orig_minutes + increased_prep_time_val_minutes

    merchant_accepted_time = order_utc_time + accept_delay
    courier_arrival_time = merchant_accepted_time + timedelta(minutes=total_prep_time_minutes) + timedelta(minutes=random.randint(0, 5)) # Courier arrives shortly after prep
    courier_start_trip_time = courier_arrival_time + timedelta(minutes=random.randint(1, 3)) # Courier picks up and starts trip
    delivery_time = courier_start_trip_time + timedelta(minutes=random.randint(5, 25)) # Delivery trip duration

    total_delivery_time = delivery_time - courier_start_trip_time
    courier_wait_restaurant = courier_start_trip_time - courier_arrival_time
    courier_wait_eater = timedelta(minutes=0) # Assuming direct delivery from courier to eater, no wait at eater
    total_prep_handoff_time = delivery_time - merchant_accepted_time # From merchant accept to delivery

    order_duration = delivery_time - order_utc_time

    return {
        "Time Merchant Accepted": merchant_accepted_time.isoformat(timespec='milliseconds') + 'Z',
        "Time to Accept": str(accept_delay),
        "Original Prep Time": str(timedelta(minutes=prep_time_orig_minutes)),
        "Prep Time Increased?": "TRUE" if prep_time_increased else "FALSE",
        "Increased Prep Time": str(timedelta(minutes=increased_prep_time_val_minutes)),
        "Courier Arrival Time": courier_arrival_time.isoformat(timespec='milliseconds') + 'Z',
        "Time Courier Started Trip": courier_start_trip_time.isoformat(timespec='milliseconds') + 'Z',
        "Time Courier Delivered": delivery_time.isoformat(timespec='milliseconds') + 'Z',
        "Total Delivery Time": str(total_delivery_time),
        "Courier Wait Time (Restaurant)": str(courier_wait_restaurant),
        "Courier Wait Time (Eater)": str(courier_wait_eater),
        "Total Prep & Handoff Time": str(total_prep_handoff_time),
        "Order Duration": str(order_duration)
    }


#  Generating Random Data for One the Stores Selling Platforms - Snackpass

def generate_snackpass_data(store_id, store_name, start_date, end_date):
    print(f"Generating Snackpass data for {store_name}...")
    customer_data = []
    items_data = []
    sales_data = []

    # Snackpass - Items Dataset (Initial list for aggregation)
    items = [
        {"Item": "Strawberry Banana Nutella Crepe", "Category": "Sweet Crêpes", "BasePrice": 10.50},
        {"Item": "Strawberry Nutella Crepe", "Category": "Sweet Crêpes", "BasePrice": 9.99},
        {"Item": "Berries Crepe", "Category": "Sweet Crêpes", "BasePrice": 10.25},
        {"Item": "Turkey & Swiss Savory Crêpe", "Category": "Savory Crêpes", "BasePrice": 12.50},
        {"Item": "Ham & Cheddar Savory Crêpe", "Category": "Savory Crêpes", "BasePrice": 11.99},
        {"Item": "Spinach & Feta Savory Crêpe", "Category": "Savory Crêpes", "BasePrice": 11.75},
        {"Item": "Classic Croissant", "Category": "Pastries", "BasePrice": 3.50},
        {"Item": "Chocolate Croissant", "Category": "Pastries", "BasePrice": 3.99},
        {"Item": "Blueberry Muffin", "Category": "Pastries", "BasePrice": 3.25},
        {"Item": "Espresso", "Category": "Coffee", "BasePrice": 2.75},
        {"Item": "Latte", "Category": "Coffee", "BasePrice": 4.50},
        {"Item": "Cappuccino", "Category": "Coffee", "BasePrice": 4.25},
        {"Item": "Iced Coffee", "Category": "Coffee", "BasePrice": 4.00},
    ]

    item_order_counts = {item['Item']: 0 for item in items}
    item_net_sales_agg = {item['Item']: 0.0 for item in items}

    
    # Generating daily sales
    
    current_date = start_date
    while current_date <= end_date:
        orders_today = random.randint(50, 200) # Base daily orders
        if current_date.weekday() in [5, 6]: # Weekends are busier
            orders_today = int(orders_today * random.uniform(1.2, 1.8))
        if current_date.month in [11, 12]: # Holiday season boost
            orders_today = int(orders_today * random.uniform(1.1, 1.5))
        if current_date.month in [1, 2]: # Slower months
            orders_today = int(orders_today * random.uniform(0.8, 1.1))

        subtotal_day = 0
        for _ in range(orders_today):
            num_items = random.randint(1, 5)
            order_subtotal = 0
            for _ in range(num_items):
                selected_item = random.choice(items)
                item_price = selected_item['BasePrice'] * random.uniform(0.95, 1.05) # slight price variation
                order_subtotal += item_price
                
                # Aggregate for Items Dataset
                item_order_counts[selected_item['Item']] += 1
                item_net_sales_agg[selected_item['Item']] += item_price

            subtotal_day += order_subtotal

        discounts = round(subtotal_day * random.uniform(0.01, 0.05), 2)
        gross_sales = subtotal_day
        refunds = round(gross_sales * random.uniform(0.001, 0.01), 2) # small percentage for refunds
        net_sales = gross_sales - refunds - discounts

        cash = round(net_sales * random.uniform(0.1, 0.4), 2)
        gift_card_redemption = round(net_sales * random.uniform(0.0, 0.1), 2)
        store_credit_redemption = round(net_sales * random.uniform(0.0, 0.05), 2)
        
        # Ensuring total payment methods don't exceed net sales or gross sales

        
        paid_sum = cash + gift_card_redemption + store_credit_redemption
        if paid_sum > net_sales:
            diff = paid_sum - net_sales
            # Prioritize reducing cash if over
            if cash >= diff:
                cash -= diff
            else:
                # Reduce gift card then store credit if cash isn't enough
                diff -= cash
                cash = 0
                if gift_card_redemption >= diff:
                    gift_card_redemption -= diff
                else:
                    diff -= gift_card_redemption
                    gift_card_redemption = 0
                    store_credit_redemption -= diff
        
        taxes = round(net_sales * random.uniform(0.05, 0.09), 2) # Sales tax
        tips = round(net_sales * random.uniform(0.05, 0.15), 2) # Tips percentage
        total_sales = net_sales + taxes + tips # Total collected from customer

        processing_fees = round(total_sales * random.uniform(0.015, 0.025), 2)
        snackpass_fees = round(net_sales * random.uniform(0.08, 0.12), 2) # Platform commission
        expected_cash_collected = cash + tips

        sales_data.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Orders": orders_today,
            "Subtotal": f"${subtotal_day:.2f}",
            "Gross Sales": f"${gross_sales:.2f}",
            "Net Sales": f"${net_sales:.2f}",
            "Refunds": f"${refunds:.2f}",
            "Discounts": f"${discounts:.2f}",
            "Cash": f"${cash:.2f}",
            "Gift Card Redemption": f"${gift_card_redemption:.2f}",
            "Store Credit Redemption": f"${store_credit_redemption:.2f}",
            "Taxes You Owe": f"${taxes:.2f}",
            "Tips": f"${tips:.2f}",
            "Total Sales": f"${total_sales:.2f}",
            "Processing Fees": f"${processing_fees:.2f}",
            "Snackpass Fees": f"${snackpass_fees:.2f}",
            "Expected Cash Collected": f"${expected_cash_collected:.2f}"
        })
        current_date += timedelta(days=1)


    

    # Snackpass - Items Dataset (Finalizing aggregations)
    
    for item in items:
        items_data.append({
            "Item": item['Item'],
            "Category": item['Category'],
            "Orders": item_order_counts[item['Item']],
            "Net Sales": f"${item_net_sales_agg[item['Item']]:.2f}"
        })
        

    # Snackpass - Customer Dataset (Generate after sales to get realistic spend)
    num_customers = random.randint(1000, 3000) # Number of unique customers per store
    for i in range(num_customers):
        name = fake.name()
        customer_since = random_date(start_date, end_date - timedelta(days=30)) # Customer since at least 30 days ago
        
        # Simulate customer orders and spend
        lifetime_orders = random.randint(1, 50)
        lifetime_spent = round(lifetime_orders * random.uniform(5.0, 25.0), 2) # Average order value
        
        frequency = random.randint(1, 10) # How many times per month/quarter they might order
        
        # Distribute orders across app, kiosk, online (example distribution)
        app_orders = random.randint(0, lifetime_orders)
        remaining_orders = lifetime_orders - app_orders
        kiosk_orders = random.randint(0, remaining_orders)
        online_orders = remaining_orders - kiosk_orders
        
        last_order = random_datetime_in_day(random_date(customer_since, end_date), STORE_LOCATIONS[store_id]["timezone"])
        
        points = random.randint(0, 500) if random.random() < 0.7 else 0 # 70% chance of having points
        gift_card_balance = round(random.uniform(0, 50), 2) if random.random() < 0.2 else 0 # 20% chance of balance

        customer_data.append({
            "Name": name,
            "Lifetime Rank": None, # Will be filled after sorting
            "Lifetime Spent": f"${lifetime_spent:.2f}",
            "Lifetime Orders": lifetime_orders,
            "Customer Since": customer_since.strftime("%Y-%m-%d"),
            "Frequency": frequency,
            "App Orders": app_orders,
            "Kiosk Orders": kiosk_orders,
            "Online Orders": online_orders,
            "Total Orders": lifetime_orders,
            "Total Spent": f"${lifetime_spent:.2f}",
            "Last Order": last_order.isoformat(timespec='milliseconds') + 'Z',
            "Points": points if points > 0 else None,
            "Gift CardBalance": f"${gift_card_balance:.2f}" if gift_card_balance > 0 else None
        })

    # Converting to DataFrame to assign Lifetime Rank

    
    df_customers = pd.DataFrame(customer_data)
    # Convert 'Lifetime Spent' to numeric for sorting
    df_customers['Lifetime Spent_numeric'] = df_customers['Lifetime Spent'].replace({'\$': ''}, regex=True).astype(float)
    df_customers = df_customers.sort_values(by='Lifetime Spent_numeric', ascending=False).reset_index(drop=True)
    df_customers['Lifetime Rank'] = df_customers.index + 1
    df_customers = df_customers.drop(columns=['Lifetime Spent_numeric'])

    # Saving to CSV
    df_customers.to_csv(f"snackpass_customers_{store_id}.csv", index=False)
    pd.DataFrame(items_data).to_csv(f"snackpass_items_{store_id}.csv", index=False)
    pd.DataFrame(sales_data).to_csv(f"snackpass_sales_{store_id}.csv", index=False)
    print(f"Finished Snackpass data for {store_name}.")


# Generating Random Data for One the Stores Selling Platforms - UberEats


def generate_uber_eats_data(store_id, store_info, start_date, end_date):
    print(f"Generating Uber Eats data for {store_info['name']}...")
    store_info_data = []
    order_history_data = []
    payments_details_data = []

    tz = pytz.timezone(store_info['timezone'])
    
    restaurant_opened_at = random_date(start_date, start_date + timedelta(days=365)).strftime("%Y-%m-%d")

    # Uber Eats - Store Info (Daily snapshot)
    current_date = start_date
    while current_date <= end_date:
        store_info_data.append({
            "Store": store_info['name'],
            "External Store ID": store_id,
            "Country": store_info['country'],
            "Country Code": store_info['country_code'],
            "City": store_info['city'],
            "Date": current_date.strftime("%Y-%m-%d"),
            "Restaurant Opened At": restaurant_opened_at,
            "Menu Available": "TRUE",
            "Restaurant Online": "TRUE" if random.random() > 0.02 else "FALSE", # 2% chance of being offline
            "Restaurant Offline": "FALSE" if random.random() > 0.02 else "TRUE"
        })
        current_date += timedelta(days=1)

    # Uber Eats - Order History & Payments Details
    order_id_counter = 1
    current_date_for_orders = start_date
    while current_date_for_orders <= end_date:
        num_orders_day = random.randint(30, 150) # Daily orders from Uber Eats
        if current_date_for_orders.weekday() in [5, 6]:
            num_orders_day = int(num_orders_day * random.uniform(1.3, 1.8))
        if current_date_for_orders.month in [11, 12]:
            num_orders_day = int(num_orders_day * random.uniform(1.1, 1.4))

        for _ in range(num_orders_day):
            order_id = f"UE{store_id}-{order_id_counter}"
            order_uuid = fake.uuid4()
            order_utc_time = random_datetime_in_day(current_date_for_orders, store_info['timezone'])
            
            # Simulate order status
            order_status = "COMPLETED"
            delivery_status = "DELIVERED"
            canceled_by = None
            cancellation_time = None

            if random.random() < 0.05: # 5% cancellation rate
                order_status = "CANCELED"
                delivery_status = "CANCELED"
                canceled_by = random.choice(["CUSTOMER", "MERCHANT", "COURIER"])
                cancellation_time = (order_utc_time + timedelta(minutes=random.randint(5, 60))).isoformat(timespec='milliseconds') + 'Z'

            scheduled = "FALSE"
            completed = "TRUE" if order_status == "COMPLETED" else "FALSE"
            online_order = "TRUE"

            menu_item_count = random.randint(1, 6)
            currency_code = "USD"
            ticket_size = round(menu_item_count * random.uniform(8.0, 15.0), 2)

            time_sequence = generate_time_sequence(order_utc_time)

            order_history_record = {
                "Store": store_info['name'],
                "External Store ID": store_id,
                "Country": store_info['country'],
                "Country Code": store_info['country_code'],
                "City": store_info['city'],
                "Order ID": order_id,
                "Order UUID": order_uuid,
                "Order Status": order_status,
                "Delivery Status": delivery_status,
                "Scheduled?": scheduled,
                "Completed?": completed,
                "Online Order?": online_order,
                "Canceled By": canceled_by,
                "Menu Item Count": menu_item_count,
                "Currency Code": currency_code,
                "Ticket Size": f"${ticket_size:.2f}",
                "Date Ordered": order_utc_time.strftime("%Y-%m-%d"),
                "Time Customer Ordered": order_utc_time.isoformat(timespec='milliseconds') + 'Z',
                "Cancellation Time": cancellation_time,
                **time_sequence,
                "Delivery Batch Type": random.choice(["SINGLE", "BATCH"]),
                "Fulfillment Type": random.choice(["DELIVERY", "PICKUP"]),
                "Order Channel": "WEB" if random.random() < 0.3 else "MOBILE",
                "Eats Brand": "UBER_EATS",
                "Subscription Pass": random.choice(["NONE", "UBER_ONE"]) if random.random() < 0.4 else "NONE",
                "Workflow UUID": fake.uuid4()
            }
            order_history_data.append(order_history_record)

            # Payments Details
            sales_excl_tax = ticket_size
            tax_rate = random.uniform(0.05, 0.09)
            tax_on_sales = round(sales_excl_tax * tax_rate, 2)
            sales_incl_tax = sales_excl_tax + tax_on_sales

            refunds_excl_tax = 0.0
            tax_on_refunds = 0.0
            refunds_incl_tax = 0.0
            if order_status == "CANCELED":
                refund_percentage = random.uniform(0.5, 1.0) # Partial or full refund
                refunds_excl_tax = round(sales_excl_tax * refund_percentage, 2)
                tax_on_refunds = round(tax_on_sales * refund_percentage, 2)
                refunds_incl_tax = refunds_excl_tax + tax_on_refunds

            price_adjustments_excl_tax = 0.0
            tax_on_price_adjustments = 0.0
            promotions_on_items = round(sales_excl_tax * random.uniform(0.0, 0.1), 2) if random.random() < 0.3 else 0.0
            tax_on_promotion_on_items = round(promotions_on_items * tax_rate, 2)
            promotions_on_delivery = round(random.uniform(0.0, 5.0), 2) if random.random() < 0.2 else 0.0
            tax_on_promotions_on_delivery = 0.0 # Delivery promotions usually not taxed for merchant
            bag_fee = round(random.uniform(0.0, 0.15), 2) if random.random() < 0.5 else 0.0 # Bag fee is typically small
            marketing_adjustment = round(sales_excl_tax * random.uniform(-0.05, 0.05), 2) if random.random() < 0.1 else 0.0 # Could be positive or negative

            total_sales_after_adjustments_incl_tax = sales_incl_tax - refunds_incl_tax - promotions_on_items - promotions_on_delivery + bag_fee + marketing_adjustment

            marketplace_fee_percent = random.uniform(0.15, 0.30) # Uber's commission
            marketplace_fee = round(sales_excl_tax * marketplace_fee_percent, 2)
            tax_on_marketplace_fee = round(marketplace_fee * random.uniform(0.05, 0.08), 2) # Tax on the fee
            delivery_network_fee = round(random.uniform(0.5, 2.0), 2) # Fee for using delivery network
            tax_on_delivery_network_fee = round(delivery_network_fee * random.uniform(0.05, 0.08), 2)
            order_processing_fee = round(random.uniform(0.1, 0.3), 2) # Per order fee
            merchant_fee = 0.0 # Can be other fees
            tax_on_merchant_fee = 0.0

            tips = round(sales_excl_tax * random.uniform(0.05, 0.20), 2) # Customer tips
            other_payments_description = None
            other_payments = 0.0
            marketplace_facilitator_tax = tax_on_sales # Often Uber facilitates and remits
            backup_withholding_tax = 0.0 # Rare, usually 0

            total_payout = total_sales_after_adjustments_incl_tax + tips - marketplace_fee - tax_on_marketplace_fee - delivery_network_fee - tax_on_delivery_network_fee - order_processing_fee - merchant_fee - tax_on_merchant_fee + other_payments - marketplace_facilitator_tax - backup_withholding_tax
            
            payout_date = (current_date_for_orders + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")

            payments_details_data.append({
                "Store Name": store_info['name'],
                "Store ID": store_id,
                "Order ID": order_id,
                "Workflow ID": fake.uuid4(),
                "Dining Mode": "DELIVERY",
                "Payment Mode": "ONLINE",
                "Order Channel": order_history_record["Order Channel"],
                "Order Status": order_status,
                "Order Date": order_utc_time.strftime("%Y-%m-%d"),
                "Order Accept Time": order_history_record["Time Merchant Accepted"],
                "Customer Uber-Membership Status": order_history_record["Subscription Pass"],
                "Sales (excl. tax)": f"${sales_excl_tax:.2f}",
                "Tax on sales": f"${tax_on_sales:.2f}",
                "Sales (incl. tax)": f"${sales_incl_tax:.2f}",
                "Refunds (excl tax)": f"${refunds_excl_tax:.2f}",
                "Tax on Refunds": f"${tax_on_refunds:.2f}",
                "Refunds (incl tax)": f"${refunds_incl_tax:.2f}",
                "Price adjustments (excl. tax)": f"${price_adjustments_excl_tax:.2f}",
                "Tax on price adjustments": f"${tax_on_price_adjustments:.2f}",
                "Promotions on items": f"${promotions_on_items:.2f}",
                "Tax on Promotion on items": f"${tax_on_promotion_on_items:.2f}",
                "Promotions on delivery": f"${promotions_on_delivery:.2f}",
                "Tax on Promotions on Delivery": f"${tax_on_promotions_on_delivery:.2f}",
                "Bag Fee": f"${bag_fee:.2f}",
                "Marketing adjustment": f"${marketing_adjustment:.2f}",
                "Total Sales after Adjustments (incl tax)": f"${total_sales_after_adjustments_incl_tax:.2f}",
                "Marketplace fee": f"${marketplace_fee:.2f}",
                "Marketplace fee %": f"{marketplace_fee_percent*100:.2f}%",
                "Tax on Marketplace fee": f"${tax_on_marketplace_fee:.2f}",
                "Delivery Network Fee": f"${delivery_network_fee:.2f}",
                "Tax on delivery network fee": f"${tax_on_delivery_network_fee:.2f}",
                "Order Processing Fee": f"${order_processing_fee:.2f}",
                "Merchant Fee": f"${merchant_fee:.2f}",
                "Tax on Merchant Fee": f"${tax_on_merchant_fee:.2f}",
                "Tips": f"${tips:.2f}",
                "Other payments description": other_payments_description,
                "Other payments": f"${other_payments:.2f}",
                "Marketplace Facilitator Tax": f"${marketplace_facilitator_tax:.2f}",
                "Backup Withholding Tax": f"${backup_withholding_tax:.2f}",
                "Total payout": f"${total_payout:.2f}",
                "Payout Date": payout_date,
                "Markup Amount": "$0.00", # Assuming no markup for this franchise
                "Markup Tax": "$0.00",
                "Retailer Loyalty ID": None,
                "Payout reference ID": fake.uuid4()
            })
            order_id_counter += 1
        current_date_for_orders += timedelta(days=1)

    # Saving to CSV
    pd.DataFrame(store_info_data).to_csv(f"ubereats_store_info_{store_id}.csv", index=False)
    pd.DataFrame(order_history_data).to_csv(f"ubereats_order_history_{store_id}.csv", index=False)
    pd.DataFrame(payments_details_data).to_csv(f"ubereats_payments_details_{store_id}.csv", index=False)
    print(f"Finished Uber Eats data for {store_info['name']}.")


# Generating Random Data for One the Stores Selling Platforms - Doordash


def generate_doordash_data(store_id, store_info, start_date, end_date):
    print(f"Generating DoorDash data for {store_info['name']}...")
    financial_details_data = []
    payout_summary_data = []

    tz_local = pytz.timezone(store_info['timezone'])
    tz_utc = pytz.utc

    # DoorDash - Financial Details
    
    doordash_order_id_counter = 1
    current_date_for_transactions = start_date
    while current_date_for_transactions <= end_date:
        num_transactions_day = random.randint(40, 180) # Daily transactions from DoorDash
        if current_date_for_transactions.weekday() in [5, 6]:
            num_transactions_day = int(num_transactions_day * random.uniform(1.3, 1.7))
        if current_date_for_transactions.month in [11, 12]:
            num_transactions_day = int(num_transactions_day * random.uniform(1.1, 1.4))

        for _ in range(num_transactions_day):
            transaction_utc_dt = random_datetime_in_day(current_date_for_transactions, store_info['timezone'])
            transaction_local_dt = transaction_utc_dt.astimezone(tz_local)
            
            payout_date_dt = transaction_utc_dt + timedelta(days=random.randint(1, 5)) # Payout a few days later
            
            doordash_order_id = str(random.randint(100000000000, 999999999999)) # 12 digit ID
            merchant_delivery_id = fake.uuid4()
            transaction_type = random.choice(["DELIVERY", "PICKUP"])
            
            final_order_status = random.choice(["Picked Up", "Delivered"])
            if random.random() < 0.03: # 3% chance of cancellation
                final_order_status = "Canceled"

            subtotal = round(random.uniform(10.0, 40.0), 2)
            subtotal_tax_passed = round(subtotal * random.uniform(0.05, 0.09), 2)
            pre_adjusted_subtotal = subtotal # For simplicity, often same as subtotal
            pre_adjusted_tax_subtotal = subtotal_tax_passed

            commission_percent = random.uniform(0.18, 0.28)
            commission = round(subtotal * commission_percent, 2)
            commission_tax = round(commission * random.uniform(0.05, 0.08), 2)

            marketing_fees = round(subtotal * random.uniform(0.0, 0.05), 2) if random.random() < 0.2 else 0.0
            marketing_fee_tax = round(marketing_fees * random.uniform(0.05, 0.08), 2)

            snap_ebt_discount = 0.0 # Assuming bakery doesn't accept SNAP EBT
            credit_amount = 0.0 # Customer credits
            debit_amount = 0.0 # Customer debits

            error_charge = round(random.uniform(0.0, 5.0), 2) if random.random() < 0.01 else 0.0
            adjustment = round(random.uniform(-5.0, 5.0), 2) if random.random() < 0.05 else 0.0
            pickup_order_fee = round(random.uniform(0.0, 1.5), 2) if transaction_type == "PICKUP" else 0.0
            other_merchant_fee = 0.0 # Could be for specific services
            bottle_deposit_fee = 0.0 # Not typically for bakeries
            bottle_deposit_fee_tax = 0.0

            description = f"Order Received Time: {transaction_utc_dt.isoformat(timespec='milliseconds')}Z Order Pickup Time: {transaction_utc_dt.isoformat(timespec='milliseconds')}Z"
            if final_order_status == "Canceled":
                description = f"Canceled Order - {description}"
            
            financial_details_data.append({
                "Timestamp UTC Time": transaction_utc_dt.strftime("%H:%M:%S"),
                "Timestamp UTC Date": transaction_utc_dt.strftime("%Y-%m-%d"),
                "Timestamp Local Time": transaction_local_dt.strftime("%H:%M:%S"),
                "Timestamp Local Date": transaction_local_dt.strftime("%Y-%m-%d"),
                "Payout Time": payout_date_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "Payout Date": payout_date_dt.strftime("%Y-%m-%d"),
                "Store ID": store_id,
                "Business ID": f"BUS{store_id}", # Example business ID
                "Store Name": store_info['name'],
                "Merchant Store ID": store_id,
                "Transaction Type": transaction_type,
                "Transaction ID": fake.uuid4(),
                "DoorDash Order ID": f'="{doordash_order_id}"', # As per example, include quotes
                "Merchant Delivery ID": f'="{merchant_delivery_id.replace("-", "")[:8].upper()}"' if transaction_type == "DELIVERY" else None,
                "External ID": None,
                "Description": description,
                "Final Order Status": final_order_status,
                "Currency": "USD",
                "Subtotal": f"{subtotal:.2f}",
                "Subtotal Tax Passed by DoorDash to Merchant": f"{subtotal_tax_passed:.2f}",
                "Pre-Adjusted Subtotal": f"{pre_adjusted_subtotal:.2f}",
                "Pre-Adjusted Tax Subtotal": f"{pre_adjusted_tax_subtotal:.2f}",
                "Commission": f"{commission:.2f}",
                "Commission Tax": f"{commission_tax:.2f}",
                "Marketing Fees": f"{marketing_fees:.2f}",
                "Marketing Fee Tax": f"{marketing_fee_tax:.2f}",
                "Snap Ebt Discount": f"{snap_ebt_discount:.2f}",
                "Credit": f"{credit_amount:.2f}",
                "Debit": f"{debit_amount:.2f}",
                "DoorDash Transaction ID": str(random.randint(1000000000, 9999999999)), # 10 digit ID
                "Payout ID": str(random.randint(100000000, 999999999)), # 9 digit ID
                "Subtotal Tax Remitted by DoorDash to Tax Authorities": f"{subtotal_tax_passed:.2f}",
                "Subtotal for tax": f"{subtotal:.2f}",
                "Doordash funded subtotal discount amount": f"{round(subtotal * random.uniform(0.0, 0.05), 2):.2f}" if random.random() < 0.1 else "0.00",
                "Merchant funded subtotal discount amount": f"{round(subtotal * random.uniform(0.0, 0.03), 2):.2f}" if random.random() < 0.05 else "0.00",
                "Error Charge": f"{error_charge:.2f}",
                "Adjustment": f"{adjustment:.2f}",
                "Pickup Order Fee": f"{pickup_order_fee:.2f}",
                "Other Merchant Fee": f"{other_merchant_fee:.2f}",
                "Bottle Deposit Fee": f"{bottle_deposit_fee:.2f}",
                "Bottle Deposit Fee Tax": f"{bottle_deposit_fee_tax:.2f}"
            })
            doordash_order_id_counter += 1
        current_date_for_transactions += timedelta(days=1)


    # DoorDash - Payout Summary (Weekly aggregation)
    
    # Convert financial_details_data to DataFrame for easier aggregation
    df_financial = pd.DataFrame(financial_details_data)
    df_financial['Subtotal_num'] = df_financial['Subtotal'].astype(float)
    df_financial['Subtotal Tax Passed by DoorDash to Merchant_num'] = df_financial['Subtotal Tax Passed by DoorDash to Merchant'].astype(float)
    df_financial['Commission_num'] = df_financial['Commission'].astype(float)
    df_financial['Commission Tax_num'] = df_financial['Commission Tax'].astype(float)
    df_financial['Marketing Fees_num'] = df_financial['Marketing Fees'].astype(float)
    df_financial['Marketing Fee Tax_num'] = df_financial['Marketing Fee Tax'].astype(float)
    df_financial['Snap Ebt Discount_num'] = df_financial['Snap Ebt Discount'].astype(float)
    df_financial['Error Charge_num'] = df_financial['Error Charge'].astype(float)
    df_financial['Adjustment_num'] = df_financial['Adjustment'].astype(float)
    df_financial['Doordash funded subtotal discount amount_num'] = df_financial['Doordash funded subtotal discount amount'].astype(float)
    df_financial['Merchant funded subtotal discount amount_num'] = df_financial['Merchant funded subtotal discount amount'].astype(float)
    df_financial['Subtotal Tax Remitted by DoorDash to Tax Authorities_num'] = df_financial['Subtotal Tax Remitted by DoorDash to Tax Authorities'].astype(float)
    df_financial['Pickup Order Fee_num'] = df_financial['Pickup Order Fee'].astype(float)

    # Convert timestamp columns to datetime objects for grouping
    df_financial['Timestamp Local Date_dt'] = pd.to_datetime(df_financial['Timestamp Local Date'])
    df_financial['Timestamp UTC Date_dt'] = pd.to_datetime(df_financial['Timestamp UTC Date'])
    
    # Group by week for payout summary
    # Define a custom week start to ensure consistent payout weeks
    def get_payout_week(date_col):
        # Adjust to start week on Monday
        return date_col - pd.to_timedelta(date_col.dt.dayofweek, unit='D')

    df_financial['Payout_Week_Local_Start'] = get_payout_week(df_financial['Timestamp Local Date_dt'])

    payout_groups = df_financial.groupby('Payout_Week_Local_Start')

    payout_id_counter = 1
    for week_start_local, group in payout_groups:
        subtotal_agg = group['Subtotal_num'].sum()
        subtotal_tax_passed_agg = group['Subtotal Tax Passed by DoorDash to Merchant_num'].sum()
        commission_agg = group['Commission_num'].sum()
        commission_tax_agg = group['Commission Tax_num'].sum()
        marketing_fees_agg = group['Marketing Fees_num'].sum()
        marketing_fee_tax_agg = group['Marketing Fee Tax_num'].sum()
        snap_ebt_discount_agg = group['Snap Ebt Discount_num'].sum()
        error_charges_agg = group['Error Charge_num'].sum()
        adjustments_agg = group['Adjustment_num'].sum()
        doordash_funded_discount_agg = group['Doordash funded subtotal discount amount_num'].sum()
        merchant_funded_discount_agg = group['Merchant funded subtotal discount amount_num'].sum()
        pickup_order_fee_agg = group['Pickup Order Fee_num'].sum()
        
        # Calculate Total Before Adjustments: This can be complex, often (Subtotal + Subtotal Tax - Discounts)
        total_before_adjustments = subtotal_agg + subtotal_tax_passed_agg - doordash_funded_discount_agg - merchant_funded_discount_agg

        # Net Payout calculation based on DoorDash's general model
        net_payout = total_before_adjustments - commission_agg - commission_tax_agg - marketing_fees_agg - marketing_fee_tax_agg - snap_ebt_discount_agg - error_charges_agg + adjustments_agg - pickup_order_fee_agg

        transactions_start_local_date = group['Timestamp Local Date_dt'].min().strftime("%Y-%m-%d")
        transactions_end_local_date = group['Timestamp Local Date_dt'].max().strftime("%Y-%m-%d")
        transactions_start_utc_date = group['Timestamp UTC Date_dt'].min().strftime("%Y-%m-%d")
        transactions_end_utc_date = group['Timestamp UTC Date_dt'].max().strftime("%Y-%m-%d")
        
        payout_date = (week_start_local + timedelta(days=random.randint(7,10))).strftime("%Y-%m-%d") # Payout typically few days after week end

        payout_summary_data.append({
            "Store ID": store_id,
            "Store Name": store_info['name'],
            "Business ID": f"BUS{store_id}",
            "Merchant Store ID": store_id,
            "Payout Date": payout_date,
            "Currency": "USD",
            "Subtotal": f"{subtotal_agg:.2f}",
            "Subtotal Tax Passed by DoorDash to Merchant": f"{subtotal_tax_passed_agg:.2f}",
            "Commission": f"{commission_agg:.2f}",
            "Commission Tax": f"{commission_tax_agg:.2f}",
            "Drive Charge": "$0.00", # Specific to DoorDash Drive, usually a fixed fee, setting to zero for generic bakery
            "Marketing Fees": f"{marketing_fees_agg:.2f}",
            "Marketing Fee Tax": f"{marketing_fee_tax_agg:.2f}",
            "Snap Ebt Discount": f"{snap_ebt_discount_agg:.2f}",
            "Error Charges": f"{error_charges_agg:.2f}",
            "Adjustments": f"{adjustments_agg:.2f}",
            "Total Before Adjustments": f"{total_before_adjustments:.2f}",
            "Net Payout": f"{net_payout:.2f}",
            "Transactions Start Local Date": transactions_start_local_date,
            "Transactions End Local Date": transactions_end_local_date,
            "Transactions Start UTC Date": transactions_start_utc_date,
            "Transactions End UTC Date": transactions_end_utc_date,
            "Payout ID": str(random.randint(100000000, 999999999)) + str(payout_id_counter), # Unique ID
            "Payout Status": "PAID",
            "Subtotal Tax Remitted by DoorDash to Tax Authorities": f"{group['Subtotal Tax Remitted by DoorDash to Tax Authorities_num'].sum():.2f}",
            "Printer Fee": "$0.00", # Assuming no printer fee
            "Tablet Fee": "$0.00" # Assuming no tablet fee
        })
        payout_id_counter += 1

    # Saving to CSV
    pd.DataFrame(financial_details_data).to_csv(f"doordash_financial_details_{store_id}.csv", index=False)
    pd.DataFrame(payout_summary_data).to_csv(f"doordash_payout_summary_{store_id}.csv", index=False)
    print(f"Finished DoorDash data for {store_info['name']}.")




# Generating Data Loop 

if __name__ == "__main__":
    for store_id, store_info in STORE_LOCATIONS.items():
        # Generate Snackpass Data
        generate_snackpass_data(store_id, store_info['name'], START_DATE, END_DATE)

        # Generate Uber Eats Data
        generate_uber_eats_data(store_id, store_info, START_DATE, END_DATE)

        # Generate DoorDash Data
        generate_doordash_data(store_id, store_info, START_DATE, END_DATE)

    print("\nAll synthetic data generation complete!")
    print(f"Data generated for {NUM_STORES} stores from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}.")
    print("CSV files saved in the current directory.")




import os
print(os.getcwd())




