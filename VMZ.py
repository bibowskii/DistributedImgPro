import socket
import threading
import cv2
import numpy as np
import time
def process_image_func(rimage, process):
    print("starting the process")
    image = cv2.imread(rimage)
    print("image read")
    if process == "blur":
        print("bluring")
        processed_image = cv2.GaussianBlur(image, (5, 5), 0)
    elif process == "edge_detection":
        print("detecting edges")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_image = cv2.Canny(gray, 100, 200)
    elif process == "color_inversion":
        print("color inverting")
        processed_image = cv2.bitwise_not(image)
    elif process == "greyscale":
        print("greyscaling")
        processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif process == "erosion":
        print("erosioning")
        kernel = np.ones((5, 5), np.uint8)
        processed_image = cv2.erode(image, kernel, iterations=1)
    elif process == "dilation":
        print("dilating")
        kernel = np.ones((5, 5), np.uint8)
        processed_image = cv2.dilate(image, kernel, iterations=1)
    elif process == "thresholding":
        print("thresholding")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, processed_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    elif process == "adaptive_thresholding":
        print("thresholfing bardo")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    elif process == "contour_detection":
        print("detecting contours")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        processed_image = cv2.drawContours(image.copy(), contours, -1, (0, 255, 0), 3)
    else:
        print("ana fady")
        print("Invalid process selected.")
        return None
    return processed_image

# Define server host and port
SERVER_HOST = '34.125.171.68'
SERVER_PORT = 12345
def send_back(img):
    client_socket.send(img)
    time.sleep(2)
    print('name sent')
    with open('/home/hotoahmedkware3/processed_image.jpg', 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        client_socket.sendall(data)
                    client_socket.send('end'.encode())
                    print('frk4')
                    if client_socket.recv(1024) == b'done':
                        print('returned to server')
# Function to handle receiving messages from the server
def receive_messages(client_socket):
    try:
         string_message = client_socket.recv(1024).decode()
         print("\n[Server - String Message]:", string_message)
         while True:
            # Receive message type from server

               print('ready')
               message = client_socket.recv(1024)
               print('received',message)
               if message == b'ready?':
                client_socket.send('go'.encode())
                print('go')
                option = client_socket.recv(1024)
                print(option.decode())
                str_message = client_socket.recv(1024)
                print(str_message)
                with open(str_message.decode(), 'wb') as file:
            # Receive the file in chunks
                 while True:
                  data = client_socket.recv(1024)  # Receive 1024 bytes at a time
                  if not data:
                    break  # End of connection

                # Check if the received data contains 'end'
                  if b'end' in data:
                    # Write the data up to the 'end' signal into the file
                     file.write(data[:data.index(b'end')])
                     print('done')
                     client_socket.send('done'.encode())
                     break  # End of file
                  else:
                    # Write the received data into the file
                    file.write(data)
                rr=str_message.decode()
                print(rr)
                pro = process_image_func(rr,option.decode())
                cv2.imwrite('processed_image.jpg',pro) 
                send_back('/home/hotoahmedkware3/processed_image.jpg'.encode()) 
    except Exception as e:
        print("Error occurred while receiving messages:", e)
    finally:
        # Close the client socket
        client_socket.close()
# Connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to server at {}:{}".format(SERVER_HOST, SERVER_PORT))

        # Start a new thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        # Main loop to keep the worker VM running
        while True:
            pass  # Keep the main thread alive
    except Exception as e:
        print("Error occurred while connecting to server:", e)
