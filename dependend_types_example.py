from core.dependent_types import Pi, Sigma
from enum import Enum

class CipherSuites(Enum):
    TLS_AES_256_GCM_SHA384 = 0x1302
    TLS_CHACHA20_POLY1305_SHA256 = 0x1303


class Cipher_AES_GCM:
    def __init__(self, iv: bytes, key: bytes):
        pass

    def encrypt(self, data: bytes) -> bytes:
        pass


class Cipher_ChaCha20:
    def __init__(self, iv: bytes, key: bytes):
        pass

    def encrypt(self, data: bytes) -> bytes:
        pass


class KeyExchange:
    def __init__(self, cipher: str):
        self.cipher = cipher

    def exchange_keys(self) -> bytes:
        return b'\x00'


class EncryptedStream:
    def __init__(self, cipher: str, key: bytes):
        self.cipher = cipher
        self.key =  key

    def write(self, buf:bytes):
        pass

    def read(self, buf:bytes):
        pass


class ConnectionError:
    pass

class ConnectionClosed:
    pass

class SecureConnectionState(Enum):
    NON_INITIALIZED = 0
    RUNNING = 1
    CLOSED = 2
    ERROR = 3


def create_connection(cipher):
    conn_state = Sigma(
            domain = SecureConnectionState,
            codomain = conn_state_codomain,
            first = SecureConnectionState.NON_INITIALIZED,
            second = KeyExchange(cipher)
        )
    return conn_state


def connection_error():
    conn_state = Sigma(
            domain = SecureConnectionState,
            codomain = conn_state_codomain,
            first = SecureConnectionState.ERROR,
            second = ConnectionError()
        )
    return conn_state


def conn_state_codomain(state:SecureConnectionState):
    match state:
        case SecureConnectionState.NON_INITIALIZED: return KeyExchange
        case SecureConnectionState.RUNNING: return EncryptedStream 
        case SecureConnectionState.CLOSED: return ConnectionClosed 
        case SecureConnectionState.ERROR: return ConnectionError


def exchange_keys(conn_state):
    if conn_state.first != SecureConnectionState.NON_INITIALIZED:
        return connection_error()
    
    session_key = conn_state.second.exchange_keys()

    new_state = Sigma(
            domain = SecureConnectionState,
            codomain = conn_state_codomain,
            first = SecureConnectionState.RUNNING,
            second = EncryptedStream(conn_state.second.cipher, session_key)
        )
    
    return new_state


def send_buf(conn_state, buf:bytes):
    if conn_state.first != SecureConnectionState.RUNNING:
        return connection_error()
    
    conn_state.second.write(buf)
    return conn_state


def example_dependend_types():
    # пи-тип, который позволяет создавать шифр по его
    # идентификатору, полученному, например, при 
    # парсинге конфигурации шифрования
    # или в рамках установления соединения по TLS 
    cipher_factory = Pi(
        domain = CipherSuites,
        codomain = lambda x: {
            CipherSuites.TLS_AES_256_GCM_SHA384: Cipher_AES_GCM,
            CipherSuites.TLS_CHACHA20_POLY1305_SHA256: Cipher_ChaCha20,
        },
        function = lambda cipher_suite: lambda iv, key: {
            CipherSuites.TLS_AES_256_GCM_SHA384: Cipher_AES_GCM(iv, key),
            CipherSuites.TLS_CHACHA20_POLY1305_SHA256: Cipher_ChaCha20(iv, key),
        }
    )

    aes_factory = cipher_factory(CipherSuites.TLS_AES_256_GCM_SHA384)
    chacha_factory =  cipher_factory(CipherSuites.TLS_CHACHA20_POLY1305_SHA256)

    # для упрощения здесь все ключи имеют тип bytes
    # по хорошему, для ключей должны создаваться отдельные типы
    aes = aes_factory(b'\x00'*12, b'\x00'*32)
    chacha = chacha_factory(b'\x00'*12, b'\x00'*32)
    
    # ---------------------------------------------------
    # В данном случае мы представляем состояние шифрованного соединения как сигма-тип, который
    # объединяет в себе код состояния (элемент first) и методы (оформленные в виде отдельных классов),
    # которые можно в этом состоянии вызывать.
    # Таким образом, мы за счет сигма-типа можем гарантировать правильный порядок вызова 
    # функций работы с соединениями. Так, например, функция передачи буфера (send_buf) не может быть  
    # вызвана до того, как будет произведен обмен ключами (exchange_keys) - в частности, 
    # в текущей реализации вернется экземпляр класса ConnectionError
    conn_state = create_connection(aes_factory) 
    conn_state = exchange_keys(conn_state)
    conn_state = send_buf(conn_state, b'00')



if __name__ == "__main__":
    example_dependend_types()
