import openai
import json
import os
import re
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
import pickle
import gradio as gr


# load the API keys
load_dotenv()
api_key  = os.getenv("OPENAI_API_KEY")
if api_key==None:
    print(False)
else:
    print(True)


saved_chat_size = 1
if "Courses.pkl" not in os.listdir("."):
   with open("Courses.pkl","wb") as file:
          pickle.dump([],file)
with open("Courses.pkl", "rb") as file:
    course_data = pickle.load(file)

planner_agent = None

def initialize_planner_agent(topic_name,existing_topics):
    global planner_agent
    if topic_name=="No Existing Topics":
       return [topic_name,gr.Dropdown(choices=recaps, value= None,interactive=True),gr.Dropdown(choices = course_data,value = topic_name,interactive=True)]
    if topic_name not in course_data:
        course_data.append(topic_name)
    planner_agent = Planner_Agent(saved_chat_size, topic_name=topic_name)
    recaps = planner_agent.Get_Recaps()

    if not recaps:
        recaps = ["No recaps available"]

    return [topic_name,gr.Dropdown(choices=recaps, value=recaps[0] if recaps[0]=="No recaps available" else None,interactive=True),gr.Dropdown(choices = course_data,value = topic_name,interactive=True),[]]

def Change_History(topic_name,chat_name):
    if chat_name==None or chat_name=="No recaps available":
        return gr.Chatbot(label="Chat History")
    with open(f"{topic_name}/Chat/{chat_name}.pkl","rb") as file:
        history = pickle.load(file)
    return history

def chat_with_agent(message, history):
    if planner_agent is None:
        return history + [("Error", "Please submit a topic first.")]

    stream = planner_agent.Chat(message, history)
    response = ""

    recaps = planner_agent.Get_Recaps()

    if not recaps:
        recaps = ["No recaps available"]

    for chunk in stream:
        filtered_chunk = chunk.choices[0].delta.content or ""
        response += filtered_chunk
        yield [history + [(message, response)],gr.Dropdown(choices=recaps, value=recaps[0] if recaps[0]=="No recaps available" else None,interactive=True),gr.Textbox(value = "")]

demo = gr.Blocks()
with demo:
    gr.Markdown("## Interactive Learning Assistant")

    with gr.Row():
        topic_input = gr.Textbox(label="Enter Topic Name")
        submit_button = gr.Button("Submit")

    with gr.Row():
        existing_topics = gr.Dropdown(choices=course_data , label="Existing Topics",interactive=True,value="No Existing Topics" if len(course_data)==0 else None)
        chat_recaps = gr.Dropdown(choices= [], label="Chat Recaps",value="No Chat Recaps")  # Will update dynamically

    with gr.Row():
        chat_output = gr.Chatbot(label="Chat History")

    with gr.Row():
        chat_input = gr.Textbox(label="Enter your message")

    send_button = gr.Button("Send")
    
    existing_topics.change(initialize_planner_agent,inputs=[existing_topics,existing_topics],outputs=[topic_input,chat_recaps,existing_topics,chat_output])

    chat_recaps.change(
        Change_History,
        inputs = [topic_input,chat_recaps],
        outputs = chat_output
    )
    
    # Update recaps dropdown dynamically when topic is submitted
    submit_button.click(
        initialize_planner_agent, 
        inputs=[topic_input,existing_topics], 
        outputs=[topic_input,chat_recaps,existing_topics,chat_output]
    )

    send_button.click(chat_with_agent, inputs=[chat_input, chat_output], outputs=[chat_output,chat_recaps,chat_input])

demo.launch()
