from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Product, UserView, UserCart, UserSearch
from schemas import *
from crud import add_user, add_product, save_embedding, load_all_embeddings
from recommender import compute_embedding, get_content_based_recommendations, get_cart_based_recommendations, get_search_based_recommendations, apriori_top_picks
import pandas as pd

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/add_user")
def api_add_user(data: NewUser):
    db = SessionLocal()
    user = User(name=data.name, email=data.email, gender=data.gender, location=data.location)
    user = add_user(db, user)
    db.close()
    return {"message": "User added", "user_id": user.user_id}

@app.post("/add_product")
def api_add_product(data: NewProduct):
    db = SessionLocal()
    product = Product(
        name=data.name, 
        category=data.category, 
        price=data.price, 
        description=data.description
    )
    product = add_product(db, product)
    embedding = compute_embedding(data.description, convert_to_numpy=True)
    save_embedding(db, product.product_id, embedding)

    db.close()
    return {"message": "Product added", "product_id": product.product_id}


@app.post("/view_product")
def api_view_product(data: ViewProduct):
    db = SessionLocal()
    db.add(UserView(user_id=data.user_id, product_id=data.product_id))
    db.commit()
    
    product_ids, embeddings = load_all_embeddings()
    db_product = db.query(Product).filter(Product.product_id==data.product_id).first()
    user_embedding = compute_embedding(db_product.description)
    recommended_ids = get_content_based_recommendations(user_embedding, embeddings, product_ids)
    recommended_products = db.query(Product).filter(Product.product_id.in_(recommended_ids)).all()
    db.close()
    
    return {"recommended_products": [{"id": p.product_id, "name": p.name} for p in recommended_products]}

@app.post("/add_to_cart")
def api_add_to_cart(data: AddToCart):
    db = SessionLocal()
    db.add(UserCart(user_id=data.user_id, product_id=data.product_id, quantity=data.quantity))
    db.commit()
    recommendations = get_cart_based_recommendations(db, data.user_id, engine)
    db.close()
    return {"cart_recommendations": recommendations}

@app.post("/search_product")
def api_search_product(data: SearchProduct):
    db = SessionLocal()
    db.add(UserSearch(user_id=data.user_id, search_text=data.search_text))
    db.commit()

    product_ids, embeddings = load_all_embeddings()
    results = get_search_based_recommendations(data.search_text, product_ids, embeddings, db)
    db.close()
    return {"search_results": results}

@app.get("/top_picks")
def api_top_picks():
    db = SessionLocal()
    user_cart_df = pd.read_sql("SELECT user_id, product_id FROM user_cart", engine)
    results = apriori_top_picks(user_cart_df, db)
    db.close()
    return {"top_picks": results}
