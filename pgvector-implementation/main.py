from typing import Any, List, Dict
import openai
import psycopg2
import logging

# Set up the OpenAI API client
import os
from dotenv import load_dotenv
load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")


# Set up the PostgreSQL connection
connection = psycopg2.connect(
    host='localhost',
    dbname='mydukaangpt',
    user='yug',
    password='2603',
    port=5432
)


def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query the PostgreSQL database to retrieve chunks with the user's input questions.
    """
    cursor = connection.cursor()

    cursor.execute(
        f"""
        SELECT doc FROM documents ORDER BY embedding <=> '{query_prompt}' LIMIT 1;
        """
    )

    results = cursor.fetchall()
    cursor.close()

    return {"results": results}

messages = [{"role": "system", "content": "You are a helpful assistant."}]

def call_chatgpt_api(user_question: str, chunks: List[str]) -> Dict[str, Any]:
    """
    Call the OpenAI ChatGPT API with the user's question and retrieved chunks.
    """
    # Send a request to the GPT-3 API

    for chunk in chunks:
    	messages.append({"role": "user", "content": str(chunk)})

    messages.append({"role": "user", "content": f'Question: {user_question}'})
    print(f'\n\nMessages sent to the API: {messages}\n\n')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,  # High temperature leads to a more creative response.
    )
    return response


def ask(user_question: str) -> Dict[str, Any]:
    """
    Handle the user's questions.
    """
    response = openai.Embedding.create(
        input=user_question,
        model='text-embedding-ada-002'
    )
    embeddings = response['data'][0]['embedding']

    # Get chunks from the database.
    chunks_response = query_database(embeddings)
    chunks = chunks_response["results"]
    
    response = call_chatgpt_api(user_question, chunks)
    logging.info("Response: %s", response)
    messages.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})

    return response["choices"][0]["message"]["content"]

while True:
        user_query = input("User: ")
        print(f'GPT: {ask(user_query)} \n\n')