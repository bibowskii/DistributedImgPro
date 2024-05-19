import socket
import threading
import queue
from PIL import Image
import os
import time

HOST = '0.0.0.0'
PORT = 12345

connections = []
connections_status = []

worker_slave_ips = ['34.16.168.219', '34.16.234.194']
received_picture_queue = queue.Queue()

total_images = 0
images_received = 0
def send_back(img,client_socket):
    client_socket.send(img.encode())
    time.sleep(2)
    print('name sent')
    with open(img, 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        client_socket.sendall(data)
                    client_socket.send('end'.encode())
                    print('frk4')
                    if client_socket.recv(1024) == b'done':
                        print('returned to client')


def handle_client(connection, client_address):
    global total_images
    global images_received

    try:
        print("Connected to regular client:", client_address)
        option = connection.recv(1024)
        print(option.decode()+'\n')
        connection.send('1'.encode())
    except Exception as e:
        print(f"Error  '{option}': {e}")
        return

    while True:
        save_path = '/home/hotoahmedkware3/'
        filename = connection.recv(1024)

        while filename[-4:] != b'.jpg':
            if b'endall' in filename or not filename:
                print('received all')
                total_images = images_received
                distribute_images_to_workers(option,connection)
                return
            filename = connection.recv(1024)

        connection.send('ack'.encode())
        print('ack sent')

        if b'endall' in filename or not filename:
            print('received all')
            break

        print(filename)
        save_path += filename.decode()

        with open(save_path, 'wb') as file:
            while True:
                data = connection.recv(1024)
                if not data:
                    break

                if b'end' in data:
                    file.write(data[:data.index(b'end')])
                    break
                else:
                    file.write(data)

        print("File received successfully.", save_path)
        connection.send('file received'.encode())
        images_received += 1
        received_picture_queue.put(save_path)

def slavery(img,option,connection):
    for i, conn in enumerate(connections):
        if connections_status[i] == 'free':
            print("Sending image to VM:", worker_slave_ips[i])
            connections_status[i] = 'busy'  # Update VM status to busy
            conn.send('ready?'.encode())
            print('ready sent')
            if conn.recv(1024) == b'go':
                conn.send(option)
                time.sleep(0.5)
                conn.send(img.encode())
                time.sleep(0.5)
                with open(img, 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        conn.sendall(data)
                conn.send('end'.encode())
                if conn.recv(1024) == b'done':
                    print('File received successfully')
                    time.sleep(0.5)
                    time.sleep(0.5)
                    str_message = conn.recv(1024)
                    print('circ',str_message)
                    path ='/home/hotoahmedkware3/pre.jpg'
                    with open(path, 'wb') as file:
            # Receive the file in chunks
                     while True:
                      data = conn.recv(1024)  # Receive 1024 bytes at a time
                      if not data:
                        break  # End of connection

                # Check if the received data contains 'end'
                      if b'end' in data:
                    # Write the data up to the 'end' signal into the file
                       file.write(data[:data.index(b'end')])
                       print('done')
                       conn.send('done'.encode())
                       break  # End of file
                      else:
                    # Write the received data into the file
                       file.write(data)
                    print('circulated')
                    connections_status[i] = 'free'
                    send_back(path,connection)
                    return
            else:
                print("VM is not ready, marking as busy")
                connections_status[i] = 'busy'  # Update VM status to busy if it's not ready

def handle_worker_slave(connection, client_address):
    print("Connected to worker-slave VM:", client_address)
    try:
        welcome_message = "Welcome, worker-slave VM!"
        connection.sendall(welcome_message.encode())
    except Exception as e:
        print("Error occurred while handling worker-slave VM {}: {}".format(client_address, e))



def distribute_images_to_workers(option,connection):
    while images_received < total_images:
        time.sleep(1)
    while not received_picture_queue.empty():
        img = received_picture_queue.get()
        print(img)
        while True:
            # Check if any VM is free
            if 'free' in connections_status:
                # At least one VM is free, distribute the image
                threading.Thread(target=slavery, args=(img,option,connection,)).start()
                break
            else:
                # All VMs are busy, wait for a short period before checking again
                print('no free')
                time.sleep(1)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Server is listening on {}:{}".format(HOST, PORT))

    while True:
        connection, client_address = server_socket.accept()
        if client_address[0] in worker_slave_ips:
            connections.append(connection)
            connections_status.append('free')
            worker_slave_thread = threading.Thread(target=handle_worker_slave, args=(connection, client_address))
            worker_slave_thread.start()
        else:
            client_thread = threading.Thread(target=handle_client, args=(connection, client_address))
            client_thread.start()

    distribution_thread = threading.Thread(target=distribute_images_to_workers)
    distribution_thread.start()
