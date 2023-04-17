from typing import List
from typing import Optional
from datetime import date
import psycopg2
from sqlalchemy import ForeignKey, Numeric, CheckConstraint, Date, func
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from pprint import pprint

from inventoryDB_enums import product_type_enum, payment_method_enum, delivery_status_enum

# Credentials to my (Sam Bernau) personal linux server hosting a postgresql-13 database
engine = create_engine("postgresql+psycopg2://jediknights:yoda123@homeoftopgs.ddns.net/jediknights")


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'product'
    product_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(product_type_enum, nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    pending_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pph: Mapped["ProductPriceHistory"] = relationship()
    customer_order: Mapped["CustomerOrder"] = relationship()

    def __repr__(self) -> str:  # represents the object as a string
        return f"Product(product_id={self.product_id!r}, name={self.name!r}, price={self.price!r}, pending_qty={self.pending_qty!r})"

    __table_args__ = (
        CheckConstraint('qty >= 0'),
        CheckConstraint('price >= 0.0'),
        CheckConstraint('pending_qty >= 0')
    )


class ProductPriceHistory(Base):
    __tablename__ = 'product_price_history'
    price_history_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    previous_price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False, info={
        "check_constraints": ["previous_qty >= 0"]})
    date_changed: Mapped[Date] = mapped_column(Date, default=func.now(), nullable=False)
    product_id: Mapped[str] = mapped_column(String(50), ForeignKey('product.product_id'), nullable=False)
    product: Mapped["Product"] = relationship(back_populates='pph')
    def __repr__(self) -> str:
        return f"ProductPriceHisory(previous_price={self.previous_price!r})"


class Customer(Base):
    __tablename__ = 'customer'
    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    carts: Mapped["Cart"] = relationship(back_populates="customer", cascade="all, delete-orphan")
    customerorder: Mapped["CustomerOrder"] = relationship("CustomerOrder",back_populates="customer")

    def __repr__(self) -> str:
        return f"Customer(name={self.name!r})"

class Payment(Base):
    __tablename__ = 'payment'
    payment_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    payment_method: Mapped[str] = mapped_column(payment_method_enum, nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False, info={
        "check_constraints": ["total_price >= 0.0"]})



class CustomerOrder(Base):
    __tablename__ = 'customer_order'
    order_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    date: Mapped[Date] = mapped_column(Date, default=func.now(), nullable=False)
    total_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0, info={
        "check_constraints": ["total_qty >= 0"]})
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(50), ForeignKey('customer.customer_id'), nullable=False)
    product_id: Mapped[str] = mapped_column(String(50), ForeignKey('product.product_id'), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(50), ForeignKey('payment.payment_id'), nullable=False)
    customer: Mapped[Customer] = relationship("Customer", back_populates="customerorder")
    product: Mapped[Product] = relationship(back_populates='customer_order')
    payment: Mapped[Payment] = relationship()
    delivery: Mapped["Delivery"] = relationship(back_populates='customer_order')


class Delivery(Base):
    __tablename__ = 'delivery'
    delivery_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    delivery_date: Mapped[Date] = mapped_column(Date, default=func.now(), nullable=False)
    delivery_type: Mapped[str] = mapped_column(product_type_enum, nullable=False)
    delivery_status: Mapped[str] = mapped_column(delivery_status_enum, nullable=False)
    order_id: Mapped[str] = mapped_column(String(50), ForeignKey('customer_order.order_id'))
    customer_order: Mapped["CustomerOrder"] = relationship(back_populates='delivery')


class Cart(Base):
    __tablename__ = 'cart'
    customer_id: Mapped[Customer] = mapped_column(String(50), ForeignKey('customer.customer_id'), primary_key=True, nullable=False)
    product_id: Mapped[Product] = mapped_column(String(50), ForeignKey('product.product_id'), primary_key=True, nullable=False)
    customer: Mapped[List["Customer"]] = relationship("Customer", back_populates='carts')


