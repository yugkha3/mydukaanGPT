# could've use a utils.js file in client but there's cors problem with pinecone i guess, hence a seperate fastAPI server to do all these.
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
import openai
import requests
import logging
import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONT_END_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def query_database(query_prompt) -> Dict[str, Any]:
    url = f"{os.getenv('PINECONE_URL')}/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Api-Key": os.getenv("PINECONE_API_KEY"),
    }
    data = {"vector": query_prompt, "top_k": 5, "includeMetadata": True, "namespace": ""}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")

def apply_prompt_template(question: str) -> str:
    prompt = f"""
        based on the above context(refer the context it as dukaan help center documentation), answer the question: {question}, also provide the source of this information(if available) as "to find out more" and be as elaborative as possible.
    """
    return prompt

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_chatgpt_api(user_question: str, chunks: List[str]) -> Dict[str, Any]:
    messages = list(
        map(lambda chunk: {
            "role": "user",
            "content": chunk
        }, chunks))
    question = apply_prompt_template(user_question)
    messages.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return response

def ask(user_question: str) -> Dict[str, Any]:
    response = openai.Embedding.create(
        input=user_question,
        model='text-embedding-ada-002'
    )
    embeddings = response['data'][0]['embedding']
    chunks_response = query_database(embeddings)
    chunks = []
    for match in chunks_response["matches"]:
        metadata = match.get('metadata', {})
        chunks.append(str(metadata))
    logging.info("User's questions: %s", user_question)
    logging.info("Retrieved chunks: %s", chunks)

    response = call_chatgpt_api(user_question, chunks)
    logging.info("Response: %s", response)

    return response["choices"][0]["message"]["content"]

@app.get("/")
def root():
    return {"message": "Welcome to the API. Use '/ask' endpoint to ask a question."}

@app.post("/ask")
async def ask_question(request_data: Dict[str, str]) -> Dict[str, Any]:
    question = request_data.get('question')
    if not question:
        raise HTTPException(status_code=400, detail="Question field is missing")

    try:
        answer = ask(question)
        return {"answer": answer}
    except Exception as e:
        logging.error("An error occurred while processing the question: %s", e)
        raise HTTPException(status_code=500, detail="Error occurred while processing the question")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)