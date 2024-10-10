from datetime import datetime, timedelta
from pymongo import MongoClient
import pandas as pd
from telegramT import *
MAX_POSTS = 100
MAX_POSTS_PER_DAY = 20
DELAY_ONE_LOOP = 10 #miniutes

class dbms:
    def __init__(self):
        # Replace the following values with your own credentials
        username = "admin"
        password = "Flash770!!"
        host = "211.226.57.173"  # Replace with your MongoDB server IP if remote
        port = 27017  # Default port for MongoDB
        database_name = "admin"
        auth_db = "admin"  # The authentication database, usually 'admin'

        # Connection URI
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database_name}?authSource={auth_db}"
        self.client = MongoClient(uri) 

        # 테스트용 데이터베이스 및 컬렉션 설정
        db = self.client['gptApp']
        self.account = db['aicafe_web']
        self.customers = db['customers']
        self.gptPosts = db['gptPosts']

        self.msg_count = {}
        #account.drop()
        #customers.drop()
        
    def build_account(self) :
        # 1. 데이터 삽입
        # Insert five records with fields [id, password, phone]
        self.account.drop()
        documents = [
            {"id": "pc_version", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "c", "password": "c", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe2", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe3", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe4", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe5", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe6", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe7", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe8", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0},
            {"id": "cafe9", "password": "aicafe139", "phone": "", "user_run" : True, "system_permission" : True, "post_num_today":0, "post_num_total":0}
        ]
        inserted_ids = self.account.insert_many(documents).inserted_ids
        print(f"Inserted document IDs: {inserted_ids}")
    def make_index (self):
        # Ensure unique index on 'id' field
        self.account.create_index("id", unique=True)
        self.customers.drop_indexes()
        self.customers.create_index([("platform", 1),("id", 1)], unique=True) #배민의 여러개정을 가진다.

    def build_gptPosts(self) :
        from datetime import datetime
        doc_sample = {"platform" :"baemin","site_id":"c","shop_id":"shop_1","shop_name":"shop_name_1",
                    "review":"_1","review_info":"post_info1","reply":"reply_1","reply_info":"info","date":datetime.now()}
        inserted_id = self.gptPosts.insert_one(doc_sample).inserted_id
        print(f"build_gptPosts, Inserted document IDs: {inserted_id}")
    
    def add_gptPosts(self,doc_list):
        #print(f"Adding documents: {doc_list}")
        inserted_ids = self.gptPosts.insert_many(doc_list).inserted_ids
        print(f"Inserted document IDs: {inserted_ids}")
        cnt = len(doc_list)
        try : 
            site_id = doc_list[0]["site_id"]
            account_doc = self.account.find_one({"id": site_id})
            print(f"Account: {account_doc.get('post_num_total', 0)}")
            self.account.update_one(
                {"id": doc_list[0]["site_id"]},
                {"$inc": {"post_num_total": cnt}}
            )
            
            total = account_doc.get("post_num_total", 0)+cnt
            if(site_id not in self.msg_count):
                self.msg_count[site_id] = 0
            if(int(total/10) != int(self.msg_count[site_id]/10)): #자리수가 바뀌면 메시지 전송
                asyncio.run(tele_send(f"site_id {site_id} post count {total}"))            
            self.msg_count[site_id] = total

            if (total) > MAX_POSTS:
                print(f"Account with site_id {account_doc['id']} has more than 100 posts.")
                self.account.update_one(
                    {"id": account_doc["id"]},
                    {"$set": {"system_permission": False}}
                )
                asyncio.run(tele_send(f"site_id {site_id} STOP BY MAX {total}"))            
        except Exception as e:
            print(f"DB ERROR add_gptPosts: {e}")
        return
 


    def get_gptPosts(self,id):
        seven_days_ago = datetime.now() - timedelta(days=7)
        #query = {"site_id": id, "date": {"$gte": seven_days_ago}}        
        query = {"site_id": id}        
        total = self.gptPosts.count_documents(query)
        print(f"Number of documents matching the query: {total}")
        if(total == 0) :
            return None,total
            
        result = self.gptPosts.find(query).sort("date", -1).limit(20)
        print(f"Reading data: {result}")   

        df = pd.DataFrame(list(result))
        if(df.empty):
            print("No data found")
            return df
        df = df.drop(columns=['_id','site_id','shop_id'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M') 

        #print(df)   
        return df,total
    
    def get_customers(self, platform):
        #{"site_id": setting[0], "platform": setting[1], "id": setting[2], "password": setting[3], "shop_id": setting[4], "shop_name": setting[5]}
        #platform별 id/password를 가져온다. 단 account정보에서 system_permission과 user_run이 true인 것만 가져온다.
        query = {"platform": platform}
        result = self.customers.find(query) 
                
        # Check if system_permission and user_run are true for the given site_id 
        customers_allowed = []
        for customer in result:
            print(f"Customer: {customer}")
            account = self.account.find_one({"id": customer["site_id"], "system_permission": True, "user_run": True})   
            if(account != None):
                customers_allowed.append(customer)
        
        df = pd.DataFrame(customers_allowed)
        if(df.empty):
            print("No data found")
            return df
        print(df)   
        return df
        
    def clear_account(self):
        # 1. 데이터 삭제
        # Delete all records
        result = self.account.delete_many({})
        print(f"Deleted {result.deleted_count} documents")

    def clear_customers(self):
        # 1. 데이터 삭제
        # Delete all records
        result = self.customers.delete_many({})
        print(f"Deleted {result.deleted_count} documents")
        
    def loginCheck(self,id, password):
        # 3. 데이터 조회 (조건부)
        # Find a record with the given id and password
        query = {"id": id, "password": password}
        result = self.account.find_one(query)
        print(result)
        if result:
            print(f"Login successful: {result}")
            return True
        else:
            print("Login failed")

            return False

    def add_customer(self,setting):
        if(setting[0] =='pc_version') :
            query = {"site_id": setting[0],"platform": setting[1], "id": setting[2] }
        else : #web_one_id, web은 site_id에 baemin 한개 아이디만 가진다
            query = {"site_id": setting[0],"platform": setting[1] }
        print(f"Query: {query}")
        try :
            result = self.customers.find_one(query)
            if result :
                print(f"Updating {setting[0]}: {result}")            
                new_values = {"$set": {"id": setting[2], "password": setting[3], "shop_id": setting[4], "shop_name": setting[5]}}
                self.customers.update_one(query, new_values)
                #print(f"Updated document: {result}")
            else : # Insert a new record
                document = {"site_id": setting[0], "platform":setting[1],"id": setting[2], "password": setting[3], "shop_id": setting[4], "shop_name": setting[5]}
                inserted_id = self.customers.insert_one(document).inserted_id
                print(f"Inserted document IDs: {inserted_id}")
        except Exception as e:
            print(f"DB ERROR add_customer: {e}")

    def update_setttings(self,settings): #update or insert
        # 4. 데이터 수정
        # Update the phone number of the record with the given id
        #{"site_id": setting[0], "platform": setting[1] {"$set": {"id": setting[2], "password": setting[3], "shop_id": setting[4], "shop_name": setting[5]}}
        for setting in settings:
            self.add_customer(setting)
        print("Settings updated")
    
    def update_user_enabled(self,site_id, user_enabled):
        # 4. 데이터 수정
        # Update the phone number of the record with the given id
        query = {"id": site_id}
        new_values = {"$set": {"user_run": user_enabled}}
        result = self.account.update_one(query, new_values)
        print(f"User run updated {result}    {site_id} {user_enabled}")
        
    def get_settings(self,id):
        #web only
        result = []
        user_enabled = False
        system_enabled = False  
        try :
            query = {"site_id": id}
            result = list(self.customers.find(query))
            print(result)
            account = self.account.find_one({"id":id}) 
            user_enabled = account.get("user_run", False)
            system_enabled = account.get("system_permission", False)
            print(f"User enabled: {user_enabled}, System enabled: {system_enabled}")
            if result:
                print(f"Settings found: {result}")                
            else:
                print("Settings not found")

        except Exception as e:
            print(f"DB ERROR get_settings: {e}")
        return result,system_enabled, user_enabled

    def display_all(self,table):
        # 4. 데이터 조회 (전체)
        print("Reading all data:")
        if(table == "account"):
            for doc in self.account.find():
                print(doc)
        else:
            for doc in self.customers.find():
                print(doc)
                
    def close_db(self):
        # 5. MongoDB 연결 종료
        self.client.close()

if __name__ == "__main__":
    db = dbms()
    init_telegram()
    #gptPosts.drop()
    #db.build_account()
    #db.make_index()
    #clear_account()
    #clear_customers()
    #db.build_gptPosts()
    db.get_gptPosts("cafe4")
    
    ret = db.loginCheck("cafe2", "aicafe139")
    for i in range(0):
        ret = db.add_gptPosts([{"platform" :"baemin","site_id":"c","shop_id":"shop_1","shop_name":"shop_name_1",
                    "review":"NO_REVIEW","review_info":"post_info1","reply":"reply_1","reply_info":"info","shop_type":"shop_type","date":datetime.now()}])

    #asyncio.run(tele_send(f"dbms  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
                       
                        
    db.get_customers("baemin")
    db.close_db()