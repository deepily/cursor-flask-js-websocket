# Flask SocketIO Demo

This is a simple client-server application built using a browser-based JavaScript client and a RESTful Flask service. The application allows you to post text from the client to the server, and echoes that text back to the JavaScript client via a persistent web socket connection.

## Project Structure

The project has the following structure:

- `server.py`: This is the main server file that handles the client requests and websocket connections.
- `requirements.txt`: This file lists all the Python dependencies that need to be installed.
- `static/index.html`: This is the main HTML file that the user interacts with.
- `static/js/main.js`: This file contains the JavaScript code for handling user input and websocket communication.
- `static/css/styles.css`: This file contains the CSS styles for the HTML elements.
- `README.md`: This file.

## Setup and Run

1. Clone this repository.
2. Install the dependencies by running `pip install -r requirements.txt`.
3. Run the server by executing `python clock.py`.
4. Open your web browser and navigate to `http://localhost:5000`.

## Usage

1. Enter your text in the input field and click 'Send'.
2. The server will echo your message and it will be displayed in the 'messages' section.

## Dependencies

- Flask==2.1.3
- Flask-SocketIO==5.0.1
- eventlet==0.30.2
- Werkzeug==2.0.3

## License

This project is licensed under the terms of the MIT license.
