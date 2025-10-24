from database import SessionLocal
from models import Product, ProductEmbedding
from crud import save_embedding
from recommender import compute_embedding

db = SessionLocal()
products = db.query(Product).all()

for product in products:
    exists = db.query(ProductEmbedding).filter_by(product_id=product.product_id).first()
    if not exists:
        embedding = compute_embedding(product.description)
        save_embedding(db, product.product_id, embedding)
        print(f"Embedding created for product_id: {product.product_id}")

db.close()
print("All embeddings generated successfully")
