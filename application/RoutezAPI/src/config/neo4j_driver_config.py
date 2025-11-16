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
        host = os.getenv('DB_HOST', "bolt://neo4jTcc:7687")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Graph(
                        host,
                        auth=(user, password),
                    )
        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance = None
