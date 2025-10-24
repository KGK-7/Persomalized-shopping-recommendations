from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from models import Product
import pickle

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_embedding(text):
    return model.encode([text])

def get_content_based_recommendations(user_embedding, embeddings, product_ids, top_n=5):
    if len(embeddings) == 0:
        return []
    sim_scores = cosine_similarity(user_embedding, np.array(embeddings))[0]
    top_idx = sim_scores.argsort()[::-1][:top_n]
    return [product_ids[i] for i in top_idx]

def get_cart_based_recommendations(db, user_id, engine):
    cart_products = pd.read_sql(f"""
        SELECT p.* FROM products p
        JOIN user_cart c ON p.product_id=c.product_id
        WHERE c.user_id={user_id}
    """, engine)

    if not cart_products.empty:
        last_product = cart_products.iloc[-1]
        category = last_product["category"]
        price = last_product["price"]
        recommendations = pd.read_sql(f"""
            SELECT * FROM products
            WHERE category='{category}'
              AND product_id NOT IN ({','.join(map(str, cart_products['product_id'].tolist()))})
              AND price BETWEEN {price*0.8} AND {price*1.2}
            LIMIT 5
        """, engine)
        return recommendations[["product_id", "name", "category"]].to_dict(orient="records")
    return []

def get_search_based_recommendations(search_text, product_ids, embeddings, db, top_n=5):
    if not product_ids:
        return []
    search_emb = compute_embedding(search_text)
    recommended_ids = get_content_based_recommendations(search_emb, embeddings, product_ids, top_n)
    recommended_products = db.query(Product).filter(Product.product_id.in_(recommended_ids)).all()
    return [{"id": p.product_id, "name": p.name} for p in recommended_products]

def apriori_top_picks(user_cart_df, db):
    if user_cart_df.empty:
        return []
    basket = pd.crosstab(user_cart_df["user_id"], user_cart_df["product_id"])
    frequent_items = apriori(basket, min_support=0.2, use_colnames=True)
    rules = association_rules(frequent_items, metric='lift', min_threshold=1.1)
    top_products = rules["consequents"].explode().unique().tolist()
    top_products_info = db.query(Product).filter(Product.product_id.in_(top_products)).all()
    return [{"id": p.product_id, "name": p.name} for p in top_products_info]
