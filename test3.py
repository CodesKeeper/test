import socket
import threading


class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # 存储客户端连接：{'main': conn, 'secondary': conn}

    def start(self):
        # 绑定并开始监听
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)  # 最多允许2个客户端连接
        print(f"服务器启动，监听 {self.host}:{self.port}...")

        # 等待主客户端和副客户端连接
        self.wait_for_clients()

    def wait_for_clients(self):
        while len(self.clients) < 2:
            conn, addr = self.server_socket.accept()
            print(f"新连接来自 {addr}")

            # 询问客户端类型
            conn.send("请输入客户端类型 (main/secondary): ".encode('utf-8'))
            client_type = conn.recv(1024).decode('utf-8').strip().lower()

            if client_type in ['main', 'secondary'] and client_type not in self.clients:
                self.clients[client_type] = conn
                conn.send(f"已成功注册为{client_type}客户端！".encode('utf-8'))
                print(f"{client_type}客户端已连接")

                # 启动线程处理该客户端的消息
                threading.Thread(target=self.handle_client, args=(client_type, conn), daemon=True).start()
            else:
                conn.send("客户端类型无效或已被占用，请重试！".encode('utf-8'))
                conn.close()

        # 通知双方连接已就绪
        self.clients['main'].send("副客户端已连接，现在可以开始通信了！".encode('utf-8'))
        self.clients['secondary'].send("主客户端已连接，现在可以开始通信了！".encode('utf-8'))

    def handle_client(self, client_type, conn):
        """处理客户端发送的消息并转发给另一方"""
        other_type = 'secondary' if client_type == 'main' else 'main'

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                print(f"收到{client_type}客户端消息: {message}")

                # 转发给另一个客户端
                if other_type in self.clients:
                    self.clients[other_type].send(f"来自{client_type}客户端: {message}".encode('utf-8'))
                else:
                    conn.send("目标客户端未连接！".encode('utf-8'))

                # 退出命令
                if message.lower() == 'exit':
                    break

        except ConnectionResetError:
            print(f"{client_type}客户端连接被重置")
        finally:
            print(f"{client_type}客户端断开连接")
            conn.close()
            del self.clients[client_type]
            # 如果还有其他客户端，通知其连接已断开
            if other_type in self.clients:
                self.clients[other_type].send(f"{client_type}客户端已断开连接！".encode('utf-8'))


if __name__ == "__main__":
    server = Server()
    try:
        server.start()
        # 保持服务器运行
        while True:
            pass
    except KeyboardInterrupt:
        print("服务器正在关闭...")
        server.server_socket.close()

print("test3")
print("已修改")