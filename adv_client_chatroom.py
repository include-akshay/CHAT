
from tkinter import *
import socket, threading, json
from tkinter.font import BOLD

root=Tk()
root.title("CHAT")
root.geometry("680x600")
root.resizable(0,0)

#kinter constants
my_font=('SimSun', 14)
black='#010101'
neon_blue='#4D6CFA'
dark_liver='#595457'
light_green="#1fc742"

root.config(bg=black)

class Connection():

    def __init__(self):
        self.encoder='utf-8'
        self.bytesize=1024


## Functions
def connect(connection):
    my_listbox.delete(0, END)

    connection.name=name_entry.get()
    connection.target_ip=ip_entry.get()
    connection.port=port_entry.get()

    try: 
        #create a client socket
        connection.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.client_socket.connect((connection.target_ip, int(connection.port)))


        # receive the initiating message from the server
        message_json=connection.client_socket.recv(connection.bytesize)
        process_message(connection, message_json)
    except:
        my_listbox.insert(0, "Connection was not established ")
    



def disconnect(connection):
    message_packet=create_message("DISCONNECT", connection.name,"I am leaving, tata!!", light_green)
    message_json=json.dumps(message_packet)
    connection.client_socket.send(message_json.encode(connection.encoder))

    gui_end()

def gui_start():

    connect_button.config(state=DISABLED)
    disconnect_button.config(state=NORMAL)
    send_button.config(state=NORMAL)
    name_entry.config(state=DISABLED)
    ip_entry.config(state=DISABLED)
    port_entry.config(state=DISABLED)


def gui_end():
    connect_button.config(state=NORMAL)
    disconnect_button.config(state=DISABLED)
    send_button.config(state=DISABLED)
    name_entry.config(state=NORMAL)
    ip_entry.config(state=NORMAL)
    port_entry.config(state=NORMAL)

def create_message(flag, name,message, color):
    message_packet={
        "flag": flag,
        "name":name,
        "message": message,
        "color":color,
    }
    return message_packet

def process_message(connection, message_json):
    message_packet= json.loads(message_json)
    flag= message_packet["flag"]
    name=message_packet["name"]
    message=message_packet["message"]
    color=message_packet["color"]

    if flag=="INFO":
        
        message_packet=create_message("INFO", connection.name, "Joins the server ", light_green)
        message_json=json.dumps(message_packet)
        connection.client_socket.send(message_json.encode(connection.encoder))

        # enabling GUI for chatting
        gui_start()

        receive_thread=threading.Thread(target=receive_message, args=(connection,))
        receive_thread.start()
    
    elif flag=="MESSAGE":
        # server has sent a msg
        my_listbox.insert(0, f"{name}: {message}")
    
    elif flag=="DISCONNECT":
        my_listbox.insert(0, f"{name} : {message}")
        disconnect(connection)

    else:
        my_listbox.insert(0, "Error while processing the message. ")

def send_message(connection):
    # send msg 
    message_packet=create_message("MESSAGE", connection.name, input_entry.get(), light_green)
    message_json=json.dumps(message_packet)
    connection.client_socket.send(message_json.encode(connection.encoder))

    # clear the input entry
    input_entry.delete(0,END)


def receive_message(connection):
    while True:
        try:
            # receive an incoming packet from the server
            message_json=connection.client_socket.recv(connection.bytesize)
            process_message(connection,message_json)

        except:
            my_listbox.insert(0, "Connection has been closed....Goodbye!! ")
            break

########


###
info_frame=Frame(root, bg=black)
output_frame=Frame(root)
input_frame=Frame(root)
info_frame.pack()
output_frame.pack(pady="5")
input_frame.pack()
####


#info frame
name_label=Label(info_frame,text="Your Name:", font=my_font, fg=light_green, bg=black)
name_entry=Entry(info_frame, font=my_font, borderwidth=3)
ip_label=Label(info_frame, text="HOST IP :", font=my_font, fg=light_green, bg=black)
ip_entry=Entry(info_frame, borderwidth=3, font=my_font)
port_label=Label(info_frame, text="PORT NUM :", font=my_font, fg=light_green, bg=black)
port_entry=Entry(info_frame, borderwidth=3, font=my_font)
connect_button=Button(info_frame, text="CONNECT", font=my_font, bg=light_green, borderwidth=5, width=10, command=lambda:connect(my_connection))
disconnect_button=Button(info_frame, text="DISCONNECT", font=my_font, bg='red', borderwidth=5, width=10, state=DISABLED, command=lambda:disconnect(my_connection))
name_label.grid(row=0, column=0, padx='2', pady='2')
name_entry.grid(row=0, column=1, padx='2', pady='2')
port_label.grid(row=0, column=2, padx='2', pady='2')
port_entry.grid(row=0, column=3, padx='2', pady='2')
ip_label.grid(row=1, column=0, padx='2', pady='2')
ip_entry.grid(row=1, column=1, padx='2', pady='2')
connect_button.grid(row=1, column=2,pady='2')
disconnect_button.grid(row=1, column=3, pady='2')
####


##OUTPUT FRAME

my_scrollbar=Scrollbar(output_frame, orient=VERTICAL)
my_listbox=Listbox(output_frame, height=20, width=50, borderwidth=3, bg=black,fg=light_green, font=my_font, 
            yscrollcommand=my_scrollbar.set)
my_scrollbar.config(command=my_listbox.yview)
my_listbox.grid(row=0, column=0)
my_scrollbar.grid(row=0, column=1, sticky="NS")

########

## INPUT FRAME

input_entry=Entry(input_frame, width=35, borderwidth=3, font=my_font)
send_button=Button(input_frame, text="SEND", borderwidth=5, width =10, font=my_font, bg=light_green, state=DISABLED, command=lambda:send_message(my_connection))
input_entry.grid(row=0, column=0, padx=5, pady=5)
send_button.grid(row=0, column=1, padx=5, pady=5)


#######

my_connection=Connection()
root.mainloop()