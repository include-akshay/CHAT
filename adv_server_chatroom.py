import tkinter, threading, json, socket
from tkinter import *

root=tkinter.Tk()
root.title("Server")
root.geometry('650x600')
root.resizable(0,0 )

my_font=('SimSun', 14)
black="#010101"
light_green="#1fc742"
root.config(bg=black)


class Connection():

    def __init__(self):
        self.host_ip= socket.gethostbyname(socket.gethostname())
        print(self.host_ip)
        self.encoder='utf-8'
        self.bytesize=1024

        self.client_sockets=[]
        self.client_ips=[]
        self.banned_ips=[]
# fucntion space
def start_server(connection):
     # get port number to run the server on
     connection.port=int(port_entry.get())

     #establishing the connection
     connection.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     connection.server_socket.bind((connection.host_ip, connection.port))
     connection.server_socket.listen()

     #updating GUI
     history_listbox.delete(0, END)
     history_listbox.insert(0, f"Server started on port {connection.port}.")
     end_button.config(state=NORMAL)
     message_button.config(state=NORMAL)
     kick_button.config(state=NORMAL)
     ban_button.config(state=NORMAL)
     self_broadcast_button.config(state=NORMAL)
     start_button.config(state=DISABLED)

     # craete a thread to keep listening for connections from clients
     connect_thread=threading.Thread(target=connect_client, args=(connection,))
     connect_thread.start()


def end_server(connection):
    message_packet=create_message("DISCONNECT", "Admin (Broadcast)", "Server is closing.....Until next time", light_green)
    message_json=json.dumps(message_packet)
    broadcast_message(connection, message_json.encode(connection.encoder))

    #update GUI
    history_listbox.insert(0, f"Server closing on port {connection.port}.")
    end_button.config(state=DISABLED)
    message_button.config(state=DISABLED)
    kick_button.config(state=DISABLED)
    ban_button.config(state=DISABLED)
    self_broadcast_button.config(state=DISABLED)
    start_button.config(state=NORMAL)

    #closing server socket
    connection.server_socket.close()
def connect_client(connection):
    while True:
        try: 
            client_socket, client_address= connection.server_socket.accept()
            if client_address[0] in connection.banned_ips:
                message_packet=create_message("DISCONNECT", "Admin (Private)", "You have been banned... Goodbye", light_green)

                message_json=json.dumps(message_packet)
                client_socket.send(message_json.encode(connection.encoder))
                client_socket.close()

            else :
                message_packet=create_message("INFO","Admin (Private)","Please send your name ", light_green)
                message_json=json.dumps(message_packet)
                client_socket.send(message_json.encode(connection.encoder))

                message_json= client_socket.recv(connection.bytesize)
                process_message(connection, message_json, client_socket, client_address)
        except:
            break

def create_message(flag, name, message, color):
    message_packet={
        "flag": flag,
        "name":name,
        "message": message,
        "color":color,
    }
    return message_packet

def process_message(connection, message_json, client_socket, client_address=(0,0)):
    message_packet= json.loads(message_json)
    flag= message_packet["flag"]
    name=message_packet["name"]
    message=message_packet["message"]
    color=message_packet["color"]

    if flag=="INFO":
        # updating the list we have of client sockets and their IP addresses
        connection.client_sockets.append(client_socket)
        connection.client_ips.append(client_address[0])

        #creating a msg for all the members to know that a new member has arrived.
        message_packet=create_message("MESSAGE", "Admin (Broadcast)", f"{name} has joined the chat. ", light_green)
        message_json=json.dumps(message_packet)
        broadcast_message(connection, message_json.encode(connection.encoder))

        # Putting name and IP of the new member of the chatroom at the server end.
        client_listbox.insert(END, f"Name : {name}        IP Address : {client_address[0]}")

        #Since the connection has been established, we should now be open to receive msgs from the client.
        receive_thread=threading.Thread(target=receive_message, args=(connection, client_socket,))
        receive_thread.start()

    elif flag=="MESSAGE":
        #broadcast the received msg
        broadcast_message(connection, message_json)

        #update server UI
        history_listbox.insert(0, f"{name} : {message}")

    elif flag=="DISCONNECT":
        # close and remove the client socket
        index= connection.client_sockets.index(client_socket)
        connection.client_sockets.pop(index)
        connection.client_ips.pop(index)
        client_listbox.delete(index)

        client_socket.close()

        # alerting all users that a client ahs left
        message_packet=create_message("MESSAGE", "Admin (Broadcast)", f"{name} has let the chatroom !!", light_green)
        message_json= json.dumps(message_packet)
        broadcast_message(connection,message_json.encode(connection.encoder))

        #updating server UI
        history_listbox.insert(0,f"Admin (Broadcast) : {name} has let the chatroom !!")


    else: 
        history_listbox.insert(0, "Error, processing message..")
        


def broadcast_message(connection, message_json):
    for client_socket in connection.client_sockets:
        client_socket.send(message_json)

