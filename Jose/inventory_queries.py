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
from project3_ORM import Product, ProductPriceHistory, Customer, Payment, CustomerOrder, Delivery

from inventoryDB_enums import product_type_enum, payment_method_enum, delivery_status_enum

engine = create_engine("postgresql+psycopg2://jediknights:yoda123@homeoftopgs.ddns.net/jediknights")


class Base(DeclarativeBase):
    pass

with Session(engine) as session:

    records = session.query(Delivery.delivery_status,CustomerOrder.address,Customer.name,Payment.payment_method,Payment.total_price)\
        .join(CustomerOrder, Payment.payment_id == CustomerOrder.payment_id)\
        .join(Delivery, Delivery.order_id == CustomerOrder.order_id)\
        .join(Customer, Customer.customer_id == CustomerOrder.customer_id)\
        .where(Payment.total_price < 50.00)


    for record in records:
      #  print(record.name,"has paid with",record.payment_method,"and their order is currently",record.delivery_status)
        print(f"{record.name}'s order has been paid with {record.payment_method} their order is currenty {record.delivery_status}. Total cost: {record.total_price}")

#    select(Delivery,CustomerOrder,Customer,Payment).join(CustomerOrder, Delivery.order_id == CustomerOrder.order_id).join(Customer, Customer.customer_id == CustomerOrder.order_id)
#
#
#
#
#for ls in record:
#    print(ls.delivery_status, ls.address, ls.payment_method)
#


#
#    query = session.query(Customer.name, CustomerOrder.total_qty, Payment.payment_method)\
#     .join(CustomerOrder, CustomerOrder.customer_id == Customer.customer_id)\
#     .join(Payment, Payment.payment_id == CustomerOrder.payment_id)\
#     .group_by(Customer.name, CustomerOrder.total_qty, Payment.payment_method)\
#     .order_by(Customer.name.asc())
#
#
## execute the query and retrieve the results
#results = query.all()
#
#
## print the results
#for result in results:
#    print(result.name, result.total_qty, result.payment_method)