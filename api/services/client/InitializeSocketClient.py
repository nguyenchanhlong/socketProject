import sys
import os
import threading

import jwt


# Get the absolute path of the directory containing InitializeSocketClient.py
current_directory = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory by going up multiple levels
parent_directory = os.path.abspath(os.path.join(current_directory, '../../../'))

# Add the parent directory to the Python path
sys.path.append(parent_directory)

# Now you can import settings
from settings import settings
import socket
from api.handlers.AuthenticationHandler.AuthHandle import AuthHandle


class SocketClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((settings.SERVER_HOST, settings.SERVER_PORT))
        print("Connected to server.")

    @staticmethod
    def auth_token(accessToken):
        get_auth_token = AuthHandle(accessToken).getAccessToken()
        while True:
            try:
                if get_auth_token['authToken'] == accessToken:
                    token_bytes = accessToken.encode('utf-8')
                    if not token_bytes:
                        print("Wrong structure of Access Token!!! Please check your token and try again.")
                    else:
                        # Decode the token using the bytes type for the secret key
                        a = jwt.decode(token_bytes, settings.AUTH_SECRET_KEY.encode('utf-8'), algorithms=['HS256'])
                        return "Authenticated, login successful!!!"
                else:
                    print("Authenticated, login failed.")
                    break
            except Exception as e:
                print("Error: ", e)
                break

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    if ":" in data:
                        address_parts = data.split(":")
                        if len(address_parts) == 2:
                            port_number = address_parts[1].strip()
                            message = address_parts[0].strip()
                            print("Received from user ({}): {}".format(port_number, message))

            except Exception as e:
                print("Error receiving message:", e)
                break

    def send_message(self):
        while True:
            try:
                message = input("")
                self.client_socket.sendall(message.encode())

            except Exception as e:
                print("Error sending message:", e)
                break

    def start(self):
        accessToken = input("Please input the Access Token: ")
        token = SocketClient.auth_token(accessToken=accessToken)
        if token == "Authenticated, login successful!!!":
            send_thread = threading.Thread(target=self.send_message)
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()
            send_thread.start()
        else:
            print("Authentication failed.")


client = SocketClient()
client.start()