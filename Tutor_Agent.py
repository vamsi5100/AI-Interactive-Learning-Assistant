
class Tutor_Agent:
    def __init__(self,collection,topic):
        self.collection = collection
        self.topic = topic
        self.system_prompt = {"role":"system","content":f'''
        Assume the role of an expert educator skilled in making complex concepts easy to understand. 
        Engage the user in an interactive learning experience by asking thought-provoking questions, encouraging them to analyze, predict outcomes, and apply the knowledge in real-world scenarios.
        Use relatable analogies, visual descriptions, and practical examples. 
        Adapt your teaching style based on the user's responses, ensuring they feel challenged yet supported. 
        Frequently invite the user to summarize key points to reinforce learning, and encourage them to ask questions throughout.
        Make sure to cover all the concepts in depth by asking interactive questions within the given topic without missing anything and make sure the user learns it before proceeding to the next step.
        You should strictly talk only about the topic given and nothing else.
        The topic is about {self.topic}.
        '''}
    #def Get_system_prompt(self):
    #    response = openai.chat.completions.create(
    #        model = "gpt-4o",
    #        messages = [self.pre_system_prompt]
    #    )
    #    return response.choices[0].message.content
    def Get_Response(self,messages):
        response = openai.chat.completions.create(
          model = "gpt-4o",
          messages = messages,
            stream=True
        )
        return response
        
    def Get_Embedding(self,input_prompt):
       embedding = OpenAI().embeddings.create(input = [input_prompt],model ="text-embedding-ada-002").data[0].embedding
       return embedding
        
    def Chat(self,user_prompt,history):
        # retrieve information from the collection
        retrieved_info = self.collection.query(
            query_embeddings = self.Get_Embedding(user_prompt),
            n_results = 3
        )

        messages = [{"role":"system","content":f"{self.system_prompt}"}]
        for r_info in retrieved_info["documents"][0]:
            messages.append({"role":"system","content":f"{r_info}"})
            
        #for chat in history:
        #    if chat["role"]=="user":
        #      messages.append({"role":"user","content":chat["content"]})
        #    else:
        #      messages.append({"role":"assistant","content":chat["content"]})

        for chat in history:
              messages.append({"role":"user","content":chat[0]})
              messages.append({"role":"assistant","content":chat[1]})
        
        messages.append({"role":"user","content":f"{user_prompt}"})
        stream = self.Get_Response(messages)
        
#        response = ""
#        for chunk in stream:
#            filtered_chunk = chunk.choices[0].delta.content or ""
#            response += filtered_chunk
        return stream
    