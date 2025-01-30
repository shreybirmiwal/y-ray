from neo4j import GraphDatabase

uri = "neo4j+ssc://9d301e76.databases.neo4j.io"
username = "neo4j"
password = "RIcw8qhANmE1GG4AURd29ii9B91l8SM82j2tcaXiWTU"

driver = GraphDatabase.driver(uri, auth=(username, password))

try:
    with driver.session(database="neo4j") as session:
        result = session.run("RETURN 'Connection Successful' AS message")
        print(result.single()["message"])
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    driver.close()