# creates tables only if they don't exist
Base.metadata.create_all(engine, checkfirst=True)

#with Session(engine) as session:

#   customers = [
#       Customer(customer_id='C001', name='Jane Smith', phone_number='555-1234', address='123 Main St',
#                email='janesmith@example.com', password='password123'),
#       Customer(customer_id='C002', name='Mary Johnson', phone_number='555-5678', address='456 Elm St',
#                email='mary.johnson@example.com', password='password456'),
#       Customer(customer_id='C003', name='David Lee', phone_number='555-2468', address='789 Elm St',
#                email='david.lee@example.com', password='password789'),
#       Customer(customer_id='C004', name='Emily Brown', phone_number='555-3698', address='321 Maple St',
#                email='emily.brown@example.com', password='password101'),
#       Customer(customer_id='C005', name='Michael Davis', phone_number='555-9876', address='654 Pine St',
#                email='michael.davis@example.com', password='password202'),
#       Customer(customer_id='C006', name='Jessica Martinez', phone_number='555-1111', address='246 Cherry St',
#                email='jessica.martinez@example.com', password='password303'),
#       Customer(customer_id='C007', name='William Taylor', phone_number='555-2222', address='246 Oak St',
#                email='william.taylor@example.com', password='password404'),
#       Customer(customer_id='C008', name='Avery Mitchell', phone_number='555-3333', address='135 Maple Ave',
#                email='avery.mitchell@example.com', password='password505'),
#       Customer(customer_id='C009', name='Mason Anderson', phone_number='555-4444', address='279 Birch St',
#                email='mason.anderson@example.com', password='password606'),
#       Customer(customer_id='C010', name='Samantha Scott', phone_number='555-5555', address='975 Cedar Rd',
#                email='samantha.scott@example.com', password='password707'),
#       Customer(customer_id='C011', name='Daniel Wright', phone_number='555-6666', address='601 Maple St',
#                email='daniel.wright@example.com', password='password808'),
#       Customer(customer_id='C012', name='Olivia Adams', phone_number='555-7777', address='907 Pine St',
#                email='olivia.adams@example.com', password='password909'),
#       Customer(customer_id='C013', name='Noah Hall', phone_number='555-8888', address='714 Elm St',
#                email='noah.hall@example.com', password='password010'),
#       Customer(customer_id='C014', name='Isabella Garcia', phone_number='555-9999', address='423 Cedar St',
#                email='isabella.garcia@example.com', password='password121'),
#       Customer(customer_id='C015', name='Ethan Hernandez', phone_number='555-0000', address='1300 Maple St',
#                email='ethan.hernandez@example.com', password='password232'),
#   ]
#   session.add_all(customers)
#   session.commit()
#
#
#
#   orders = [
#           CustomerOrder(order_id='ORD001', date=date(2023, 3, 1), total_qty=2, address='123 Main St',
#                         customer_id='C001', product_id='P001', payment_id='PAY001'),
#           CustomerOrder(order_id='ORD002', date=date(2023, 3, 2), total_qty=1, address='456 Elm St',
#                         customer_id='C002', product_id='P002', payment_id='PAY002'),
#           CustomerOrder(order_id='ORD003', date=date(2023, 3, 3), total_qty=4, address='789 Elm St',
#                         customer_id='C003', product_id='P003', payment_id='PAY003'),
#           CustomerOrder(order_id='ORD004', date=date(2023, 3, 4), total_qty=3, address='321 Maple St',
#                         customer_id='C004', product_id='P004', payment_id='PAY004'),
#           CustomerOrder(order_id='ORD005', date=date(2023, 3, 5), total_qty=2, address='654 Pine St',
#                         customer_id='C005', product_id='P005', payment_id='PAY005'),
#           CustomerOrder(order_id='ORD006', date=date(2023, 3, 6), total_qty=5, address='246 Cherry St',
#                         customer_id='C006', product_id='P006', payment_id='PAY006'),
#           CustomerOrder(order_id='ORD007', date=date(2023, 3, 7), total_qty=1, address='246 Oak St',
#                         customer_id='C007', product_id='P007', payment_id='PAY007'),
#           CustomerOrder(order_id='ORD008', date=date(2023, 3, 8), total_qty=3, address='135 Maple Ave',
#                         customer_id='C008', product_id='P008', payment_id='PAY008'),
#           CustomerOrder(order_id='ORD009', date=date(2023, 3, 9), total_qty=2, address='279 Birch St',
#                         customer_id='C009', product_id='P009', payment_id='PAY009'),
#           CustomerOrder(order_id='ORD010', date=date(2023, 3, 10), total_qty=1, address='975 Cedar Rd',
#                         customer_id='C010', product_id='P010', payment_id='PAY010')
#   ]
#   session.add_all(orders)
#   session.commit()
#
#
#   products = [
#
#       Product(product_id='P001', name='Apple', description='Fresh apples from local farm',
#               product_type='Food and beverage', qty=50, price=0.99, pending_qty=0),
#       Product(product_id='P002', name='Orange', description='Juicy oranges from California',
#               product_type='Food and beverage', qty=35, price=1.25, pending_qty=5),
#       Product(product_id='P003', name='Banana', description='Ripe bananas from Ecuador',
#               product_type='Food and beverage', qty=20, price=0.79, pending_qty=2),
#       Product(product_id='P004', name='Mango', description='Sweet mangoes from India',
#               product_type='Food and beverage', qty=15, price=1.99, pending_qty=1),
#       Product(product_id='P005', name='Pineapple', description='Fresh pineapples from Hawaii',
#               product_type='Food and beverage', qty=10, price=2.99, pending_qty=0),
#       Product(product_id='P006', name='Strawberry', description='Organic strawberries from local farm',
#               product_type='Food and beverage', qty=25, price=3.99, pending_qty=3),
#       Product(product_id='P007', name='Grapefruit', description='Tart grapefruits from Florida',
#               product_type='Food and beverage', qty=30, price=1.49, pending_qty=6),
#       Product(product_id='P008', name='Kiwi', description='Juicy kiwis from New Zealand',
#               product_type='Food and beverage', qty=40, price=0.99, pending_qty=4),
#       Product(product_id='P009', name='Papaya', description='Ripe papayas from Mexico',
#               product_type='Food and beverage', qty=15, price=2.49, pending_qty=2),
#       Product(product_id='P010', name='Watermelon', description='Sweet watermelons from Georgia',
#               product_type='Food and beverage', qty=5, price=4.99, pending_qty=0),
#
#   ]
#   session.add_all(products)
#   session.commit()
#   deliveries = [
#
#       Delivery(delivery_id='D001', delivery_date='2022-03-21', delivery_type='Food and beverage',
#                delivery_status='Shipped', order_id='ORD001'),
#       Delivery(delivery_id='D002', delivery_date='2022-03-23', delivery_type='Food and beverage',
#                delivery_status='Delivered', order_id='ORD002'),
#       Delivery(delivery_id='D003', delivery_date='2022-03-24', delivery_type='Food and beverage',
#                delivery_status='In-transit', order_id='ORD003'),
#       Delivery(delivery_id='D004', delivery_date='2022-03-26', delivery_type='Food and beverage',
#                delivery_status='Shipped', order_id='ORD004'),
#       Delivery(delivery_id='D005', delivery_date='2022-03-27', delivery_type='Food and beverage',
#                delivery_status='Delivered', order_id='ORD005'),
#       Delivery(delivery_id='D006', delivery_date='2022-03-28', delivery_type='Food and beverage',
#                delivery_status='In-transit', order_id='ORD006'),
#       Delivery(delivery_id='D007', delivery_date='2022-03-30', delivery_type='Food and beverage',
#                delivery_status='Shipped', order_id='ORD007'),
#       Delivery(delivery_id='D008', delivery_date='2022-03-31', delivery_type='Food and beverage',
#                delivery_status='Delivered', order_id='ORD008'),
#       Delivery(delivery_id='D009', delivery_date='2022-04-02', delivery_type='Food and beverage',
#                delivery_status='In-transit', order_id='ORD009'),
#       Delivery(delivery_id='D010', delivery_date='2022-04-03', delivery_type='Food and beverage',
#                delivery_status='Shipped', order_id='ORD010'),
#       Delivery(delivery_id='D011', delivery_date='2022-03-20', delivery_type='Food and beverage',
#                delivery_status='Delivered', order_id='ORD001'),
#       Delivery(delivery_id='D012', delivery_date='2022-03-21', delivery_type='Food and beverage',
#                delivery_status='Shipped', order_id='ORD002'),
#
#   ]
#   session.add_all(deliveries)
#   session.commit()
#  history_price = [
#         ProductPriceHistory(price_history_id='PPH001', previous_price=29.99, date_changed='2022-03-15', product_id='P001'),
#         ProductPriceHistory(price_history_id='PPH002', previous_price=39.99, date_changed='2022-03-16', product_id='P002'),
#         ProductPriceHistory(price_history_id='PPH003', previous_price=19.99, date_changed='2022-03-17', product_id='P003'),
#         ProductPriceHistory(price_history_id='PPH004', previous_price=49.99, date_changed='2022-03-18', product_id='P004'),
#         ProductPriceHistory(price_history_id='PPH005', previous_price=9.99, date_changed='2022-03-19', product_id='P005'),
#         ProductPriceHistory(price_history_id='PPH006', previous_price=34.99, date_changed='2022-03-20', product_id='P006'),
#         ProductPriceHistory(price_history_id='PPH007', previous_price=89.99, date_changed='2022-03-21', product_id='P007'),
#         ProductPriceHistory(price_history_id='PPH008', previous_price=119.99, date_changed='2022-03-22', product_id='P008'),
#         ProductPriceHistory(price_history_id='PPH009', previous_price=7.99, date_changed='2022-03-23', product_id='P009'),
#         ProductPriceHistory(price_history_id='PPH010', previous_price=24.99, date_changed='2022-03-24', product_id='P010'),
#  ]
#  session.add_all(history_price)
#  session.commit()
# data = [
#          {'customer_id': 'C001', 'product_id': 'P001'},
#          {'customer_id': 'C001', 'product_id': 'P003'},
#          {'customer_id': 'C002', 'product_id': 'P002'},
#          {'customer_id': 'C003', 'product_id': 'P004'},
#          {'customer_id': 'C004', 'product_id': 'P006'},
#          {'customer_id': 'C004', 'product_id': 'P009'},
#          {'customer_id': 'C005', 'product_id': 'P005'},
#          {'customer_id': 'C005', 'product_id': 'P007'},
#          {'customer_id': 'C005', 'product_id': 'P008'},
#          {'customer_id': 'C006', 'product_id': 'P001'},
#          {'customer_id': 'C006', 'product_id': 'P002'},
#          {'customer_id': 'C007', 'product_id': 'P003'},
#          {'customer_id': 'C007', 'product_id': 'P004'},
#          {'customer_id': 'C008', 'product_id': 'P005'},
#          {'customer_id': 'C009', 'product_id': 'P006'},
#          {'customer_id': 'C009', 'product_id': 'P007'},
#          {'customer_id': 'C010', 'product_id': 'P008'},
#          {'customer_id': 'C011', 'product_id': 'P009'},
#          {'customer_id': 'C011', 'product_id': 'P010'},
#          {'customer_id': 'C012', 'product_id': 'P001'},
#          {'customer_id': 'C013', 'product_id': 'P002'},
#          {'customer_id': 'C014', 'product_id': 'P003'},
#          {'customer_id': 'C015', 'product_id': 'P004'},
#       ]
# session.add_all(data)
# session.commit()

