from fastapi import FastAPI
from pydantic import BaseModel
import logging
from backend.schemas import ProductCreate, ProductResponse
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# product storage

product_list = {}
id_counter = 0

app = FastAPI()
logger.info(f'Running app version {app.version}')

@app.get('/')
def homepage():
    return {"msg" : "Homepage"}

@app.get('/api/products', response_model=[ProductResponse])
def get_products():
    return


@app.get('/api/product/{product_id}', response_model=ProductResponse)
def get_product(product_id: int):
    for product in product_list:
        if product.id == product_id:
            return product
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")

@app.post('/api/product')
def create_product(product : ProductCreate):
    new_id = id_counter + 1
    id_counter += 1
    product_list[new_id] = product
    return {"msg" : "created"}