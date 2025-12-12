import bcrypt
import hashlib

def hash_password(password: str) -> str:
    # Конвертируем пароль в байты
    password_bytes = password.encode('utf-8')
    
    # Если пароль слишком длинный, используем SHA256
    if len(password_bytes) > 72:
        password_bytes = hashlib.sha256(password_bytes).digest()
    
    # Генерируем соль и хешируем
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Для проверки делаем то же преобразование
    password_bytes = plain_password.encode('utf-8')
    
    if len(password_bytes) > 72:
        password_bytes = hashlib.sha256(password_bytes).digest()
    
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)