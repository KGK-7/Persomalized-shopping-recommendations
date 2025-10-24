from sqlalchemy import Column, Integer, String, Float, ForeignKey, BLOB
from database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    gender = Column(String(10))
    location = Column(String(100))

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    category = Column(String(50))
    price = Column(Float)
    description = Column(String(500))

class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    embedding = Column(BLOB)

class UserView(Base):
    __tablename__ = "user_views"
    view_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

class UserCart(Base):
    __tablename__ = "user_cart"
    cart_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer, default=1)

class UserSearch(Base):
    __tablename__ = "user_searches"
    search_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    search_text = Column(String(255))
