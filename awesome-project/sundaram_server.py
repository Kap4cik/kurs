from typing import Union, List
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import time
import os
import random
import hashlib

app = FastAPI(title="Sundaram Resheto API", description="API для генерации простых чисел методом Решета Сундарама")

class User(BaseModel):
    login: str
    email: str
    password: str
    technical_token: Union[str, None] = None
    session_token: Union[str, None] = None
    id: Union[int, None] = -1
    current_primes: List[int] = []
    sundaram_params: dict = {}
    saved_params: List[dict] = []

class AuthUser(BaseModel):
    login: str
    password: str

class SundaramGenerateRequest(BaseModel):
    limit: int

class SaveParamsRequest(BaseModel):
    name: str
    limit: int

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

def resheto_sundarama(limit: int) -> List[int]:

    if limit < 2:
        return []

    n = (limit - 1) // 2
    
    reshet = [True] * (n + 1)
    
    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            k = i + j + 2 * i * j
            if k <= n:
                reshet[k] = False
            j += 1
    
    primes = [2]
        
    for i in range(1, n + 1):
        if reshet[i]:
            prime = 2 * i + 1
            if prime <= limit:
                primes.append(prime)
    
    return primes

def get_user_by_token(request: Request, body: dict = None) -> User:
    client_signature = request.headers.get('Authorization')
    if not client_signature:
        raise HTTPException(status_code=401, detail="Отсутствует подпись")
    
    current_time = int(time.time())
    body_str = json.dumps(body) if body is not None else "{}"
    
    for time_add in [-3, -2, -1, 0]:
        check_time = str(current_time + time_add)
        
        for file in os.listdir("users"):
            with open(f"users/{file}", 'r') as f:
                user_data = json.load(f)
                user_token = user_data.get('session_token')
                server_signature = hashlib.sha256(f"{user_token}{body_str}{check_time}".encode()).hexdigest()
                if server_signature == client_signature:
                    return User(**user_data)
    raise HTTPException(status_code=401, detail="Неверная подпись")

def save_user(user: User):
    with open(f"users/user_{user.id}.json", 'w') as f:
        json.dump(user.model_dump(), f)

def save_history(user_id: int, operation_type: str, details: str):
    history_file = f"history/history_{user_id}.json"
    if not os.path.exists(history_file):
        return
    
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    history_add = {
        "user": user_id,
        "time": current_time,
        "operation": operation_type,
        "details": details
    }
    history.append(history_add)
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

@app.post("/users/register")
def create_user(user: User):
    if not os.path.exists("users"):
        os.makedirs("users")
    
    for file in os.listdir("users"):
        with open(f"users/{file}", 'r') as f:
            data = json.load(f)
            if data['login'] == user.login:
                raise HTTPException(status_code=400, detail="Логин уже занят")
            if data['email'] == user.email:
                raise HTTPException(status_code=400, detail="Email уже занят")
    
    user.id = int(time.time())
    user.technical_token = str(random.getrandbits(128))
    user.session_token = hashlib.sha256(f"{user.technical_token}{time.time()}".encode()).hexdigest()
    
    save_user(user)
    
    if not os.path.exists("history"):
        os.makedirs("history")
    
    with open(f"history/history_{user.id}.json", 'w') as f:
        json.dump([], f)
    
    save_history(user.id, "register", "Пользователь зарегистрирован")
    return {
        "message": "Успешная регистрация",
        "login": user.login,
        "session_token": user.session_token
    }

