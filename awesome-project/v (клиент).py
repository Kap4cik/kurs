class AuthUser(BaseModel):
 login: str
 password: str

#1 подпись сессионный токен
#2 подпись кэш сессионый токен и время
def get_signature():
    return {"Authorization": session_token}
    current_time = str(int(time.time()))
    signature = hashlib.sha256(f"{session_token}{current_time}".encode()).hexdigest()
    return {
        "Authorization": signature,
        "Time": current_time
    }

def print_error(response):
    error = response.json().get("detail", "Ошибка")