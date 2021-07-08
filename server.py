import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Stworz socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

# Tu nasluchuje do nowych polaczen
server_socket.listen()

# Lista socketow dla select.select()
sockets_list = [server_socket]

# Lista polaczonych klientow
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Odbior wiadomosci
def receive_message(client_socket):

    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        #jesli nie otrzymamy zadnej wiadomosci
        if not len(message_header):
            return False
        # Konwersja headera do int
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        #w sytuacji jakiegokolwiek bledu i wyjscia klienta
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        # nowe polaczenie, zaakceptowanie
        if notified_socket == server_socket:
            # unikalny socket klienta, dodatkowo zwraca ip/port
            client_socket, client_address = server_socket.accept()
            # ustawienie nazwy uzytkownika
            user = receive_message(client_socket)
            # jesli uzytkownik rozlaczy sie przed ustawieniem nazwy
            if user is False:
                continue
            # jesli uzytkownik przekroczy maxymalna ilosc dozwolonych uzytkownikow
            elif len(sockets_list) == 3:
                continue
            # dodaj zaakceptowany socket do select.select
            sockets_list.append(client_socket)
            # zapisz nazwe uzytkownika
            clients[client_socket] = user
            print('Zaakceptowano polaczenie z {}:{}, uzytkownik: {}'.format(*client_address, user['data'].decode('utf-8')))
        #Else - istniejacy socket wysyla wiadomosc
        else:
            # otrzymuje wiadomosc
            message = receive_message(notified_socket)
            # klient rozlaczony
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            # identyfikacja usera
            user = clients[notified_socket]
            print(f'Wiadomosc od {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            for client_socket in clients:
                if client_socket != notified_socket:
                    # Wyslij usera i wiadomosc
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])