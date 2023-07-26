import psycopg2
from contextlib import closing
from fastapi import HTTPException

class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.config)
        except psycopg2.OperationalError as e:
            raise HTTPException(status_code=500, detail="Database connection error")

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute(self, query, args=None):
        if not self.connection:
            self.connect()

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, args)
            self.connection.commit()
            return cursor.fetchall()

# Load database configuration from config.json
import json
with open("config.json") as f:
    db_config = json.load(f)

db = Database(db_config)
