from typing import List
from typing import Optional
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
        return f"Product(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

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


class Customer(Base):
    __tablename__ = 'customer'
    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    carts: Mapped["Cart"] = relationship(back_populates="customer", cascade="all, delete-orphan")
    customer_order: Mapped["CustomerOrder"] = relationship(back_populates="customer")


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
    customer: Mapped[Customer] = relationship(back_populates='customer_order')
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
    customer: Mapped[Customer] = relationship("Customer", back_populates='carts')


# creates tables only if they don't exist
Base.metadata.create_all(engine, checkfirst=True)
with Session(engine) as session:
    products = [

        Product(product_id='P001', name='Apple', description='Fresh apples from local farm', product_type='Food and beverage', qty=50, price=0.99, pending_qty=0),
        Product(product_id='P002', name='Orange', description='Juicy oranges from California', product_type='Food and beverage', qty=35, price=1.25, pending_qty=5),
        Product(product_id='P003', name='Banana', description='Ripe bananas from Ecuador', product_type='Food and beverage', qty=20, price=0.79, pending_qty=2),
        Product(product_id='P004', name='Mango', description='Sweet mangoes from India', product_type='Food and beverage', qty=15, price=1.99, pending_qty=1),
        Product(product_id='P005', name='Pineapple', description='Fresh pineapples from Hawaii', product_type='Food and beverage', qty=10, price=2.99, pending_qty=0),
        Product(product_id='P006', name='Strawberry', description='Organic strawberries from local farm', product_type='Food and beverage', qty=25, price=3.99, pending_qty=3),
        Product(product_id='P007', name='Grapefruit', description='Tart grapefruits from Florida', product_type='Food and beverage', qty=30, price=1.49, pending_qty=6),
        Product(product_id='P008', name='Kiwi', description='Juicy kiwis from New Zealand', product_type='Food and beverage', qty=40, price=0.99, pending_qty=4),
        Product(product_id='P009', name='Papaya', description='Ripe papayas from Mexico', product_type='Food and beverage', qty=15, price=2.49, pending_qty=2),
        Product(product_id='P010', name='Watermelon', description='Sweet watermelons from Georgia', product_type='Food and beverage', qty=5, price=4.99, pending_qty=0),

    ]
    session.add_all(products)
    session.commit()



