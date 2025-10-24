from pydantic import BaseModel

class NewUser(BaseModel):
    name: str
    email: str
    gender: str
    location: str

class NewProduct(BaseModel):
    name: str
    category: str
    price: float
    description: str

class ViewProduct(BaseModel):
    user_id: int
    product_id: int

class AddToCart(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1

class SearchProduct(BaseModel):
    user_id: int
    search_text: str
