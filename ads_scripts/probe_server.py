"""探测 ADS CLI Server — TCP :8000 范围"""
import socket
import struct

def send_msg(sock, msg):
    """fixedLengthSocket 协议: 4字节长度头 + 消息体"""
    data = msg.encode('utf-8') if isinstance(msg, str) else msg
    sock.sendall(struct.pack('!I', len(data)) + data)

def recv_msg(sock):
    """读取 fixedLengthSocket 响应"""
    raw = sock.recv(4)
    if len(raw) < 4:
        return None
    length = struct.unpack('!I', raw)[0]
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return data.decode('utf-8', errors='ignore')

# 扫描端口 8000-8015
for port in range(8000, 8016):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', port))
        send_msg(sock, '?VERS')
        resp = recv_msg(sock)
        if resp:
            print(f"PORT {port}: {resp}")
        sock.close()
    except Exception as e:
        pass  # 端口未监听

print("Scan done.")
