import socket
import select
import errno
import sys
HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

my_username = input("Username: ")

# Stworz socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Polaczenie z odpowiednim serwerem
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# Prepare username and header and send them
# serializacja uzytkownika
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
while True:
    # user wpisuje wiadomosc
    message = input(f'{my_username} > ')
    if message:
        # serializacja wiadomosci
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            # If - jesli brak wiadomosci,lub inny przypadek gdzie uzytkownik wychodzi
            if not len(username_header):
                print('Polaczenie zerwane')
                sys.exit()
            # konwersja na int
            username_length = int(username_header.decode('utf-8').strip())
            # deserializacja nazwy uzytkownika
            username = client_socket.recv(username_length).decode('utf-8')
            # to samo dla wiadomosci
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            # print wiadomosci
            print(f'{username} > {message}')
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            continue
    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()