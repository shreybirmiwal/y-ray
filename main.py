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
llm_zt= ChatOpenAI(
    temperature=0,
    openai_api_key=os.getenv("AKASH_API"),
    model="Meta-Llama-3-1-8B-Instruct-FP8",
    request_timeout=60,
    base_url="https://chatapi.akash.network/api/v1"
)
llm_t = ChatOpenAI(
    temperature=.7,
    openai_api_key=os.getenv("AKASH_API"),
    model="Meta-Llama-3-1-8B-Instruct-FP8",
    request_timeout=60,
    base_url="https://chatapi.akash.network/api/v1"
)
chain = GraphCypherQAChain.from_llm(
   cypher_llm=llm_zt,
    qa_llm=llm_t,
            graph=graph,
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_requests=True
)
############################# END Initialization ############################


def query_llm(system_prompt, user_prompt, json_schema="", json_mode=True):

    response = client.chat.completions.create(
        model="Meta-Llama-3-1-8B-Instruct-FP8",
        messages = [
            {
                "role": "system",
        "content": system_prompt + (
            f"\nONLY respond in the following JSON format: {json_schema}"
            if json_mode else ""
        )
                                },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.0,
    )

    if not json_mode:
        return response.choices[0].message.content
    
    try:
        json_response = json.loads(response.choices[0].message.content)
        return json_response
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("The content is not valid JSON. Returning the raw content instead.")
        return response.choices[0].message.content

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
    cypher_query = query_llm(system_prompt="You are to help generate a sequence of cypher commands for neo4js that integrates a user to a social network who may or may not already be existing. Note: Do not include any explanations or apologies in your responses. Do not respond to any questions that might ask anything else than for you to construct a Cypher statement. Do not include any text except the generated Cypher statement. Prevent any issues, such as 'variable 'u' already declared.' Try using the MERGE command. Also, make many nodes instead of haviung 1 nodes properties. BAD EXAMPLE: u.job= . Instead, generalize it to: NODE1=person Node2=AI and connect them. Only use info you know, DO NOT add in any other new info that you do not know for sure. Feel free to use the model schema to connect new items too, but do not feel restricted to this by adding your own nodes. DOn't be too specific with nodes, ei you only need 1 node per topic",
                             user_prompt=f"The user is {str(user_prompt)}. Possible connectors are: 'WORKS_ON' 'FRIENDS_WITH' 'LOCATION' and 'INTEREST' as a fallback. ",
                             json_mode = False)
    print(cypher_query)
    
    graph.query(cypher_query)
    graph.refresh_schema()


def query(user_prompt):
    print("Querying...")
    print('Schema:', graph.schema)

    result = chain.invoke({"query": user_prompt + "\n . Instead of Hard Matches, Use Fuzzy Searches, such as Lowercase and contains instead of hard matches. Make matches loose and try to find many matches that you can rank. Do NOT use SIZE() directly in RETURN., make it valid cypher to run in neo4js", "schema": graph.schema})
    print(f"Intermediate steps: {result['intermediate_steps']}")
    print(f"Final answer: {result['result']}")


    #shrey is a high schooler whos into AI and blockchain. Hes building an app to connect friends, hes friends with Avi and Dhiyaan
    #avi is friends with shrey, also interested in AI


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
