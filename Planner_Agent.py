import Data_Collector_Agent,Tutor_Agent,Recap_Agent

class Planner_Agent:
    def __init__(self,saved_chat_size,topic_name):
        self.topic_name = topic_name.replace(" ","")
        self.data_agent = Data_Collector_Agent(self.topic_name)
        self.collection = self.data_agent.Get_Collection()
        self.tutor_agent = Tutor_Agent(self.collection,self.topic_name)
        self.recap_agent = Recap_Agent(self.topic_name)
        self.saved_chat_size = saved_chat_size
        if "Chat" not in os.listdir(f"./{self.topic_name}"):
          os.mkdir(f"{self.topic_name}/Chat")
        
    def Chat(self,prompt,history):
        if len(history)>=self.saved_chat_size:
            if (len(history))%self.saved_chat_size==0:
             self.Save_Chat(history[-self.saved_chat_size:])
            history = history[-self.saved_chat_size:]
        
        stream = self.tutor_agent.Chat(prompt,history)
        return stream
        #response = ""
        #for chunk in stream:
        #    filtered_chunk = chunk.choices[0].delta.content or ""
        #    response += filtered_chunk
        #    yield response
            
   # def Load_Chat_IDs(self):
   #     if "chat_ids.pkl" not in os.listdir(f"./{self.topic_name}/Chat"):
   #         with open(f"{self.topic_name}/Chat/chat_ids.pkl","wb") as file:
   #             pickle.dump([],file)
   #     with open(f"{self.topic_name}/Chat/chat_ids.pkl","rb") as file:
   #         ID_data = pickle.load(file)
   #     if ID_data == None:
   #         return []
   #     return ID_data

    def Save_Chat(self,chat_data):
        #Chat_IDs = self.Load_Chat_IDs()
        #index = len(Chat_IDs)+1
        # get chat title
        chat_title = self.recap_agent.Create_Chat_Title(chat_data)
        print(chat_title)
        for name in os.listdir(f"./{self.topic_name}./Chat"):
            if chat_title==name.replace(".pkl",""):
                 chat_title+="_1"
        #Chat_IDs.append(index)
        with open(f"{self.topic_name}/Chat/{chat_title}.pkl","wb") as file:
            pickle.dump(chat_data,file)
       # with open(f"{self.topic_name}/Chat/chat_ids.pkl","wb") as file:
       #     pickle.dump(Chat_IDs,file)

    def Get_Recaps(self):
        return self.recap_agent.Get_Recaps()