@app.post("/users/authenticate")
def auth_user(params: AuthUser):
    json_files_names = [file for file in os.listdir('users/') if file.endswith('.json')]
    for json_file_name in json_files_names:
        file_path = os.path.join('users/', json_file_name)
        with open(file_path, 'r') as f:
            json_item = json.load(f)
            user = User(**json_item)
            if user.login == params.login and user.password == params.password:
                user.session_token = hashlib.sha256(f"{user.technical_token}{time.time()}".encode()).hexdigest()
                save_user(user)
                save_history(user.id, "auth", "Успешная авторизация")
                return {
                    "message": "Успешная авторизация",
                    "login": user.login,
                    "session_token": user.session_token
                }
    
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@app.post("/sundaram/generate")
def generate_sundaram_primes(request: SundaramGenerateRequest, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    if request.limit < 1:
        raise HTTPException(status_code=400, detail="Верхняя граница должна быть положительным числом")
    
    primes = resheto_sundarama(request.limit)
    
    user.current_primes = primes
    user.sundaram_params = {
        "limit": request.limit,
        "count": len(primes)
    }
    save_user(user)

    save_history(user.id, "sundaram_generate", 
                 f"Сгенерировано {len(primes)} простых чисел до {request.limit}")
    
    return {
        "message": f"Найдено {len(primes)} простых чисел до {request.limit}",
        "primes": primes,
        "limit": request.limit,
        "count": len(primes)
    }

@app.get("/sundaram/current")
def get_current_primes(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    if not user.current_primes:
        raise HTTPException(status_code=404, detail="Результат не найден")
    
    save_history(user.id, "sundaram_get", f"Получен список из {len(user.current_primes)} простых чисел")
    return {
        "message": f"Текущий результат ({len(user.current_primes)} простых чисел)",
        "primes": user.current_primes,
        "params": user.sundaram_params
    }

@app.delete("/sundaram/current")
def delete_current_primes(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    user.current_primes = []
    user.sundaram_params = {}
    save_user(user)
    
    save_history(user.id, "sundaram_delete", "Результат удален")
    return {"message": "Результат удален", "primes": []}

@app.post("/sundaram/save_params")
def save_parameters(request: SaveParamsRequest, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    if not hasattr(user, 'saved_params'):
        user.saved_params = []
    
    for param in user.saved_params:
        if param.get('name') == request.name:
            raise HTTPException(status_code=400, detail="Параметры с таким именем уже существуют")
    
    user.saved_params.append({
        "name": request.name,
        "limit": request.limit,
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
    save_user(user)
    save_history(user.id, "save_params", f"Сохранены параметры '{request.name}' (limit={request.limit})")
    
    return {
        "message": "Параметры сохранены",
        "name": request.name,
        "total_saved": len(user.saved_params)
    }

@app.get("/sundaram/saved_params")
def get_saved_parameters(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    if not hasattr(user, 'saved_params') or not user.saved_params:
        return {"message": "Нет сохраненных параметров", "params": []}
    
    return {
        "message": f"Сохраненные параметры ({len(user.saved_params)})",
        "params": user.saved_params
    }

@app.delete("/sundaram/saved_params/{param_name}")
def delete_saved_parameters(param_name: str, request_obj: Request):
    user = get_user_by_token(request_obj)
    
    if not hasattr(user, 'saved_params'):
        raise HTTPException(status_code=404, detail="Нет сохраненных параметров")
    
    original_count = len(user.saved_params)
    user.saved_params = [p for p in user.saved_params if p.get('name') != param_name]
    
    if len(user.saved_params) == original_count:
        raise HTTPException(status_code=404, detail="Параметры с таким именем не найдены")
    
    save_user(user)
    save_history(user.id, "delete_params", f"Удалены параметры '{param_name}'")
    
    return {
        "message": "Параметры удалены",
        "deleted_name": param_name,
        "remaining": len(user.saved_params)
    }

@app.get("/users/history")
def get_user_history(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    history_file = f"history/history_{user.id}.json"
    
    with open(history_file, 'r') as f:
        history = json.load(f)
        
    if history == []:
        return {"message": "История пуста", "history": history}
    
    return {
        "message": "История запросов",
        "history": history
    }

@app.delete("/users/history")
def delete_user_history(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    history_file = f"history/history_{user.id}.json"
    if os.path.exists(history_file):
        with open(history_file, 'w') as f:
            json.dump([], f)
            
    return {"message": "История удалена"}

@app.patch("/users/password")
def change_password(request: PasswordChange, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    user_file = f"users/user_{user.id}.json"
    if not os.path.exists(user_file):
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    with open(user_file, 'r') as f:
        user_data = json.load(f)
    if user_data['password'] != request.old_password:
        raise HTTPException(status_code=400, detail="Неверный старый пароль")
    
    user_data['password'] = request.new_password
    user_data['technical_token'] = hashlib.sha256(f"{time.time()}{random.getrandbits(256)}".encode()).hexdigest()
    user_data['session_token'] = hashlib.sha256(f"{user_data['technical_token']}{time.time()}".encode()).hexdigest()
    
    with open(user_file, 'w') as f:
        json.dump(user_data, f)
    save_history(user.id, "change_password", "Пароль изменен")
    
    return {
        "message": "Пароль изменен",
        "new_session_token": user_data['session_token']
    }

if __name__ == "__main__":
    import uvicorn
    print("Сервер Sundaram Sieve запущен на http://localhost:8000")
    print("Документация API: http://localhost:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)