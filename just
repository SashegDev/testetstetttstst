import socket
import threading
import subprocess

# Server settings
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 23          # Port for Telnet

# Function to handle client connections
def handle_client(client_socket):
    print("Client connected")
    client_socket.send(b"Welcome to the Telnet server!\n")
    
    while True:
        # Receive command from client
        command = client_socket.recv(1024).decode('latin-1').strip()
        if command.lower() == 'exit':
            break

        if not command:  # Check for empty command
            client_socket.send(b"Error: Empty command\n")
            continue

        # Execute the command and send the result back
        try:
            # Use subprocess to execute the command
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            client_socket.send(output.decode('latin-1') + b"\n")
        except subprocess.CalledProcessError as e:
            client_socket.send(f"Error: Command '{command}' exited with code {e.returncode}\n".encode('latin-1'))

    client_socket.close()
    print("Client disconnected")

# Start the server
if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Telnet server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected client: {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()
