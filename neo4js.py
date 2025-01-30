from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os
load_dotenv()

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

graph.query(
    """
MERGE (m:Movie {name:"Top Gun", runtime: 120})
WITH m
UNWIND ["Tom Cruise", "Val Kilmer", "Anthony Edwards", "Meg Ryan"] AS actor
MERGE (a:Actor {name:actor})
MERGE (a)-[:ACTED_IN]->(m)
"""
)


def getUpdatedSchema(graph):
    graph.refresh_schema()
    print(graph.schema)
    return graph.schema


getUpdatedSchema(graph=graph)
result = chain.invoke({"query": "Who played in Top Gun?"})
print(f"Intermediate steps: {result['intermediate_steps']}")
print(f"Final answer: {result['result']}")