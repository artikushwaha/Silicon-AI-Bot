from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from CRWALER import crawl_website
from Retriever import create_index, search_query
import mysql.connector
import requests

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="12345678",
        database="silicon_coders"
    )

crawled_data = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/crawl', methods=['POST'])
def crawl():
    base_url = request.form['base_url']
    global crawled_data
    crawled_data = crawl_website(base_url)
    print(crawled_data)

    save_crawled_data_to_db(crawled_data)
    create_index(crawled_data)
    return render_template('/templates/index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    question = request.json['question']
    results = search_query(question)
    response = [{'url': result['url'], 'content': result['content']} for result in results]
    return jsonify(response), 200

def save_crawled_data_to_db(crawled_data):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crawled_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url TEXT,
        content TEXT
    )
    ''')

    # Chunk data and insert into database
    for url, content in crawled_data.items():
        chunk_size = 1000  # Adjust the chunk size as needed
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
        for chunk in chunks:
            cursor.execute("INSERT INTO crawled_data (url, content) VALUES (%s, %s)", (url, chunk))

    connection.commit()
    cursor.close()
    connection.close()

GEMINI_API_URL = "https://api.gemini.ai/your-endpoint"
API_KEY = "AIzaSyBJl7CWyX24V-8X-WnBGuK-nFyHAD5z3a8"  # Your Gemini API key

def query_gemini_ai(prompt):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        "prompt": prompt,
        "data": get_data_from_db()  # Get data from your database if needed
    }
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    return response.json()

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    prompt = f"User: {user_input}\nAI:"
    ai_response = query_gemini_ai(prompt)
    return jsonify({"response": ai_response.get('result', 'No response received')})

def get_data_from_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT content FROM crawled_data")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return [row[2] for row in results]

if __name__ == '__main__':
    app.run(debug=True)
