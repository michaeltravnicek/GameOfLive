from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/greet/{name}")
def greet(name: str, age: Optional[int] = None):
    greeting = f"Hello, {name}!"

    if age is not None:
        greeting += f" You are {age} years old."

    return {"message": greeting}


@app.post("/users/")
def create_user(user: User):
    return {"message": "User created successfully", "data": user.dict()}