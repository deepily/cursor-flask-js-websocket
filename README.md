# Flask SocketIO Demo

This is a simple client-server application built using a browser-based JavaScript client and a RESTful Flask service. The application allows you to push & pop jobs from the client to/from the server's fifo queue. Whenever the queue is changed the status is pushed to the JavaScript client via a persistent web socket connection.

## Project Structure

The project has the following structure:

- `clock.py`: This is the main server file that handles the client requests and websocket connections.
- `requirements.txt`: This file lists all the Python dependencies that need to be installed.
- `static/clock.html`: This is the main HTML file that the user interacts with.
- `README.md`: This file.

## Setup and Run

1. Clone this repository.
2. Install the dependencies by running `pip install -r requirements.txt`.
3. Run the server by executing `python clock.py`.
4. Open your web browser and navigate to `http://127.0.0.1:5000/static/clock.html`.

## Usage

1. Push your latest job text via http://127.0.0.1:5000/push?job_name=
2. Pop the first job from the queue using: http://127.0.0.1:5000/pop
3. The server will push updates to the client fifo queue (http://localhost:5000/clock) and updates will be displayed in the client's clock and Q state divs .

## Dependencies

- Flask==2.1.3
- Flask-SocketIO==5.0.1
- eventlet==0.30.2
- Werkzeug==2.0.3
- requests==2.31.0

## Special Permissions
Firefox doesn't allow autoplay of media w/in a webpage without explicitly setting and allow all switch: https://support.mozilla.org/en-US/kb/block-autoplay

Firefox extensions can, however, do autoplay because the following configurations flag defaults to true: `media.autoplay.allow-extension-background-pages`

## License

This project is licensed under the terms of the MIT license.
