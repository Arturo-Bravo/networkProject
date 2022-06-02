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
#fast access by name
joined = {}
#access by client
joinedFlipped = {}
names = {}

#room list
#rooms are a dictionary of lists
# {roomname: [(client1),(client2)], room2:[(client2)]}
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

#list members in a room
def listMembers(room, client):
	if len(room) == 0:
		client.send('You need to include a room name'.encode('ascii'))
		return
	#room does not exist
	if room not in rooms:
		client.send('Room does not exist'.encode('ascii'))
		return

	client.send(f"{room} members:\n".encode('ascii'))
	count = 0
	for user in rooms[room]:
		count+=1
		member = joinedFlipped[user]
		client.send(f"{member}\n".encode('ascii'))
	client.send(f"Total members: {count}".encode('ascii'))

#leave a room
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
	
#send a message to a specific room
#special case command
def sendRoom(room, message, client):
	if len(room) == 0:
		client.send('You need to include a room name'.encode('ascii'))
		return
	#room does not exist
	if room not in rooms:
		client.send('Room does not exist'.encode('ascii'))
		return

	if client not in rooms[room]:
		client.send('You are not in this room.\n'.encode('ascii'))
		return

	clientName = joinedFlipped[client]
	message = clientName+ ' to ' + room + ':' + message
	for people in rooms[room]:
		if people != client:
			people.send(message.encode('ascii'))

#join multiple rooms
def joinMultiple(roomlist, client):
	roomlist = roomlist.split(',')
	for room in roomlist:
		if room in rooms:
			if client in rooms[room]:
				client.send(f'you are already in this room. {room}\n'.encode('ascii'))
			else:
				rooms[room].append(client)
				client.send(f'Joined room: {room}\n'.encode('ascii'))
		else:
			client.send(f'{room} is not a room.\n'.encode('ascii'))
		

	return


def sendMultiple(roomlist, message, client):
	roomlist = roomlist.strip()
	roomlist = roomlist.split(',')
	for room in roomlist:
		if room in rooms:
			if client in rooms[room]:
				sendRoom(room, message, client)
			else:
				client.send(f'You are not in this room: {room}\n'.encode('ascii'))
		else:
			client.send(f'{room} is not a room.\n'.encode('ascii'))

	return
######################################
#no argument commands
def listRooms(client):
	if len(rooms) == 0:
		client.send('There are no rooms'.encode('ascii'))
		return
	for room in rooms:
		name = room.encode('ascii')
		client.send(name)

def help(client):
	client.send('server help --list commands\n\n'.encode('ascii'))
	client.send('create room (room name) --creates a room with a room name\n\n'.encode('ascii'))
	client.send('list rooms --lists all rooms\n\n'.encode('ascii'))
	client.send('join room (room name) --join room\n\n'.encode('ascii'))
	client.send('leave room (room name) --leave room\n\n'.encode('ascii'))
	client.send('list members (room name) --list members of a certain room\n\n'.encode('ascii'))
	client.send('send (room name) "message" --send a message to a certain room\n\n'.encode('ascii'))
	client.send('join multiple (roomlist) --join multiple rooms at once. rooms are seperated by a comma.\nEx: join multiple room1,room2,room3 \n\n')
	client.send('send multiple (roomlist) "message"--send to multiple rooms at once. rooms are seperated by a comma.\nEx: send multiple multiple room1,room2,room3 "Hello rooms 1-3"\n\n')


#command list
commands = {
	'create room': createRoom,
	'join room': joinRoom,
	'leave room': leaveRoom,
	'list members': listMembers
}

#no argument commands
singleCommands = {
	'list rooms': listRooms,
	'server help': help
}

#send message to all connected clients
def broadcast(message):
	for client in joinedFlipped:
		client.send(message)

#send message to all but the client that is sending
def sending(message, sender):
	for client in joinedFlipped:
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

			#special case commands
			special = re.search(r'\w+ \w+ ".*"', order)
			if special:
				special = special.group()
				args = special.split()
				msg = re.search(r'".*"', special)
				msg = msg.group()
				if args[0] == 'send':
					sendRoom(args[1], msg, client)
					continue

			#join multiple rooms
			joinM = re.search(r'join multiple (\w+,?)*', order)
			if joinM:
				joinM = joinM.group()
				args = joinM.split(' ', 2)[2]
				joinMultiple(args, client)
				continue
			#send a message to multiple rooms
			sendM = re.search(r'send multiple (\w+,?)* ".*"', order)
			if sendM:
				sendM = sendM.group()
				msg = re.search(r'".*"', sendM)
				msg = msg.group()
				#extract the rooms
				sendM = re.sub(r'".*"', '', sendM)
				locations = sendM.split(' ', 2)[2]
				sendMultiple(locations, msg, client)
				continue
				
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

			toDel = client

			nameToRemove = joinedFlipped[client]
			#remove client from all rooms
			for room in rooms:
				if client in rooms[room]:
					rooms[room].remove(client)
			del joined[nameToRemove]
			del joinedFlipped[client]

			client.close()
			broadcast("{} left.".format(nameToRemove).encode('ascii'))
			break


def receive():
	while True:
		#accept connection
		client, address = server.accept()
		print("Connected with {}".format(str(address)))

		#request and store name
		client.send("namereq".encode('ascii'))
		name = client.recv(1024).decode('ascii')

		toAdd = 0
		if name in joined:
			#if name is taken set clients name to chosen name and an increase of integer
			if name in names:
				names[name] = names[name] + 1
				toAdd = names[name]
			else:
				names[name] = 0
			name = name+str(toAdd)
			client.send('nameset'.encode('ascii'))
			#need to receive a message to send again to set the name
			blank = client.recv(1024).decode('ascii')
			client.send(name.encode('ascii'))

		#fast access by name
		joined[name] = client
		#fast access by client
		joinedFlipped[client] = name

		print(joined)

		#broadcast name
		print("Name is {}".format(name))
		broadcast("{} joined.".format(name).encode('ascii'))
		client.send('\nConnected to server'.encode('ascii'))
		client.send('\nFor a list of commands enter: server help\n'.encode('ascii'))

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()


receive()