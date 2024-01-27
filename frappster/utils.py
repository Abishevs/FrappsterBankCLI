import bcrypt
from datetime import datetime, timedelta

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                    salt)
    return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'),
                          hashed_password.encode('utf-8'))

def is_too_many_login_attempts(login_attempts: int, max_attempts: int = 3):
    return login_attempts > max_attempts

def reset_login_attempts(last_attempt: datetime, max_time_seconds: int = 30):
    time_diff = datetime.now() - last_attempt
    return time_diff > timedelta(minutes=max_time_seconds)
