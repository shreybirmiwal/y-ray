from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI


from dotenv import load_dotenv
import os
load_dotenv()


graph = Neo4jGraph(url="neo4j+s://5f3c6da1.databases.neo4j.io", username="neo4j", password="f0VIEK1-IwQqhfZvlM6_kZxQyA8GdbSVta-ckU5pHVw")

graph.query(
    """
MERGE (m:Movie {name:"Top Gun", runtime: 120})
WITH m
UNWIND ["Tom Cruise", "Val Kilmer", "Anthony Edwards", "Meg Ryan"] AS actor
MERGE (a:Actor {name:actor})
MERGE (a)-[:ACTED_IN]->(m)
"""
)