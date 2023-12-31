from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId

uri = "mongodb+srv://root2:doC123@myservercluster.7bw8olc.mongodb.net/?retryWrites=true&w=majority"


#uri = "mongodb://localhost:27017"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Mongo says DB connection successful")
except Exception as e:
    print(e)


stopandemic_DB = client.stopandemic

def setup_database():
    stopandemic_DB.drop_collection(stopandemic_DB.doctor)
    items_collection = stopandemic_DB.doctor
    for item in ['Nick', 'Paul', 'Rose']:
        items_collection.insert_one({"name":item})

def get_items(id=None):
    items_collection = stopandemic_DB.disease
    if id == None:
        items = items_collection.find({})
    else:
        items = items_collection.find({"_id":ObjectId(id)})
    items = list(items)
    for item in items:
        item["id"] = str(item["_id"])
    return items

def get_itemsDiseasePatient(disease_code):
    patients_collection = stopandemic_DB.patient
    patients_with_disease = patients_collection.aggregate([
        {
            "$match": {
                "disease_code": disease_code
            }
        },
        {
            "$lookup": {
                "from": "disease",
                "localField": "disease_code",
                "foreignField": "disease_code",
                "as": "patientDisease"
            }
        },
        {
            "$project": {
                "_id": 1,  # Exclude _id field
                "patient_fname": 1,  # Include patient_fname field
                "patient_sname":1,
                "patient_country":1
            }
        }
    ])
    
    return list(patients_with_disease)



def add_item(name):
    items_collection = stopandemic_DB.doctor
    items_collection.insert_one({"Name":name})

def add_Doctor_document(docCode,docName,surName,docCountry,patientCode):
    items_collection = stopandemic_DB.doctor
    items_collection.insert_one({"doctor_code":docCode,"doctor_fname":docName,"doctor_sname":surName,
                                 "doctor_country":docCountry,"patient_code":patientCode})   

def add_Patient_document(patCode,patName,pSurName,patCountry,patAge,patStatus,patTravel,
                         patDiseaseCode,patDocCode):
     items_collection = stopandemic_DB.patient
     items_collection.insert_one({"patient_code":patCode,"patient_fname":patName,
                                  "patient_sname":pSurName,"patient_country":patCountry,
                                  "patient_age":patAge,"status":patStatus,"travel_history":patTravel,
                         "disease_code":patDiseaseCode,"doctor_code":patDocCode})

def add_Disease_document(diseaseCode,diseaseName,description,medication,treatment):
    items_collection = stopandemic_DB.disease
    items_collection.insert_one({"disease_code":diseaseCode,"description":description,
                                 "disease_name":diseaseName,"drugs":medication,
                                 "treament":treatment})  


def delete_item(id):
    items_collection = stopandemic_DB.patient
    items_collection.delete_one({"_id":ObjectId(id)})

def get_items_patient(id=None):
    items_collection = stopandemic_DB.patient
    if id == None:
        items = items_collection.find({})
    else:
        items = items_collection.find({"_id":ObjectId(id)})
    items = list(items)
    for item in items:
        item["id"] = str(item["_id"])
    return items

def update_item(id, name):
    items_collection = stopandemic_DB.doctor
    where = {"_id": ObjectId(id)}
    updates = { "$set": { "Name": name } }
    items_collection.update_one(where, updates)

def update_Patient_document(id,patCode,patName,pSurName,patCountry,patAge,
                            patStatus,patTravel,patDiseaseCode,patDocCode):
    items_collection = stopandemic_DB.patient
    where = {"_id": ObjectId(id)}
    updates = { "$set": {"patient_code":patCode,"patient_fname": patName, "patient_sname":pSurName,
                         "patient_age":patAge, "patient_country":patCountry, "status":patStatus,
                         "travel_history":patTravel, "disease_code":patDiseaseCode,"doctor_code":patDocCode
                         }}
    items_collection.update_one(where, updates)

def searchItem(searchItem):
    patients_collection = stopandemic_DB.patient
    if "patient_fname_text" not in patients_collection.index_information():
        patients_collection.create_index([("patient_fname", "text")], name="patient_fname_text")

    result = patients_collection.aggregate([
        {
            "$search": {
                "index": "text",
                "text": {
                    "path": "patient_fname",
                    "query": searchItem
                },
                "sort": {
                    "patient_fname": 1
                }
            }
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "_id": 1,
                "patient_fname": 1,
                "patient_sname": 1
            }
        }
    ])

    return list(result)

    
def test_setup_database():
    print("testing setup_database()")
    setup_database()
    items = get_items()
    assert len(items) == 3
    descriptions = [item['Name'] for item in items]
    for description in ['Nick', 'Paul', 'Rose']:
        assert description in descriptions

def test_get_items():
    print("testing get_items()")
    setup_database()
    items = get_items()
    assert type(items) is list
    assert len(items) > 0
    for item in items:
        assert 'id' in item
        assert type(item['id']) is str
        assert 'Name' in item
        assert type(item['Name']) is str
    example_id = items[0]['id']
    example_description = items[0]['Name']
    items = get_items(example_id)
    assert len(items) == 1
    assert example_id == items[0]['id']
    assert example_description == items[0]['Name']

def test_add_item():
    print("testing add_item()")
    setup_database()
    items = get_items()
    original_length = len(items)
    add_item("licorice")
    items = get_items()
    assert len(items) == original_length + 1
    descriptions = [item['Name'] for item in items]
    assert "licorice" in descriptions


def test_delete_item():
    print("testing delete_item()")
    setup_database()
    items = get_items()
    original_length = len(items)
    deleted_description = items[1]['Name']
    deleted_id = items[1]['id']
    delete_item(deleted_id)
    items = get_items()
    assert len(items) == original_length - 1
    for item in items:
        assert item['id'] != deleted_id
        assert item['Name'] != deleted_description

def test_update_item():
    print("testing update_item()")
    setup_database()
    items = get_items()
    original_description = items[1]['Name']
    original_id = items[1]['id']
    update_item(original_id,"changeRose")
    items = get_items()
    found = False
    for item in items:
        if item['id'] == original_id:
            assert item['Name'] == "changeRose"
            found = True
    assert found


if __name__ == "__main__":
    test_setup_database()
    test_get_items()
    test_add_item()
    test_delete_item()
    test_update_item()

# def delete_item(id):
#     item = Item.select().where(Item.id == id).get()
#     item.delete_instance()

# def update_item(id, description):
#     # item = Item.select().where(Item.id == id).get()
#     # item.description = description
#     # item.save()
#     Item.update({Item.description: description}).where(Item.id == id).execute()

# # def test_update_item():
# #     print("testing update_item()")
# #     setup_database()
# #     items = get_items()
# #     original_description = items[1]['description']
# #     original_id = items[1]['id']
# #     update_item(original_id,"new-description")
# #     items = get_items()
# #     found = False
# #     for item in items:
# #         if item['id'] == original_id:
# #             assert item['description'] == "new-description"
# #             found = True
# #     assert found

# if __name__ == "__main__":
#     test_setup_database()
#     test_get_items()
#     # test_add_item()
#     # test_delete_item()
#     # test_update_item()
#     print("done.")