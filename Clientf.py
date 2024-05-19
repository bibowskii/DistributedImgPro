import tkinter as tk
from tkinter import filedialog
import socket
import threading
import time
import select
from PIL import Image, ImageTk
import io

# Define server host and port
SERVER_HOST = '34.125.171.68'  # Change this to the server's IP address or hostname
SERVER_PORT = 12345

# Function to handle receiving messages from the server
# def receive_messages(client_socket):
#     try:
#         while True:
#             # Receive message from server
#             message = client_socket.recv(1024).decode()
#             if not message:
#                 break
#             print("\n[Server]:", message)
#     except Exception as e:
#         print("Error occurred while receiving messages:", e)
#     finally:
#         # Close the client socket
#         client_socket.close()

# Function to handle sending image and option to the server
def send_image_and_option(client_socket, image_paths, selected_option):
    try:
            #time.sleep(2)
            #client_socket.shutdown(socket.SHUT_WR)
        client_socket.send(str(selected_option).encode())
        #client_socket.flush()
        ack =client_socket.recv(1024)
        while ack != b'1':
                ack = client_socket.recv(1024)
                time.sleep(0.5)
                print('x',ack)
        print(selected_option)
        print("Option sent successfully.")

        for image_path in image_paths:
            # Send the image file to the server
            try:
                if image_path=="":
                    client_socket.send('endall'.encode())
                    #threading.Thread(target=receive_and_display_images, args=(client_socket, root), daemon=True).start()
                    receive_and_display_images(client_socket,root)
                    return
                    break

                print(image_path)

                client_socket.send(image_path.split('/')[-1].encode())
                print('sent')

                while True:
                 ack = select.select([client_socket], [], [], 1)
                 if ack[0]:
                     data = client_socket.recv(1024)
                     if data == b'ack':
                      print("ACK received.")
                      break
                     else:
                         print(data)
                 else:
                        # Timeout reached, resend data
                        print("Timeout reached. Resending data.")
                        #client_socket.send('x'.encode())
                        client_socket.send(image_path.split('/')[-1].encode())
                #while ack[0] != b'1':
                 #   time.sleep(0.5)
                  #  client_socket.send(image_path.split('/')[-1].encode())
                   # ack = select.select([client_socket], [], [], 1)

                    #print('x', ack)
                print(image_path.encode())
                with open(image_path, 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        client_socket.sendall(data)
                client_socket.send('end'.encode())
                #print(1234456789)
                if client_socket.recv(1024).decode()=='file received':
                 print(f"File '{image_path}' sent successfully.")
                else:
                    print('kosm de mada')
            except Exception as e:
                print(f"Error sending file '{image_path}': {e}")
                return
        client_socket.send('endall'.encode())
        print('555')
        receive_and_display_images(client_socket, root)
        #client_socket.shutdown(socket.SHUT_WR)
        #client_socket.close()


    except Exception as e:
        print("Error occurred while sending image and option:", e)
        return

# Function to handle receiving and displaying images from the server
# Function to handle receiving and displaying images from the server
import os

# Function to handle receiving and displaying images from the server
def receive_and_display_images(client_socket, root):
    try:
        # Get the directory of the current Python script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the file path for saving the image
        image_path = os.path.join(script_dir, 'received_image.jpg')

        while True:
            # Receive image data from the server
            name = client_socket.recv(1024)
            image_data = b''
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                if b'end' in chunk:
                    chunk = chunk[:chunk.index(b'end')]
                    image_data += chunk
                    print('done')
                    print(image_data)
                    # Save the received image
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    print('Saved image')
                    client_socket.send('done'.encode())
                    # Display the received image in the GUI
                    received_image = Image.open(image_path)
                    received_photo = ImageTk.PhotoImage(received_image)
                    received_label = tk.Label(root, image=received_photo)
                    received_label.image = received_photo  # Keep a reference to the image
                    received_label.pack()


                    return
                image_data += chunk

    except Exception as e:
        print("Error occurred while receiving and displaying images:", e)


# Function to handle button click event
def send_data():
    # Get selected option from dropdown menu
    selected_option = option_var.get()

    # Get selected image file paths
    content = file_entry.get(1.0, tk.END)  # Get content of file_entry
    file_paths_list = content.split('\n')  # Split content by newline
    # Remove any empty strings from the list
    file_paths_list = [path for path in file_paths_list if path.strip()]
    # Convert list to tuple
    file_paths_tuple = tuple(file_paths_list)
    image_paths = file_paths_tuple

    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("Connected to server at {}:{}".format(SERVER_HOST, SERVER_PORT))

            # Send images and option to server
            print(image_paths)
            send_image_and_option(client_socket, image_paths, selected_option)

            # Start a thread to receive and display images from the server
            #threading.Thread(target=receive_and_display_images, args=(client_socket, root), daemon=True).start()
        except Exception as e:
            print("Error occurred while connecting to server:", e)

# Function to handle file selection button click event
def browse_file():
    file_paths = filedialog.askopenfilenames()
    file_entry.delete(1.0, tk.END)
    for file_path in file_paths:
        file_entry.insert(tk.END, file_path + '\n')

# Create main window
root = tk.Tk()
root.title("Image and Option Sender")

# Create dropdown menu
options = ["blur", 'edge_detection', 'color_inversion', 'greyscale', 'erosion', 'dilation', 'thresholding',
           'adaptive_thresholding', 'contour_detection']  # Modify this list with your desired options
option_var = tk.StringVar(root)
option_var.set(options[0])  # Set default option
option_menu = tk.OptionMenu(root, option_var, *options)
option_menu.pack()

# Create file selection entry and button
file_entry = tk.Text(root, height=10, width=50)
file_entry.pack()
browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack()

# Create send button
send_button = tk.Button(root, text="Send Data", command=send_data)
send_button.pack()

# Start GUI main loop
root.mainloop()
