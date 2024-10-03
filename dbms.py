from pymongo import MongoClient

def db_init():
    global client, db, account, customers
    # MongoDB에 연결 (로컬 MongoDB 서버가 실행 중이어야 함)
    client = MongoClient('mongodb://211.226.57.173:27017/')

    # 테스트용 데이터베이스 및 컬렉션 설정
    db = client['gptApp']
    account = db['aicafe_web']
    customers = db['customers']
    #account.drop()
    #customers.drop()
    # Ensure unique index on 'id' field
    account.create_index("id", unique=True)
    customers.create_index([("site_id", 1), ("platform", 1)], unique=True)

def build_account() :
    # 1. 데이터 삽입
    # Insert five records with fields [id, password, phone]
    documents = [
        {"id": "c", "password": "c", "phone": ""},
        {"id": "cafe2", "password": "cafe2", "phone": ""},
        {"id": "cafe3", "password": "cafe3", "phone": ""},
        {"id": "cafe4", "password": "cafe4", "phone": ""},
        {"id": "cafe5", "password": "cafe5", "phone": ""}
    ]
    inserted_ids = account.insert_many(documents).inserted_ids
    print(f"Inserted document IDs: {inserted_ids}")

    # 2. 데이터 조회
    print("Reading data:")
    for doc in account.find():
        print(doc)
def clear_account():
    # 1. 데이터 삭제
    # Delete all records
    result = account.delete_many({})
    print(f"Deleted {result.deleted_count} documents")

def clear_customers():
    # 1. 데이터 삭제
    # Delete all records
    result = customers.delete_many({})
    print(f"Deleted {result.deleted_count} documents")
    
def loginCheck(id, password):
    # 3. 데이터 조회 (조건부)
    # Find a record with the given id and password
    query = {"id": id, "password": password}
    result = account.find_one(query)
    print(result)
    if result:
        print(f"Login successful: {result}")
        return True
    else:
        print("Login failed")
        return False

def update_setttings(settings): #update or insert
    # 4. 데이터 수정
    # Update the phone number of the record with the given id
    for setting in settings:
        query = {"site_id": setting[0], "platform": setting[1]}
        print(f"Query: {query}")
        result = customers.find_one(query)
        if result :
            print(f"Updating {setting[0]}: {result}")            
            new_values = {"$set": {"id": setting[2], "password": setting[3], "shop_id": setting[4], "shop_name": setting[5]}}
            customers.update_one(query, new_values)
            #print(f"Updated document: {result}")
        else : # Insert a new record
            document = {"site_id": setting[0], "platform":setting[1],"id": setting[2], "password": setting[3], "shop_id": setting[4], "shop_name": setting[5]}
            inserted_id = customers.insert_one(document).inserted_id
            print(f"Inserted document IDs: {inserted_id}")
    print("Settings updated")

def get_settings(id):
    # 4. 데이터 조회 (조건부)
    # Find a record with the given id
    query = {"site_id": id}
    result = list(customers.find(query))
    print(result)
    if result:
        print(f"Settings found: {result}")
        return result
    else:
        print("Settings not found")
        return []

def display_all(table):
    # 4. 데이터 조회 (전체)
    print("Reading all data:")
    if(table == "account"):
        for doc in account.find():
            print(doc)
    else:
        for doc in customers.find():
            print(doc)
            
def close_db():
    # 5. MongoDB 연결 종료
    client.close()

if __name__ == "__main__":
    db_init()
    #build_account()
    #clear_account()
    #clear_customers()
    
    ret = loginCheck("c", "c")
    #if(ret) :
    #    update_setttings([["cafe_1", "site_1", "id_2", "password_1", "shop_1", "shop_name_1"]])
    get_settings("c")
    display_all('costomers')
    result = customers.find({"site_id": "c"})
    for doc in result:
        print(doc)
    close_db()