import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv

class DataAccess:
    def __init__(self):
        load_dotenv()
        dbPath = os.getenv('SQLITE_DB')
        self.conn = sqlite3.connect(dbPath)
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS predictions
            (date TEXT, cityCode TEXT, prediction TEXT)
        ''')
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS actuals
            (date TEXT, cityCode TEXT, actual TEXT)
        ''')
        self.conn.commit()

    def insertPrediction(self, date, cityCode, prediction):
        # check if the prediction is existed by getPredictions
        exitingPrediction = self.getPredictions(date, cityCode)
        if len(exitingPrediction) > 0:
            return

        self.c.execute('''
            INSERT INTO predictions (date, cityCode, prediction)
            VALUES (?, ?, ?)
        ''', (date, cityCode, prediction))
        self.conn.commit()

    def getPredictions(self, date, cityCode):
        query = '''
            SELECT prediction
            FROM predictions
            WHERE date = ? AND cityCode = ?
        '''
        data = pd.read_sql_query(query, self.conn, params=(date, cityCode))
        self.conn.close

        return data
    
    def insertActual(self, date, cityCode, actual):
        # check if the actual is existed by getActuals
        exitingActual = self.getActuals(date, cityCode)
        if len(exitingActual) > 0:
            return

        self.c.execute('''
            INSERT INTO actuals (date, cityCode, actual)
            VALUES (?, ?, ?)
        ''', (date, cityCode, actual))
        self.conn.commit()

    def getActuals(self, date, cityCode):
        query = '''
            SELECT actual
            FROM actuals
            WHERE date = ? AND cityCode = ?
        '''
        data = pd.read_sql_query(query, self.conn, params=(date, cityCode))
        self.conn.close
        return data

    def getResults(self):
        query = '''
            SELECT p.date, p.cityCode, p.prediction, IFNULL(a.actual, '') as actual
            FROM predictions p
            LEFT JOIN actuals a
            ON p.date = a.date AND p.cityCode = a.cityCode
            WHERE p.prediction IS NOT NULL
            ORDER BY p.date DESC
            LIMIT 100
        '''
        data = pd.read_sql_query(query, self.conn)
        self.conn.close

        return data

    def getAllResults(self):
        query = '''
            SELECT p.date, p.cityCode, p.prediction, IFNULL(a.actual, '') as actual
            FROM predictions p
            LEFT JOIN actuals a
            ON p.date = a.date AND p.cityCode = a.cityCode
            WHERE p.prediction IS NOT NULL
        '''
        data = pd.read_sql_query(query, self.conn)
        self.conn.close

        return data

    def __del__(self):
        self.conn.close()
