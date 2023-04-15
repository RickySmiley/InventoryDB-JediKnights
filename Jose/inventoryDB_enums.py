from sqlalchemy import Enum

product_type_enum = Enum(
    'Apparel and accessories',
    'Electronics and technology',
    'Home and garden',
    'Health and beauty',
    'Food and beverage',
    'Sports and outdoors',
    'Toys and games',
    'Automotive and industrial',
    'Office and school supplies',
    'Pet supplies',
    name='product_type_enum'
)

payment_method_enum = Enum(
    'Credit Card',
    'PayPal',
    'Venmo',
    'Apple Pay',
    'Debit Card',
    'Google Pay',
    name='payment_method_enum'
)

delivery_status_enum = Enum(
    'Order_placed',
    'Shipped',
    'In-transit',
    'Delivered',
    name='delivery_status_enum'
)
