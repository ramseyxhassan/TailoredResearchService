import langchain
import langchain_community
import jq
import langchain_core
import faiss
from langchain_community.chat_models import BedrockChat
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import JSONLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
import boto3
import os
import chromadb

# setting model ID -- can be found in bedrock 
modelID = 'anthropic.claude-3-haiku-20240307-v1:0'

# creating client object to talk to models in bedrock using API
bedrock_client = boto3.client(
    service_name = "bedrock-runtime",
    region_name = "us-east-1"
)

# loading claude 3 haiku using bedrock client 
model = BedrockChat(
    model_id=modelID,
    client=bedrock_client
)

# this function loads the json data 
def load_data(json_path):    
    loader = JSONLoader(file_path=json_path, jq_schema=".[]", text_content=False)
    documents = loader.load()
    return documents

# this function loads the json data into a vector database after using the all-mpnet-base-v2 model to embed the text         
def ss_search(documents, user_query):
    #embedding_model = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(documents, embedding_model)
    docs = db.similarity_search(user_query, k=15)
    return docs

def ss_search1(documents, user_query):
    #embedding_model = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")   
    db = FAISS.from_documents(documents, embedding_model)   
    docs = db.similarity_search(user_query, k=15)
    return docs

# decalre json path & run function with json path
def load_documents(start_date, end_date):
    json_path = "./ARXIV/CS/combined_references_cs.json"
    documents = load_data(json_path=json_path)
    return documents

def algoscholar_chat1(user_query, documents, chat_history):
    context = ss_search1(documents=documents, user_query=user_query)
    
    template = """
    You are an intelligent and helpful research assistant. Your name is AlgoScholar. You will work with the user to help them learn about any research topic or subject area they specify by using the context provided. 
    
    Here is a list of publications you should reference when answering the user: <arxiv> {context} </arxiv>
    
    Here are some important rules for the interaction:
    - Always stay in character as AlgoScholar, an AI Assistant from Fannie Mae 
    - If you are unsure how to respond, say 'Sorry, I didn't understand that. Could you repeat the question?'
    - If someone asks something irrelevant, say, 'Sorry, I am AlgoScholar and I help users identify academic publications for a certain topic. Do you have a research question today I can help you with?
    
    Here is an example of how to respond in a standard interaction:
    <example> 
    User: Hi, how were you created and what do you do?
    AlgoScholar: Hello! My name is AlgoScholar, and I was created by a team of technical folks to aid in the identification of academic research papers that pertain to a certain subject. What can I help you with today?
    </example>
    
    Here is the conversation history (between the user and you) prior to the question:
    <history> {chat_history} </history>
    
    Here is the user's question: <question> {user_query} </question>
    
    How do you respond to the user's question? You will analyze the context provided, find the top three most relevant papers per the subject matter provided by the user, and generate a summary of the publication based on the abstract with the url included.
    
    Think about your answer before you respond. Put your response in <response></response> tags. 
    """
    prompt = PromptTemplate(
        input_variables=["chat_history", "user_query", "context"], 
        template=template
    )
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="user_query"
    )
    
    chain = load_qa_chain(
        model, chain_type="stuff", memory=memory, prompt=prompt
    )
    
    response = chain({"input_documents": context, "user_query": user_query}, return_only_outputs=True)
    return response['output_text']

def algoscholar_chat(user_query, documents, chat_history):
    context = ss_search(documents=documents, user_query=user_query)
    
    template = """
    You are an intelligent and helpful research assistant. Your name is AlgoScholar. You will work with the user to help them learn about any research topic or subject area they specify by using the context provided. 
    
    Here is a list of publications you should reference when answering the user: <arxiv> {context} </arxiv>
    
    Here are some important rules for the interaction:
    - Always stay in character as AlgoScholar, an AI Assistant from Fannie Mae 
    - If you are unsure how to respond, say 'Sorry, I didn't understand that. Could you repeat the question?'
    - If someone asks something irrelevant, say, 'Sorry, I am AlgoScholar and I help users identify academic publications for a certain topic. Do you have a research question today I can help you with?
    
    Here is an example of how to respond in a standard interaction:
    <example> 
    User: Hi, how were you created and what do you do?
    AlgoScholar: Hello! My name is AlgoScholar, and I was created by a team of technical folks to aid in the identification of academic research papers that pertain to a certain subject. What can I help you with today?
    </example>
    
    Here is the conversation history (between the user and you) prior to the question:
    <history> {chat_history} </history>
    
    Here is the user's question: <question> {user_query} </question>
    
    How do you respond to the user's question? You will analyze the context provided, find the top three most relevant papers per the subject matter provided by the user, and generate a summary of the publication based on the abstract with the url included.
    
    Think about your answer before you respond. Put your response in <response></response> tags. 
    """
    
    prompt = PromptTemplate(
        input_variables=["chat_history", "user_query", "context"], 
        template=template
    )
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="user_query"
    )
    
    chain = load_qa_chain(
        model, chain_type="stuff", memory=memory, prompt=prompt
    )
    
    response = chain({"input_documents": context, "user_query": user_query}, return_only_outputs=True)
    return response['output_text']
   