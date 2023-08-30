import requests

from flask import Flask, render_template, request, send_file, url_for
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime

from datetime import datetime

"""
First In First Out Queue
"""
class FifoQueue:

    def __init__(self):
        self.queue = []
        self.last_queue_size = 0
        self.push_count = 0

    def push(self, item):
        self.queue.append(item)
        self.push_count += 1

    def get_push_count(self):
        return self.push_count

    def pop(self):
        if not self.is_empty():
            return self.queue.pop( 0 )

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def has_changed(self):
        if self.size() != self.last_queue_size:
            self.last_queue_size = self.size()
            return True
        else:
            return False

"""
Globally visible stack object
"""
job_queue = FifoQueue()

"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

app.config['SERVER_NAME'] = '127.0.0.1:5000' 

"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

"""
Generate random sequence of dummy sensor values and send it to our clients
"""
def background_thread():
    print("Tracking job queue size...")
    while True:
        print( get_current_datetime() )
        if job_queue.has_changed():
            print( "Q size has changed" )
            socketio.emit('time_update', {'value': job_queue.size(), "date": get_current_datetime()})
            with app.app_context():
                url = url_for('get_audio') + f"?tts_text={job_queue.size()} jobs waiting"
            print( f"Emitting url [{url}]..." )
            socketio.emit('audio_file', {'audioURL': url})
        else:
            socketio.emit('no_change', {'value': job_queue.size(), "date": get_current_datetime()})

        socketio.sleep(2)

"""
Serve static files
"""
@app.route('/static/<filename>')
def serve_static(filename):

    return app.send_static_file(filename)

@app.route('/push', methods=['GET'])
def push():

    job_name = request.args.get('job_name')
    print( job_name )
    job_name = f'{job_queue.get_push_count() + 1 }th job: {job_name}'
    
    job_queue.push(job_name)
    return f'Job [{job_name}] added to stack. Stack size [{job_queue.size()}]'    

@app.route('/pop', methods=['GET'])
def pop():

    popped_job = job_queue.pop()
    return f'Job [{popped_job}] popped from stack. Stack size [{job_queue.size()}]'
 
@app.route('/get_audio')
def get_audio():

    tts_text = request.args.get('tts_text')
    tts_url  = "http://127.0.0.1:5002/api/tts?text=" + tts_text

    print( "Fetching:", tts_url )
    response = requests.get(tts_url)
    path     = "audio/tts.wav"

    # Check if the request was successful
    if response.status_code == 200:
        # Write the content of the response to a file
        with open( path, 'wb') as audio_file:
            audio_file.write(response.content)
        # return path
    else:
        print(f"Failed to get UPDATED audio file: {response.status_code}")
        # return None

    return send_file( path, mimetype='audio/wav')

"""
Decorator for connect
"""
@socketio.on('connect')
def connect():

    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():

    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)