def receive_message(connection, client_socket):
    while True:
        try:
            message_json=client_socket.recv(connection.bytesize)
            process_message(connection, message_json, client_socket)
        except:
            break


# this broadcast fucntion is for the msgs that are being created by the admin and not by some client
def self_broadcast(connection):
    message_packet=create_message("MESSAGE", "Admin (Broadcast)", input_entry.get(), light_green)
    message_json=json.dumps(message_packet)
    broadcast_message(connection, message_json.encode(connection.encoder))

    #clearing the input entry from teh admin frame.
    input_entry.delete(0, END)

def private_message(connection):
    # select the client from the clientg listbox
    index=client_listbox.curselection()[0]
    client_socket= connection.client_sockets[index]
    
    # create a message packet and send
    message_packet=create_message("MESSAGE", "Admin (PVT.)", input_entry.get(), light_green)
    message_json=json.dumps(message_packet)
    client_socket.send(message_json.encode(connection.encoder))

    #clearing the input entry from teh admin frame.
    input_entry.delete(0, END)

def kick_client(connection):
    index=client_listbox.curselection()[0]
    client_socket= connection.client_sockets[index]

    message_packet=create_message("DISCONNECT", "Admin (PVT.)", "You have been kicked ", light_green)
    message_json=json.dumps(message_packet)
    client_socket.send(message_json.encode(connection.encoder))


def ban_client(connection):
    index=client_listbox.curselection()[0]
    client_socket= connection.client_sockets[index]

    message_packet=create_message("DISCONNECT", "Admin (PVT.)", "You have been banned ", light_green)
    message_json=json.dumps(message_packet)
    client_socket.send(message_json.encode(connection.encoder))

    connection.banned_ips.append(connection.client_ips[index])

# GUI space

connection_frame=tkinter.Frame(root,bg=black)
history_frame=tkinter.Frame(root,bg=black)
client_frame=tkinter.Frame(root,bg=black)
message_frame=tkinter.Frame(root,bg=black)
admin_frame=tkinter.Frame(root,bg=black)

connection_frame.pack(pady=5)
history_frame.pack()
client_frame.pack(pady=5)
message_frame.pack()
admin_frame.pack()

# connection frame layout
port_label=Label(connection_frame,text="Port Number : ", font=my_font, bg=black, fg=light_green)
port_entry=Entry(connection_frame, width=10, borderwidth=3, font=my_font)
start_button=Button(connection_frame, text="Start Server", borderwidth=5, width=15, font=my_font, bg=light_green,
                    command=lambda:start_server(my_connection))
end_button=Button(connection_frame, text="End Server", borderwidth=5, width=15, font=my_font,bg=light_green, state= DISABLED, command=lambda:end_server(my_connection))

port_label.grid(row=0, column=0, padx=5, pady=10)
port_entry.grid(row=0, column=1, padx=5, pady=10)
start_button.grid(row=0, column=2, padx=5, pady=10)
end_button.grid(row=0, column=3, padx=5, pady=10)

# history frame layout

history_scrollbar=Scrollbar(history_frame, orient=VERTICAL)
history_listbox=Listbox(history_frame, height=10, width=55, borderwidth=3, font=my_font, bg=black, fg=light_green, yscrollcommand=history_scrollbar.set)
history_scrollbar.config(command=history_listbox.yview)
history_listbox.grid(row=0, column=0)
history_scrollbar.grid(row=0, column=1, sticky="NS")

#Clinet Frame 
client_scrollbar=Scrollbar(client_frame, orient=VERTICAL)
client_listbox=Listbox(client_frame, height=10, width=55, borderwidth=3, font=my_font, bg=black, fg=light_green, yscrollcommand=client_scrollbar.set)
client_scrollbar.config(command=client_listbox.yview)
client_listbox.grid(row=0, column=0)
client_scrollbar.grid(row=0, column=1, sticky="NS")

# populating msg frame

input_entry=Entry(message_frame, width=40, borderwidth=3, font=my_font)
self_broadcast_button=Button(message_frame, text="Broadcast", width=13, borderwidth=5, bg=light_green, state=DISABLED, command=lambda:self_broadcast(my_connection))

input_entry.grid(row=0, column=0, padx=5, pady=5)
self_broadcast_button.grid(row=0, column=1, padx=5, pady=5)

# admin frame
message_button=Button(admin_frame, text="PVT. MSG.", width=15, borderwidth=5, bg=light_green, state=DISABLED, command=lambda:private_message(my_connection))
kick_button=Button(admin_frame, text="KICK", width=15, borderwidth=5, bg=light_green, state=DISABLED, command=lambda:kick_client(my_connection))
ban_button=Button(admin_frame, text="BAN", width=15, borderwidth=5, bg=light_green, state=DISABLED,command=lambda:ban_client(my_connection))

message_button.grid(row=0, column=0, padx=5, pady=5)
kick_button.grid(row=0, column=1, padx=5, pady=5)
ban_button.grid(row=0, column=2, padx=5, pady=5)

#mainloop

my_connection=Connection()
root.mainloop()