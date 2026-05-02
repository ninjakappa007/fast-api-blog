from fastapi import FastAPI
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price : float
    is_sale : bool | None = None


app = FastAPI()

@app.get('/')
def homepage():
    return {"msg" : "Homepage"}

@app.get('/product/{product_id}')
def get_product(product_id : int):
    return {"product_id" : product_id}

@app.put('/product/{product_id}')
def update_product(product_id : int, product : Product):
    return {"product_name" : product.name, "product_id" : product_id}