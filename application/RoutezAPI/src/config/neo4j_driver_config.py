# from neo4j import GraphDatabase, Driver
from py2neo import Graph, Node, Relationship
import os
from typing import Optional
import threading

class Neo4jSingleton:
    _instance: Optional[Graph] = None
    _lock = threading.Lock()



    @classmethod
    def get_driver(cls) -> Graph:
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')
        print(user, password)
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Graph(
                        "bolt://localhost:7687",  # ou bolt+s://...
                        auth=(user, password),
                    )
        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
