from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"

driver = GraphDatabase.driver(uri, auth=(username, password))

try:
    with driver.session(database="neo4j") as session:
        result = session.run("RETURN 'Connection Successful' AS message")
        print(result.single()["message"])
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    driver.close()
