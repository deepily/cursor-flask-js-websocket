import json
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
jobs_run_queue  = FifoQueue()

"""
Background Threads
"""
clock_thread = None
run_thread   = None
thread_lock  = Lock()
# Track the number of jobs we've pushed into the queue
push_count  = 1

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

app.config['SERVER_NAME'] = '127.0.0.1:5000' 


"""
Track the todo Q
"""
def clock_thread():

    print("Tracking job TODO queue size...")
    while True:
        
        # print( uj.get_current_datetime() )
        socketio.emit('time_update', {"date": uj.get_current_datetime()})
        socketio.sleep(1)

def track_running_thread():

    print("Simulating job run execution...")
    while True:
        
        print( "Jobs running @ " + uj.get_current_datetime() )
        
        if not jobs_todo_queue.is_empty():
            
            print( "popping one job from todo Q" )
            job = jobs_todo_queue.pop()
            socketio.emit('todo_update', {'value': jobs_todo_queue.size()})

            jobs_run_queue.push( job )
            socketio.emit('run_update', {'value': jobs_run_queue.size()})

            print("Executing job... " )
            # Point to (NOT pop) the job at the head of the queue
            running_job = jobs_run_queue.head()

            socketio.sleep( 5 )
            
            running_job.complete( "I don't know, beats the hell out of me!" )
            print("Executing job... Done!")
            print( running_job.to_json() )
            
            jobs_run_queue.pop()
            socketio.emit('run_update',  {'value': jobs_run_queue.size()})
            jobs_done_queue.push(running_job)
            socketio.emit('done_update', {'value': jobs_done_queue.size()})


            with app.app_context():
                url = url_for('get_audio') + f"?tts_text=1 job finished. {running_job.question}? {running_job.answer}"
            print( f"Emitting DONE url [{url}]..." )
            socketio.emit('audio_update', {'audioURL': url})


        else:
            print( "no jobs to pop from todo Q " )
            socketio.sleep( 5 )

"""
Serve static files
"""
@app.route('/static/<filename>')
def serve_static(filename):

    return app.send_static_file(filename)

@app.route('/push', methods=['GET'])
def push():

    global push_count

    question = request.args.get('question')
    job = Job(push_count, question)
    push_count += 1
    
    print( job.to_json() )
    
    # Only notify the poster if there are jobs ahead of them in the todo Q
    if jobs_todo_queue.size() != 0:    
    
        # Generate plurality suffix
        suffix = "s" if jobs_todo_queue.size() > 1 else ""
        with app.app_context():
                url = url_for('get_audio') + f"?tts_text={jobs_todo_queue.size()} job{suffix} before this one"
        print( f"Emitting TODO url [{url}]..." )
        socketio.emit('audio_update', {'audioURL': url})

    jobs_todo_queue.push(job)
    socketio.emit('todo_update', {'value': jobs_todo_queue.size()})

    return f'Job [{question}] added to queue. queue size [{jobs_todo_queue.size()}]'    

# Rethink how we're killing/poppng jobs in the todo queue
# @app.route('/pop', methods=['GET'])
# def pop():

#     popped_job = jobs_todo_queue.pop()
#     return f'Job [{popped_job}] popped from queue. queue size [{jobs_todo_queue.size()}]'
 
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

# COPILOT: Given a queue, generate a list of HTML elements
def generate_html_list(fifo_queue, descending=False):
    
    html_list = []
    for job in fifo_queue.queue:
        html_list.append( job.get_html() )
    
    if descending:
        html_list.reverse()
    
    return html_list

@app.route('/get_queue/<queue_name>', methods=['GET'])
def get_queue(queue_name):

    if queue_name == "todo":
        jobs = generate_html_list( jobs_todo_queue, descending=True )
    elif queue_name == "done":
        jobs = generate_html_list( jobs_done_queue, descending=True )
    elif queue_name == "run":
        jobs = generate_html_list( jobs_run_queue )        
    else:
        return json.dumps({"error": "Invalid queue name. Please specify either 'todo' or 'done'."})

    return json.dumps({f"{queue_name}_jobs": jobs})


"""
Decorator for connect
"""
@socketio.on('connect')
def connect():

    print('Client connected')
    global clock_thread
    with thread_lock:
        if clock_thread is None:
            clock_thread = socketio.start_background_task(clock_thread)
            exec_thread = socketio.start_background_task(track_running_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():

    print('Client disconnected',  request.sid)

if __name__ == '__main__':

    socketio.run(app, debug=True)
