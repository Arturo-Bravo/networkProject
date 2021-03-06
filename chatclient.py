from http import client
import socket
import threading

name = input("Enter your username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8080))

#listening to server and sending username
def receive():
	global name
	while True:
		try:
			message = client.recv(1024).decode()
			if message == 'namereq':
				client.send(name.encode())
			elif message == 'nameset':
				#send to clear the socket or something, this works
				client.send('nothing'.encode())
				message = client.recv(1024).decode()
				name = message
				print("Your name ", name)
				continue
			else:
				print(message)
		except:
			print("An error occured.")
			client.close()
			break

#send messages to server
def write():
	while True:
		message = input('')
		message = name + ': ' + message
		client.send(message.encode())

receiveThread = threading.Thread(target=receive)
receiveThread.start()

writeThread = threading.Thread(target=write)
writeThread.start()