import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    connection = get_db_connection()
    post = get_post(post_id)
    article = connection.execute("SELECT title FROM posts WHERE id=?", (post_id,)).fetchone()
    connection.close()
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    if post is None:
      logging.info(f"{current_time_str} 404 Not found article id: {post_id}")
      return render_template('404.html'), 404
    else:
      logging.info(f"{current_time_str} Retrieved existing article: {article[0]}")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"{current_time_str} The 'About Us' page is retrieved")
    return render_template('about.html')

connection_count = 0
@app.before_request
def before_request():
    global connection_count
    connection_count += 1

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    global connection_count
    response = {
        "db_connection_count": connection_count,
        "post_count": post_count
    }
    connection.close()
    return jsonify(response), 200

@app.route('/healthz')
def healthz():
    response = {
        "result": "OK - healthy"
    }
    return jsonify(response), 200

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            current_time = datetime.datetime.now()
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"{current_time_str} new article is created: {title}")
            return redirect(url_for('index'))
    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
