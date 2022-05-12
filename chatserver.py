# https://www.neuralnine.com/tcp-chat-in-python/

import socket
import threading
import re

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

#room list
rooms = []

#command functions
def createRoom():
	rooms.append(len(rooms))
	print('Created room', rooms)


def listRooms():
	print('Rooms:')

#command list
commands = {
	'create room': createRoom, 
	'list rooms': listRooms
	}

#send message to all connected clients
def broadcast(message):
	for client in clients:
		client.send(message)

#checking for client messages and removing them
def handle(client):
	while True:
		try:
			message = client.recv(1024)

			#check if order is one of the commands
			order = message.decode('ascii')
			#get first 2 words in text
			check = re.search("\w+ \w+", order)
			if check:
				check = check.group()
				if check in commands:
					commands[check]()
			else:
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