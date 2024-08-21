import socket

HOST = '127.0.0.1'
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# send_data = 'stop_conveyor'
send_data = 'activate_conveyor'

print('send: ' + send_data)
client_socket.send(send_data.encode())

recv_indata = client_socket.recv(1024)
print('recv: ' + recv_indata.decode())

client_socket.close()
