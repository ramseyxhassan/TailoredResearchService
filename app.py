import streamlit as st
from datetime import datetime
from dateutil.relativedelta import *
from AlgoScholar_v2 import algoscholar_chat1, load_documents
from pyvis import network as net
from IPython.display import display, HTML
from typing import NamedTuple

MAX_CHAT_SESSIONS = 5
MAX_MESSAGES_PER_SESSION = 20

with open('algo.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    


if "chat_history" not in st.session_state:
    st.session_state.chat_history = {"Session 1": []}
    st.session_state.selected_session = "Session 1"
    st.session_state.rating_history = []
    st.session_state.current_rating = None
    st.session_state.save_key = None

def get_next_session_name():
    existing_session_numbers = [int(name.split(" ")[-1]) for name in st.session_state.chat_history.keys()]
    for session_number in range(1, MAX_CHAT_SESSIONS + 1):
        if session_number not in existing_session_numbers:
            return f"Session {session_number}"
    return None

def create_new_chat_session():
    new_session_name = get_next_session_name()
    if new_session_name:
        st.session_state.chat_history[new_session_name] = []
        st.session_state.selected_session = new_session_name
        st.experimental_rerun()
    else:
        st.warning(f"Maximum number of chat sessions ({MAX_CHAT_SESSIONS}) reached.")

def delete_chat_session(session_name):
    if len(st.session_state.chat_history) > 1:
        if session_name in st.session_state.chat_history:
            del st.session_state.chat_history[session_name]
            available_sessions = list(st.session_state.chat_history.keys())
            st.session_state.selected_session = available_sessions[0]
            st.experimental_rerun()
    else:
        st.warning("Cannot delete the last chat session.")

selected_topic = st.sidebar.selectbox("Select Topic", ["Computer Science", "Quantitative Finance", "Economics"])
date = datetime.now()
defaultdate = date + relativedelta(months=-3)
start_date = st.sidebar.date_input("Start Date", defaultdate)
end_date = st.sidebar.date_input("End Date", min_value=datetime(2020, 1, 1), max_value=datetime.today())

if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")
    st.stop()

chat_sessions = list(st.session_state.chat_history.keys())
selected_session = st.session_state.selected_session
selected_session_index = chat_sessions.index(selected_session) if selected_session in chat_sessions else 0
selected_session = st.sidebar.radio("Chat Sessions", options=chat_sessions, index=selected_session_index)

if st.sidebar.button("Create New Chat Session"):
    create_new_chat_session()

if st.sidebar.button("Delete Chat Session") and len(st.session_state.chat_history) > 1:
    delete_chat_session(selected_session)
st.title("💬 Welcome to AlgoScholar Chatbot")
#st.title("💬 Chatbot")

for index, msg in enumerate(st.session_state.chat_history[selected_session]):
    if msg["role"] == "assistant":
        rating_key = f"rating_{selected_session}_{index}"
        current_rating = st.radio(
            "Rate the relevance of the response:",
            ["1 - Not Relevant", "2 - Somewhat Relevant", "3 - Highly Relevant"],
            key=rating_key
        )

        # Save individual ratings
        if st.button("Save Rating", key=f"save_rating_{selected_session}_{index}"):
            if current_rating:
                prompt = st.session_state.get('current_prompt', 'No prompt')
                chatbot_response = st.session_state.get('current_response', 'No response')
                st.session_state.rating_history.append((prompt, chatbot_response, current_rating))
                st.success("Rating saved successfully!")
            else:
                st.warning("Please select a rating before saving.")

if "awaiting_response" not in st.session_state:
    st.session_state.awaiting_response = False

if len(st.session_state.chat_history[selected_session]) < MAX_MESSAGES_PER_SESSION:
    if len(st.session_state.chat_history[selected_session]) % 2 == 0:
        prompt = st.chat_input(disabled=st.session_state.awaiting_response)
        
        if prompt:
            st.session_state.awaiting_response = True
            st.session_state.chat_history[selected_session].append({"role": "user", "content": prompt})

            with st.spinner("Thinking..."):
                chat_history = [msg["content"] for msg in st.session_state.chat_history[selected_session]]
                #json_path = "./ARXIV/CS/combined_references_cs.json"
                documents = load_documents#('2024-02-01', '2024-02-01')#(json_path=json_path)
                documents
                # documents = load_documents(start_date, end_date)
              
                chatbot_response = algoscholar_chat1(user_query=prompt, documents=documents, chat_history=chat_history)
                st.session_state['current_prompt'] = prompt
                st.session_state['current_response'] = chatbot_response
                st.session_state.chat_history[selected_session].append({"role": "assistant", "content": chatbot_response})

            st.session_state.current_rating = st.radio("Rate the relevance of the response:", ["1 - Not Relevant", "2 - Somewhat Relevant", "3 - Highly Relevant"], key=f"rating_{prompt}")
                
            if st.button("Save Rating", key=st.session_state.save_key):
                if current_rating:
                    prompt = st.session_state.get('current_prompt', 'No prompt')
                    chatbot_response = st.session_state.get('current_response', 'No response')
                    st.session_state.rating_history.append((prompt, chatbot_response, current_rating))
                    st.success("Rating saved successfully!")
                else:
                    st.warning("Please select a rating before saving.")
                        
            st.session_state.awaiting_response = False
else:
    st.warning(f"Maximum number of messages ({MAX_MESSAGES_PER_SESSION}) reached for this session.")
