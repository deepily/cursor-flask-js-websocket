import requests

from flask import Flask, render_template, request, send_file, url_for
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime

from fifo_queue import FifoQueue
from job import Job
import util_jobs as uj

"""
Globally visible queue object
"""
jobs_todo_queue = FifoQueue()
jobs_done_queue = FifoQueue()

"""
Background Threads
"""
todo_thread = None
done_thread = None
run_thread  = None
thread_lock = Lock()

announcement_delay = 0

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

app.config['SERVER_NAME'] = '127.0.0.1:5000' 


"""
Track the todo Q
"""
def track_todo_thread():

    print("Tracking job TODO queue size...")
    while True:
        
        print( uj.get_current_datetime() )
        socketio.emit('time_update', {"date": uj.get_current_datetime()})

        if jobs_todo_queue.has_changed():

            print( "TODO Q size has changed" )
            socketio.emit('todo_update', {'value': jobs_todo_queue.size()})

            with app.app_context():
                url = url_for('get_audio') + f"?tts_text={jobs_todo_queue.size()} jobs waiting"

            print( f"Emitting TODO url [{url}]..." )
            socketio.emit('audio_update', {'audioURL': url})
            announcement_delay = 2
        else:
            announcement_delay = 0
        # else:
        #     socketio.emit('time_update', {'value': jobs_todo_queue.size(), "date": uj.get_current_datetime()})

        socketio.sleep(2)

"""
Track the done Q
"""
def track_done_thread():

    print("Tracking job DONE queue size...")
    while True:

        print( uj.get_current_datetime() )
        socketio.emit('time_update', {"date": uj.get_current_datetime()})

        if jobs_done_queue.has_changed():

            print( "Done Q size has changed" )
            socketio.emit('done_update', {'value': jobs_done_queue.size()})

            with app.app_context():
                url = url_for('get_audio') + f"?tts_text={jobs_done_queue.size()} jobs finished"

            print( f"Emitting DONE url [{url}]..." )
            socketio.sleep( announcement_delay )
            socketio.emit('audio_update', {'audioURL': url})
        # else:
        #     socketio.emit('no_change', {'value': jobs_done_queue.size(), "date": uj.get_current_datetime()})

        socketio.sleep(3)

def track_running_thread():

    print("Simulating job run execution...")
    while True:
        
        print( "Jobs running @ " + uj.get_current_datetime() )
        
        if not jobs_todo_queue.is_empty():
            
            print( "popping one job from todo Q" )
            job = jobs_todo_queue.pop()
            jobs_done_queue.push( job )

        else:
            print( "no jobs to pop from todo Q " )

        socketio.sleep( 10 )

"""
Serve static files
"""
@app.route('/static/<filename>')
def serve_static(filename):

    return app.send_static_file(filename)

@app.route('/push', methods=['GET'])
def push():

    question = request.args.get('question')
    job = Job(question)
    
    print( job.__str__ )
    
    jobs_todo_queue.push(job)
    return f'Job [{question}] added to queue. queue size [{jobs_todo_queue.size()}]'    

@app.route('/pop', methods=['GET'])
def pop():

    popped_job = jobs_todo_queue.pop()
    return f'Job [{popped_job}] popped from queue. queue size [{jobs_todo_queue.size()}]'
 
@app.route('/get_audio')
def get_audio():

    tts_text = request.args.get('tts_text')
    tts_url  = "http://127.0.0.1:5002/api/tts?text=" + tts_text
    tts_text = tts_text.replace( " ", "+" )

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

    print('Client connected')
    global todo_thread
    with thread_lock:
        if todo_thread is None:
            todo_thread = socketio.start_background_task(track_todo_thread)
            done_thread = socketio.start_background_task(track_done_thread)
            exec_thread = socketio.start_background_task(track_running_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():

    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)