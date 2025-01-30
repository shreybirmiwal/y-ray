import openai
from dotenv import load_dotenv
import os
import json
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI

############################## Initialization ##############################
load_dotenv()
client = openai.OpenAI(
    api_key=os.getenv("AKASH_API"),
    base_url="https://chatapi.akash.network/api/v1"
)
graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"), password=os.getenv("NEO4J_PASSWORD"), enhanced_schema=True,)
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=os.getenv("AKASH_API"),
    model="Meta-Llama-3-1-8B-Instruct-FP8",
    request_timeout=60,
    base_url="https://chatapi.akash.network/api/v1"
)
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_requests=True
)
############################# END Initialization ############################


def query_llm(system_prompt, user_prompt, json_schema):

    response = client.chat.completions.create(
        model="Meta-Llama-3-1-8B-Instruct-FP8",
        messages = [
            {
                "role": "system",
                "content": system_prompt + "\n" + "ONLY respond in the following JSON format: " + json_schema
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

def getUpdatedSchema(graph):
    graph.refresh_schema()
    print(graph.schema)
    return graph.schema

def add_new(user_prompt=""):
    system_prompt = "You are to extract information from the following prompt. You can leave things empty if it is NA"
    json_schema = '{"name": "John Doe", "contact": "Phone: 123-456-7890, Email john@gmail.com", "birthday": "07-25-2001", "job": "NA", "facts": "Likes apples", "friends": ["Jane Doe", "Jack Doe"], "location": "SF"}'
    
    structured = query_llm(system_prompt, user_prompt, json_schema)
    print(structured)

    try:
        with open('database.json', 'r', encoding='utf-8') as file:
            database = json.load(file)
    except FileNotFoundError:
        database = []

    database.append(structured)
    with open('database.json', 'w', encoding='utf-8') as file:
        json.dump(database, file, indent=4)


    # add data to graph
    # current_graph_schema = getUpdatedSchema(graph=graph)
    # q = LLM_cypher(f"Please generate a sequence of Cypher queries to add this new user to the graph database (neo4j). This is the  user: {str(structured)}. Do not output anything other than the Cypher query.")
    # print(q)
    # graph.query(q)

def query(user_prompt):
    result = chain.invoke({"query": user_prompt})
    print(f"Intermediate steps: {result['intermediate_steps']}")
    print(f"Final answer: {result['result']}")

    # who's birthday is coming up?
    # update users details
    # 'who can i meet in NYC related to ai next week?'
    # 'who do i know that can intro me to Jane Doe?'
    # what should i say to user xys
    # who should I invite to my birthday party given we should have common friends
    # who should I message to get a job at company xyz
    # who should I message to check in with them and maintain relationship


while(True):
    choice = input("/add, /query, /exit: ")
    if choice == "/add":
        user_prompt = input("Who would you like to add to the network? ")
        add_new(user_prompt=user_prompt)

    elif choice == "/query":
        user_prompt = input("What would you like to search? ")
        query(user_prompt)

    elif choice == "/exit":
        break
    else:
        print("Invalid choice")
