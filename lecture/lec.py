from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field

import databases
import sqlalchemy

"""
>>> pip install sqlalchemy
>>> pip install databases[aiosqlite]
"""


app = FastAPI(__name__)


database_url = "sqlite:///my_database.db"
database = databases.Database(database_url)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(database_url)
metadata.create_all()



class  Item(BaseModel):
    name: str = Field(..., title="name", max_length=10)
    price: float
    offer: bool = None

class User(BaseModel):
    user_name: str
    full_name: str = Field(default= "noone")

class Order(BaseModel):
    items: List[Item]
    user: User

@app.post("/items")
async def create_file(items: Item):
    return {"item": items}