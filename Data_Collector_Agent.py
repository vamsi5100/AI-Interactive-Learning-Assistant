


class Data_Collector_Agent:
    def __init__(self,topic_name):
        self.topic_name = topic_name
        if self.topic_name not in os.listdir("."):
          os.mkdir(self.topic_name)
        if "Courses.pkl" not in os.listdir("."):
            with open("Courses.pkl","wb") as file:
                pickle.dump([],file)
        with open("Courses.pkl","rb") as file:
                self.courses = pickle.load(file)
        if self.topic_name not in self.courses:
           self.courses.append(self.topic_name)
           with open("Courses.pkl","wb") as file:
                   pickle.dump(self.courses,file)
           
        self.textbook_info_system_prompt = '''
Assume you are a guy who creates textbook notes. Generate a detailed information about the given topic and its subtopic.
Respond strictly in json format.

Here is the example of the required json format.
output = {
    "topic": "a1",
    "subtopic": "b1",
    "details": "brief information about the topic and subtopic in 3-4 lines covering all concepts ------."
}
'''
    def Get_Messages(self):
        data_collection_system_prompt = '''
        Assume you are a AI teaching assistant. You need to prepare complete 12 week workflow of a given topic_name which needs to include every concept from start to end.Respond strictly in JSON format.
        The output format should be as shown:
        output = {
                  "Week 1" : {
                         "Day 1": { "topic 1":[concept 1,concept 2,.........]
                                    "topic 2":[concept 1,concept 2,.........] 
                         }
                         "Day 2": { "topic 1":[concept 1,concept 2,.........]
                                    "topic 2":[concept 1,concept 2,.........] 
                         }
                  }
                  "Week 2" : {
                         "Day 1": { "topic 1":[concept 1,concept 2,.........]
                                    "topic 2":[concept 1,concept 2,.........] 
                         }
                         "Day 2": { "topic 1":[concept 1,concept 2,.........]
                                    "topic 2":[concept 1,concept 2,.........] 
                         }
                         "Day 3": { "topic 1":[concept 1,concept 2,.........]
                                    "topic 2":[concept 1,concept 2,.........] 
                         }
        
                  }
                  
                 }
        '''
        data_collection_user_prompt = f"The topic name is {self.topic_name}"
        messages = [
             {"role":"system", "content" : data_collection_system_prompt  },
             {"role":"user", "content" : data_collection_user_prompt  }
        ]
        return messages
    def format_to_json(self,string):
       stringremovals = ["```json","```"]
       output = string
       for char in stringremovals:
         output = output.replace(char,"")
       return output
        
    def Curriculum_Generator_Agent(self):
        messages = self.Get_Messages()
        # load the llm
   
        output = openai.chat.completions.create(
               model = "gpt-4o",
               messages = messages,   
        )
        curriculum = output.choices[0].message.content
        output = json.loads(self.format_to_json(curriculum))
        if os.path.exists(f"{self.topic_name}/curriculum.json"):
            os.remove(f"{self.topic_name}/curriculum.json")
        with open(f"{self.topic_name}/curriculum.json","w") as file:
            json.dump(output,file,indent=4)
        curriculum_list = list(output.values())
        return curriculum_list
        
    def Create_Data(self,curriculum_list):
        textbook_data=[]
        for week in range(0,len(curriculum_list)):
         for day in curriculum_list[week]:
           topic = list(curriculum_list[week][day].keys())[0]
           for subtopic in curriculum_list[week][day][topic]:
              textbook_info_user_prompt = f"The topic is {topic} and the subtopic is {subtopic}."
              textbook_messages = [
             {"role" : "system" , "content" : self.textbook_info_system_prompt},
             {"role" : "user" , "content" : textbook_info_user_prompt}
               ]
              response = openai.chat.completions.create(
              model = "gpt-4o",
              messages = textbook_messages
              )
              textbook_data.append(self.format_to_json(response.choices[0].message.content))
              break
           break
         break
        return textbook_data
        
    def Create_Collection(self,textbook_data):
         # instantiate chromadb
         client = chromadb.PersistentClient(f"{self.topic_name}/{self.topic_name}")
         client_ai = OpenAI()
         # create embeddings
         embeddings = [client_ai.embeddings.create(input = [data],model ="text-embedding-ada-002").data[0].embedding
                   for data in textbook_data
                  ]
         # create collection
         collection = client.create_collection(name = self.topic_name)
         ids = [str(i+1) for i in range(0,len(textbook_data))]
         # add embeddings, documents, ids to the collections
         
         collection.add(
           embeddings= embeddings,
           documents=textbook_data,
           ids=ids
         )
         return collection
        

        
    def Run(self):
        curriculum_list = self.Curriculum_Generator_Agent()
        textbook_data = self.Create_Data(curriculum_list)
        collection_data = self.Create_Collection(textbook_data)

    def Get_Collection(self):
       
       # instantiate chromadb
       #print(f"topic_name : {self.topic_name}")
       client = chromadb.PersistentClient(f"{self.topic_name}/{self.topic_name}")
        
       isthere = any(self.topic_name==collection.name for collection in client.list_collections())
        
       # get collection
       if isthere:
         return client.get_collection(self.topic_name)
       else:
         self.Run()
         collection = client.get_collection(self.topic_name)
         if collection:
             return collection
         print("No Collection found")
         return collection
    