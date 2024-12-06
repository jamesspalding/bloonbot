import socket

current_round = None
current_cash = None
current_lives = None


#create place to store obtained values
def write_to_file():
    try:
        with open("game_data.txt", "w") as file:
            file.write(f"{current_round}\n")
            file.write(f"{current_cash}\n")
            file.write(f"{current_lives}\n")
    except Exception as e:
        print(f"Error writing to file: {e}")


#update values to be read
def update_variable(var_name, value):
    global current_round, current_cash, current_lives

    if var_name == "round":
        current_round = value
    elif var_name == "cash":
        current_cash = value
    elif var_name == "lives":
        current_lives = value

    write_to_file()


#server to communicate with c#
def start_server(host='127.0.0.1', port=764):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            try:
                conn, _ = s.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        message = data.decode().strip()
                        print(f"Received: {message}")
                        
                        if ":" in message:
                            var_name, value = message.split(":", 1)
                            value = int(value)
                            update_variable(var_name, value)

            except ConnectionResetError as e:
                print(f"Connection reset by client: {e}")
            except Exception:
                ...


if __name__ == "__main__":
    start_server()