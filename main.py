from http.client import HTTPException
from typing import List

from fastapi import FastAPI, status, HTTPException
from pydantic.main import BaseModel

import models
from database import SessionLocal

app = FastAPI()

db = SessionLocal()


@app.get('/')
def index():
    return {"greeting", "Heloo World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


class Item(BaseModel):  # serializer
    id: int
    name: str
    description: str
    price: int
    on_offer: bool

    class Config:
        orm_mode = True


@app.get('/items', response_model=List[Item], status_code=200)
def get_all_items():
    items = db.query(models.Item).all()
    return items


@app.post('/items', response_model=Item,
          status_code=status.HTTP_201_CREATED)
def create_an_item(item: Item):
    db_item = db.query(models.Item).filter(models.Item.name == item.name).first()

    if db_item is not None:
        raise HTTPException(detail="Item already exists")

    new_item = models.Item(
        name=item.name,
        price=item.price,
        description=item.description,
        on_offer=item.on_offer
    )

    db.add(new_item)
    db.commit()

    return new_item


@app.get('/item/{item_id}', response_model=Item, status_code=status.HTTP_200_OK)
def get_an_item(item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")

    return item


@app.put('/item/{item_id}', response_model=Item, status_code=status.HTTP_200_OK)
def update_an_item(item_id: int, item: Item):
    item_to_update = db.query(models.Item).filter(models.Item.id == item_id).first()

    if item_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")

    item_to_update.name = item.name
    item_to_update.price = item.price
    item_to_update.description = item.description
    item_to_update.on_offer = item.on_offer

    db.commit()
    return item_to_update


@app.delete('/item/{item_id}')
def delete_item(item_id: int):
    item_to_delete = db.query(models.Item).filter(models.Item.id == item_id).first()

    if item_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource Not Found")

    db.delete(item_to_delete)
    db.commit()

    return item_to_delete