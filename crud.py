from sqlalchemy.orm import Session
from models import User, Product, ProductEmbedding, UserView, UserCart, UserSearch
import pickle
import numpy as np
from database import SessionLocal 

def add_user(db: Session, user):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def add_product(db: Session, product):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def save_embedding(db: Session, product_id, embedding):
    db_embedding = ProductEmbedding(
        product_id=product_id,
        embedding=pickle.dumps(embedding)
    )
    db.add(db_embedding)
    db.commit()

def load_all_embeddings():
    db = SessionLocal()
    rows = db.query(ProductEmbedding).all()
    products = []
    embeddings = []
    for row in rows:
        products.append(row.product_id)
        emb = pickle.loads(row.embedding)
        # flatten in case it is 2D [[...]]
        if len(emb.shape) > 1:
            emb = emb.flatten()
        embeddings.append(emb)
    db.close()
    return products, np.array(embeddings)

