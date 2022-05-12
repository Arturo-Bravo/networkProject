# https://www.neuralnine.com/tcp-chat-in-python/

import socket
import threading

#connection
host = '127.0.0.1'
port = 8080

#server
#AF_INET is internet socket, SOCK_STREAM means use TCP not UDP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

#client list
clients = []
nicknames = []

#send message to all connected clients
def broadcast(message):
	for client in clients:
		client.send(message)

#checking for client messages and removing them
def handle(client):
	while True:
		try:
			message = client.recv(1024)
			broadcast(message)
		except:
			index = clients.index(client)
			clients.remove(client)
			client.close()
			nickname = nicknames[index]
			broadcast("{} left.".format(nickname).encode('ascii'))
			nicknames.remove(nickname)
			break


def receive():
	while True:
		#accept connection
		client, address = server.accept()
		print("Connected with {}".format(str(address)))

		#request and store name
		client.send("namereq".encode('ascii'))
		name = client.recv(1024).decode('ascii')
		nicknames.append(name)
		clients.append(client)

		#broadcast name
		print("Name is {}".format(name))
		broadcast("{} joined.".format(name).encode('ascii'))
		client.send('Connected to server'.encode('ascii'))

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()


receive()