
class Recap_Agent:
    def __init__(self,i_dir):
        self.i_dir = i_dir

    def Get_Recaps(self):
        recaps = []
        for chat in os.listdir(f"./{self.i_dir}/Chat"):
            recaps.append(chat.replace(".pkl",""))
        return recaps

    def Create_Chat_Title(self,chat_history):
        system_prompt = f'''
        Analyze the following chat conversation and generate a concise yet informative title that summarizes the key topic or theme discussed. 
        The title should be clear, engaging, and no longer than 8 words. 
        Here is the chat history: {chat_history}'''
        
        response = openai.chat.completions.create(
          model = "gpt-4o",
          messages = [{"role":"system","content":system_prompt}]
        )
        return response.choices[0].message.content
        