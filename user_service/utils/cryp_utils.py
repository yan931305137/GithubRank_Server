from cryptography.fernet import Fernet

# 固定密钥
key = b'jdduZWwbXIgno2-VDdm1-ZjIZd1IpfwTELmrBI29rgk='  # 请将此处替换为您的固定密钥

def encrypt_password(password):
    """
    加密密码
    :param password: 明文密码
    :return: 加密后的密码
    """
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password):
    """
    解密密码
    :param encrypted_password: 加密后的密码
    :return: 解密后的明文密码
    """
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password
