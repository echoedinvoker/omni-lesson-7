import socket
import threading

def start_server_socket(host, port, db):
    state = db.per_instance_state

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    server_socket.settimeout(1)

    while state.socket_flag:
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue
        recv_data = conn.recv(1024)
        recv_data = recv_data.decode('utf-8')
        print(f"Received data: {recv_data}")

        if recv_data == "stop_conveyor":
            state.stop_conveyor_flag = True
        elif recv_data == "activate_conveyor":
            state.activate_conveyor_flag = True

        conn.send(recv_data.encode())
        conn.close()

def setup(db: og.Database):
    state = db.per_instance_state

    state.host = "0.0.0.0"
    state.port = 3000
    state.socket_flag = False
    state.server_socket_thread = None
    
    state.stop_conveyor_flag = False
    state.activate_conveyor_flag = False

def cleanup(db: og.Database):
    pass

def compute(db: og.Database):
    state = db.per_instance_state

    if state.socket_flag == False:
        state.socket_flag = True
        state.server_socket_thread = threading.Thread(target=start_server_socket, args=(state.host, state.port, db))
        state.server_socket_thread.start()

    if state.stop_conveyor_flag:
        db.outputs.is_stop = True
        state.stop_conveyor_flag = False
    else:
        db.outputs.is_stop = False

    if state.activate_conveyor_flag:
        db.outputs.is_activate = True
        state.activate_conveyor_flag = False
    else:
        db.outputs.is_activate = False

    return True

