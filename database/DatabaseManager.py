import sqlite3
import os
from tools import genarate_session_id, generate_keys
import time

def build_database():
    #Checks if the database does not already exist
    if (os.path.isfile("database/database.db")):
        return
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS connections (session BIGINT, ip TEXT, stime BIGINT, rtime BIGINT, publickey TEXT, privatekey TEXT)")
    conn.commit()
    conn.close()

def new_connection(ip):
    # Adds a new connection to the conenctions database
    #fields added are
    #session ID, IP Address, epoch time, time since last request, public key of current step.
    # Here session ID is the primary key
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    publickey,privatekey = generate_keys()
    session = genarate_session_id()
    cursor.execute("INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?)", (session, ip, int(time.time()), int(time.time()), publickey,privatekey))
    conn.commit()
    conn.close()
    return session,publickey

def check_request(session, publickey):
    #Checks if the session ID and public key match
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM connections WHERE session = ?", (session,))
    data = cursor.fetchall()
    if (len(data) == 0):
        return -1
    if (data[0][4] != publickey):
        return -1
    #check if the time since last request is less than 3 seconds
    if (int(time.time()) - data[0][3] < 3):
        return 0
    #check if the time since sessionId creation is greater than 20 minutes
    if (int(time.time()) - data[0][2] > 1200):
        return 0
    conn.commit()
    conn.close()
    return 1

def remove_invalid_session(session):
    #Removes the session from the database
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM connections WHERE session = ?", (session,))
    conn.commit()
    conn.close()

def new_request(session):
    #Updates the time since last request
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    publickey,privatekey = generate_keys()
    cursor.execute("UPDATE connections SET rtime = ?, publickey = ?, privatekey = ? WHERE session = ?", (int(time.time()), publickey, privatekey, session))
    conn.commit()
    conn.close()
    return publickey