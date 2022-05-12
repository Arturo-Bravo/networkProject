from http import client
import socket
import threading

name = input("Enter your username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8080))

#listening to server and sending username
def receive():
	while True:
		try:
			message = client.recv(1024).decode('ascii')
			if message == 'namereq':
				client.send(name.encode('ascii'))
			else:
				print(message)
		except:
			print("An error occured.")
			client.close()
			break

def write():
	while True:
		message = '{}: {}'.format(name, input(''))
		client.send(message.encode('ascii'))

receiveThread = threading.Thread(target=receive)
receiveThread.start()

writeThread = threading.Thread(target=write)
writeThread.start()