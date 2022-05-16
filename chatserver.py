#  used this for the first commit to get started https://www.neuralnine.com/tcp-chat-in-python/

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
rooms = {}

#command functions
def createRoom(name, client):
	if len(name) == 0:
		client.send('You need to include a room name'.encode('ascii'))
	elif name in rooms:
		client.send("Room already exists".encode('ascii'))
	else:
		rooms[name] = []
		rooms[name].append(client)
		client.send("Created room {}".format(name).encode('ascii'))

def joinRoom(name, client):
	if len(name) == 0:
		client.send('You need to include a room name'.encode('ascii'))
		return
	#room does not exist
	if name not in rooms:
		client.send('Room does not exist'.encode('ascii'))
		return
	#if attempting to join a room you already are in
	if client in rooms[name]:
		client.send('You are already in this room.'.encode('ascii'))
		return
	rooms[name].append(client)
	client.send("Joined room {}".format(name).encode('ascii'))

def leaveRoom(name, client):
	if len(name) == 0:
		client.send('You need to include a room name'.encode('ascii'))
		return
	#room does not exist
	if name not in rooms:
		client.send('Room does not exist'.encode('ascii'))
		return
	#if attempting to leave a room you are not in
	if client not in rooms[name]:
		client.send('You are not in this room.'.encode('ascii'))
		return
	rooms[name].remove(client)
	print(client)
	client.send("Left room {}".format(name).encode('ascii'))
	

#no argument commands
def listRooms(client):
	if len(rooms) == 0:
		client.send('There are no rooms'.encode('ascii'))
		return
	for room in rooms:
		name = room.encode('ascii')
		client.send(name)

def help(client):
	client.send('create room (room name) --creates a room with a room name'.encode('ascii'))
	client.send('list rooms --lists all rooms'.encode('ascii'))


#command list
commands = {
	'create room': createRoom,
	'join room': joinRoom,
	'leave room': leaveRoom
}

#no argument commands
singleCommands = {
	'list rooms': listRooms
}

#send message to all connected clients
def broadcast(message):
	for client in clients:
		client.send(message)

#send message to all but 1 client
def sending(message, sender):
	for client in clients:
		if client != sender:
			client.send(message)
		else:
			client.send('Message sent'.encode('ascii'))

#checking for client messages and removing them
def handle(client):
	while True:
		try:
			message = client.recv(1024)

			#check if order is one of the commands
			order = message.decode('ascii')
			#get first 3 words in text
			check = re.search(r'\w+ \w+ \w+', order)
			#get first 2 words
			single = re.search(r'\w+ \w+', order)
			#if there is a formatted command
			if check:
				check = check.group()
				args = check.split()
				func = args[0] + ' ' + args[1]
				#if it is a valid command
				if func in commands:
					#call the appropiate function
					commands[func](args[2], client)
				else:
					sending(message, client)
			#check for single commands
			elif single:
				single = single.group()
				if single in singleCommands:
					singleCommands[single](client)
				#if command is being called incorrectly let the command handle the error message
				elif single in commands:
					commands[single]("", client)
				else:
					sending(message, client)
			else:
				sending(message, client)
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
		client.send('\nConnected to server'.encode('ascii'))

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()


receive()