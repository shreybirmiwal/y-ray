import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = openai.OpenAI(
    api_key=os.getenv("AKASH_API"),
    base_url="https://chatapi.akash.network/api/v1"
)

def query_llm(system_promt, user_prompt, json_schema):

    response = client.chat.completions.create(
        model="Meta-Llama-3-1-8B-Instruct-FP8",
        messages = [
            {
                "role": "system",
                "content": system_promt + "\n" + "ONLY respond in the following JSON format: " + json_schema
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.0,
    )

    #check if valid JSON
    try:
        json_response = json.loads(response.choices[0].message.content)
        return json_response
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("The content is not valid JSON. Returning the raw content instead.")
        return response.choices[0].message.content
    

json_schema = '{"name": "John Doe", "phone": "123-456-7890", "email": ""}'
print(query_llm(system_promt="ur a ai assistant" , user_prompt="tell me about canada", json_schema=json_schema))