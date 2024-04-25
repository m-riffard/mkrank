from typing_extensions import TypedDict
import firebase_admin
from firebase_admin import db, credentials
from fastapi import FastAPI, HTTPException


class UserData(TypedDict):
    name: str
    rank: int
    nb_races: int


if not firebase_admin._apps:
    cred = credentials.Certificate("api/credentials.json")
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://mk-rank-default-rtdb.europe-west1.firebasedatabase.app/"
        },
    )

app = FastAPI()

users_ref = db.reference("/users")


@app.post("/users")
def create_user(name: str, rank: int, nb_races: int):
    new_user_ref = users_ref.child(name)
    new_user_ref.set({"rank": rank, "nb_races": nb_races})
    return {"name": name, "rank": rank, "nb_races": nb_races}


@app.get("/users")
def get_all_users():
    return users_ref.get()


@app.get("/users/{name}")
def get_user_by_name(name: str):
    user = users_ref.child(name).get()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/users/{name}")
def update_user(name: str, rank: int = None, nb_races: int = None):
    user_ref = users_ref.child(name)
    user_data = user_ref.get()

    if user_data:
        if rank is not None:
            user_ref.update({"rank": rank})
            user_data["rank"] = rank

        if nb_races is not None:
            user_ref.update({"nb_races": nb_races})
            user_data["nb_races"] = nb_races

        return user_data

    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{name}")
def delete_user(name: str):
    user_ref = users_ref.child(name)
    user_data = user_ref.get()

    if user_data:
        user_ref.delete()
        return {"message": "User deleted"}

    raise HTTPException(status_code=404, detail="User not found")
