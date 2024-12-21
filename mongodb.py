from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Use your MongoDB URI
db = client["techiehelp_db"]  # Replace with your database name
collection = db["chat_history"]  # Replace with your collection name

# Store message function
def store_message(query, response):
    message = {
        "query": query,
        "response": response,
        "timestamp": datetime.now()
    }
    collection.insert_one(message)

# Fetch chat history function
def fetch_chat_history():
    # Fetch chat history from the database
    messages = collection.find().sort("timestamp", -1)  # Sorting by timestamp in descending order
    chat_history = [{"query": msg["query"], "response": msg["response"], "timestamp": msg["timestamp"]} for msg in messages]
    return chat_history

# Close MongoDB connection
def close_connection():
    client.close()
