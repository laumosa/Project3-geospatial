from pymongo import MongoClient



def mongo_connect ():
    # This function connects to "Ironhack" MongoDB database and returns a collection named "companies".
    client = MongoClient("localhost:27017")
    db = client["Ironhack"]
    c = db.get_collection("companies")
    return c



