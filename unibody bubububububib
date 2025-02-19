import socket
import threading
import subprocess

# Настройки сервера
HOST = '0.0.0.0'  # Слушаем на всех интерфейсах
PORT = 23          # Порт для Telnet

# Функция для обработки клиента
def handle_client(client_socket):
    print("Клиент подключен")
    client_socket.send(b"Добро пожаловать в Telnet сервер!\n")
    
    while True:
        # Получаем команду от клиента
        command = client_socket.recv(1024).decode('utf-8').strip()
        if command.lower() == 'exit':
            break

        # Выполняем команду и отправляем результат обратно
        try:
            # Используем subprocess для выполнения команды
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            client_socket.send(output + b"\n")
        except subprocess.CalledProcessError as e:
            client_socket.send(f"Ошибка: {e.output.decode('utf-8')}\n".encode('utf-8'))

    client_socket.close()
    print("Клиент отключен")

# Запуск сервера
if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Telnet сервер запущен на {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Подключен клиент: {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()
