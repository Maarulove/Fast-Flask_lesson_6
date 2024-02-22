from fastapi import FastAPI
import sqlalchemy
from pydantic import Field, BaseModel
from typing import List, Literal
import databases
from time import time




"""
Объедините студентов в команды по 2-5 человек в сессионных залах.

Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: 
товары, заказы и пользователи.
— Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
— Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
— Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.
• Таблица пользователей должна содержать следующие поля: 
            id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
• Таблица заказов должна содержать следующие поля:
            id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
• Таблица товаров должна содержать следующие поля:
            id (PRIMARY KEY), название, описание и цена.

Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.
Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.

"""

app = FastAPI()

class Goods(BaseModel):
    name: str
    description: str 
    price: float
class Goods_id(Goods):
    id: int

class User(BaseModel):
    name: str
    surname: str
    email: str
    password: str
class User_id(User):
    id: int

class Offers(BaseModel):
    user_id: int
    goods_id: int
    date: str
    status: Literal["In stock", "Out of stock"]
class Offers_id(Offers):
    id: int


app = FastAPI()
database_url = "sqlite:///my_database.db"
database = databases.Database(database_url)
metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(30)),
    sqlalchemy.Column("surname", sqlalchemy.String(30)),
    sqlalchemy.Column("email", sqlalchemy.String(70)),
    sqlalchemy.Column("password", sqlalchemy.String(50))
)

goods = sqlalchemy.Table(
    "goods",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(70)),
    sqlalchemy.Column("description", sqlalchemy.String()),
    sqlalchemy.Column("price", sqlalchemy.Float)

)

offers = sqlalchemy.Table(
    "offers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("goods_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("goods.id")),
    sqlalchemy.Column("date", sqlalchemy.String()),
    sqlalchemy.Column("status", sqlalchemy.String()))

engine = sqlalchemy.create_engine(database_url, connect_args={'check_same_thread': False})
metadata.create_all(engine)

@app.on_event("startup")
async def start_up():
    await database.connect()
@app.on_event("shutdown")
async def shut_down():
    await database.disconnect() 


## create post fror each class
@app.post("/create-user")
async def create_user(user: User):
    query = users.insert().values(**user.dict())
    last = await database.execute(query)
    return {**user.dict(), "id": last}

@app.post("/create-goods")
async def create_goods(user: Goods):
    query = goods.insert().values(**user.dict())
    last = await database.execute(query)
    return {**user.dict(), "id": last}

@app.post("/create-offers")
async def create_offers(user: Offers):
    query = offers.insert().values(**user.dict())
    last = await database.execute(query)
    return {**user.dict(), "id": last}



### get all data from specific class
@app.get("/goods", response_model=List[Goods])
async def get_goods_data(user: Goods):
    query = goods.select()
    return await database.execute(query)

@app.get("/offers", response_model=List[Offers])
async def get_offers_data(user: Offers):
    query = offers.select()
    return await database.execute(query)

@app.get("/users", response_model=List[User])
async def get_user_data(user: User):
    query = users.select()
    return await database.execute(query)


# get specific data from specific table
@app.get("/users{user-id}", response_model=User)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return database.fetch_all(query)

@app.get("/offer{offer-id}", response_model=Offers)
async def get_offer(user_id: int):
    query = offers.select().where(users.c.id == user_id)
    return database.fetch_all(query)

@app.get("/goods{goods-id}", response_model=Goods)
async def get_goods(user_id: int):
    query = goods.select().where(users.c.id == user_id)
    return database.fetch_all(query)


# Update the date from specific table

@app.put("/offer/{offer-id}")
async def update_offers(offer_id: int, new_user: Offers_id):
    query = offers.update().where(offers.c.id == offer_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": offer_id}
    
@app.put("/goods/{goods-id}")
async def update_goods(goods_id: int, new_user: Goods_id):
    query = goods.update().where(goods.c.id == goods_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": goods_id}

@app.put("/users/{user-id}")
async def update_users(user_id: int, new_user: User_id):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


# delete tables
@app.delete("/users/{user-id}")
async def delete_user(user_id:int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": f"User {user_id} deleted"}

@app.delete("/goods/{goods-id}")
async def delete_goods(goods_id:int):
    query = goods.delete().where(goods.c.id == goods_id)
    await database.execute(query)
    return {"message": f"User {goods_id} deleted"}

@app.delete("/offer/{offer-id}")
async def delete_offer(offer_id:int):
    query = offers.delete().where(offers.c.id == offer_id)
    await database.execute(query)
    return {"message": f"User {offer_id} deleted"}