import requests
import json
from pydantic import BaseModel
import re
import time
import hashlib

class User(BaseModel):
    login: str
    email: str
    password: str

class AuthUser(BaseModel): 
    login: str
    password: str

def validate_login(login):
    if len(login) < 5:
        print("Ошибка! Логин должен содержать не менее 5 символов")
        return False
    return True

def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        print("Ошибка! Формат email не соответствует норме! Пример: test_123@gmail.com")
        return False
    return True

def validate_password(password):
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{5,}$'
    if not re.match(password_pattern, password):
        print("Ошибка! Минимальное количество символов для пароля = 5! Необходимо использовать заглавные и строчные буквы, а также спецсимволы.")
        return False
    return True

def print_error(response):
    try:
        error_data = json.loads(response)
        error = error_data.get("detail", "Ошибка")
        print(f"Ошибка: {error}")
    except:
        print(f"Ошибка: {response}")

class Client:
    def __init__(self):
        self.session_token = None
    
    def create_signature(self, data):
        current_time = str(int(time.time()))
        body_str = json.dumps(data) if data is not None else "{}"
        signature = hashlib.sha256(f"{self.session_token}{body_str}{current_time}".encode()).hexdigest()
        return signature
    
    def send_request(self, method, url, data=None):
        headers = {'Authorization': self.create_signature(data)}
        
        if method.upper() == 'GET':
            response = requests.get(url, json=data, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, json=data, headers=headers)
        
        return response.text, response.status_code
    
    def print_sundaram_requirements(self):
        print("\n")
        print("ГЕНЕРАЦИЯ ПРОСТЫХ ЧИСЕЛ МЕТОДОМ РЕШЕТА СУНДАРАМА")
        print("Требования к параметрам:")
        print("1. Верхняя граница (n) должна быть целым положительным числом")
        print("2. Для n < 2 будет возвращен пустой список")
        print("3. Алгоритм находит все простые числа до заданного предела")
        print("")
        print("ПРИМЕРЫ:")
        print("1. n = 10 - [2, 3, 5, 7]")
        print("2. n = 30 - [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]")
        print("3. n = 100 - все простые числа до 100 (25 чисел)")

    def register(self):
        print("\nРЕГИСТРАЦИЯ В СИСТЕМЕ РЕШЕТА СУНДАРАМА")
        
        login = input("Логин: ")
        if not validate_login(login):
            return False
        
        email = input("Email: ")
        if not validate_email(email):
            return False
        
        password = input("Пароль: ")
        if not validate_password(password):
            return False
        
        confirm_password = input("Повторите пароль: ")
        if password != confirm_password:
            print("Ошибка: Пароли не совпадают!")
            return False
        
        print("Пароли совпадают")
        user_data = User(login=login, email=email, password=password)
        
        response = requests.post("http://localhost:8000/users/register", json=user_data.model_dump())
        
        if response.status_code == 200:
            user = response.json()
            self.session_token = user['session_token']
            print(f"\nПользователь {user['login']} успешно зарегистрирован!")
            return True
        else:
            error = response.json().get('detail', 'Ошибка')
            print(f"Произошла ошибка: {error}")
            return False
    
    def authenticate(self):
        print("\nАВТОРИЗАЦИЯ В СИСТЕМЕ РЕШЕТА СУНДАРАМА")
        
        login = input("Логин: ")
        password = input("Пароль: ")
        
        user_data = AuthUser(login=login, password=password)
        
        response = requests.post("http://localhost:8000/users/authenticate", json=user_data.model_dump())
        
        if response.status_code == 200:
            user = response.json()
            self.session_token = user['session_token']
            print(f"\nАвторизация {user['login']} прошла успешно!")
            return True
        else:
            error = response.json().get('detail', 'Ошибка')
            print(f"Произошла ошибка: {error}")
            return False
    
    def generate_primes(self):
        print("\nГЕНЕРАЦИЯ ПРОСТЫХ ЧИСЕЛ МЕТОДОМ РЕШЕТА СУНДАРАМА")
        self.print_sundaram_requirements()
        
        try:
            limit = int(input("Верхняя граница (n) для поиска простых чисел: "))
            
            if limit < 1:
                print("Ошибка: верхняя граница должна быть положительным числом!")
                return
            
            data = {"limit": limit}
            result, code = self.send_request('POST', "http://localhost:8000/sundaram/generate", data)
            
            if code == 200:
                response_data = json.loads(result)
                print(f"\n{response_data['message']}")
                primes = response_data['primes']
                print(f"Найдено {len(primes)} простых чисел до {limit}:")
                
                for i in range(0, len(primes), 10):
                    print(" ".join(str(x) for x in primes[i:i+10]))
            else:
                print_error(result)
        except ValueError:
            print("Ошибка: введите целое число")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def get_current_result(self):
        result, code = self.send_request('GET', "http://localhost:8000/sundaram/current")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"\n{response_data['message']}")
            
            if 'limit' in response_data:
                print(f"Верхняя граница: {response_data['limit']}")
            
            primes = response_data['primes']
            print(f"Текущий результат ({len(primes)} простых чисел):")
            print(f"{primes}")
        else:
            print_error(result)
    
    def delete_current_result(self):
        confirm = input("\nВы уверены, что хотите удалить текущий результат? (да/нет): ")
        if confirm.lower() != 'да':
            print("Отмена...")
            return
        
        result, code = self.send_request('DELETE', "http://localhost:8000/sundaram/current")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
        else:
            print_error(result)
    
    def save_parameters(self):
        print("\nСОХРАНЕНИЕ ПАРАМЕТРОВ")
        
        try:
            name = input("Название для сохранения: ")
            if not name:
                print("Ошибка: название не может быть пустым!")
                return
            
            limit = int(input("Верхняя граница (n): "))
            
            if limit < 2:
                print("Ошибка: верхняя граница должна быть не менее 2!")
                return
            
            data = {"name": name, "limit": limit}
            result, code = self.send_request('POST', "http://localhost:8000/sundaram/save_params", data)
            
            if code == 200:
                response_data = json.loads(result)
                print(f"\n{response_data['message']}")
                print(f"Имя: {response_data['name']}")
                print(f"Всего сохранено параметров: {response_data['total_saved']}")
            else:
                print_error(result)
        except ValueError:
            print("Ошибка: введите целое число!")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def show_saved_parameters(self):
        result, code = self.send_request('GET', "http://localhost:8000/sundaram/saved_params")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"\n{response_data['message']}")
            
            params = response_data['params']
            if not params:
                print("Нет сохраненных параметров")
            else:
                for i, param in enumerate(params, 1):
                    print(f"{i}. {param.get('name')}: limit={param.get('limit')} ({param.get('created_at')})")
        else:
            print_error(result)
    
    def delete_saved_parameters(self):
        self.show_saved_parameters()
        
        param_name = input("\nВведите название сохранения для удаления: ")
        if not param_name:
            print("Отмена операции!")
            return
        
        confirm = input(f"Вы точно хотите удалить параметры '{param_name}'? (да/нет): ")
        if confirm.lower() != 'да':
            print("Отмена операции!")
            return
        
        result, code = self.send_request('DELETE', f"http://localhost:8000/sundaram/saved_params/{param_name}")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
            print(f"Удалено: {response_data['deleted_name']}")
            print(f"Осталось параметров: {response_data['remaining']}")
        else:
            print_error(result)
    
    def view_history(self):
        result, code = self.send_request('GET', "http://localhost:8000/users/history")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"\n{response_data['message']}")
            
            history = response_data['history']
            if not history:
                print("История пуста")
            else:
                for i, inf in enumerate(history, 1):
                    print(f"{i}. {inf.get('time')}: {inf.get('operation')} ({inf.get('details')})")
        else:
            print_error(result)
    
    def delete_history(self):
        confirm = input("\nВы точно хотите удалить всю историю запросов? (да/нет): ")
        if confirm.lower() != 'да':
            print("Отмена операции")
            return
        
        result, code = self.send_request('DELETE', "http://localhost:8000/users/history")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
        else:
            print_error(result)
    
    def change_password(self):
        print("\nСМЕНА ПАРОЛЯ")
        
        confirm = input("Вы точно хотите изменить пароль? (да/нет): ")
        if confirm.lower() != 'да':
            print("Отмена операции")
            return
        
        old_password = input("Старый пароль: ")
        new_password = input("Новый пароль: ")
        
        if not validate_password(new_password):
            return
        
        confirm_password = input("Повторите новый пароль: ")
        if new_password != confirm_password:
            print("Ошибка: Пароли не совпадают")
            return
        
        data = {"old_password": old_password, "new_password": new_password}
        result, code = self.send_request('PATCH', "http://localhost:8000/users/password", data)
        
        if code == 200:
            response_data = json.loads(result)
            self.session_token = response_data['new_session_token']
            print(f"{response_data['message']}")
        else:
            print_error(result)
    
    def sundaram_main(self):
        while True:
            print("\nГЕНЕРАЦИЯ ПРОСТЫХ ЧИСЕЛ МЕТОДОМ РЕШЕТА СУНДАРАМА")
            print("1. Найти все простые числа до заданного предела")
            print("2. Показать текущий результат")
            print("3. Сохранить параметры поиска")
            print("4. Показать сохраненные параметры")
            print("5. Удалить сохраненные параметры")
            print("6. Удалить текущий результат")
            print("7. Назад в главное меню")
        
            try:
                choice = input("Выберите действие (1-9): ").strip()
                
                if choice == "1":
                    self.generate_primes()
                elif choice == "2":
                    self.get_current_result()
                elif choice == "3":
                    self.save_parameters()
                elif choice == "4":
                    self.show_saved_parameters()
                elif choice == "5":
                    self.delete_saved_parameters()
                elif choice == "6":
                    self.delete_current_result()
                elif choice == "7":
                    print("Возврат в главное меню.")
                    return
                else:
                    print("Неверный выбор. Введите число от 1 до 9")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
    
    def account_management(self):
        while True:
            print("\nУПРАВЛЕНИЕ УЧЕТНОЙ ЗАПИСЬЮ")
            print("1. Просмотр истории запросов")
            print("2. Удаление истории запросов")
            print("3. Смена пароля")
            print("4. Назад в главное меню")
            
            try:
                choice = input("Выберите действие (1-4): ").strip()
                
                if choice == "1":
                    self.view_history()
                elif choice == "2":
                    self.delete_history()
                elif choice == "3":
                    self.change_password()
                elif choice == "4":
                    print("Возврат в главное меню...")
                    return
                else:
                    print("Неверный выбор. Введите число от 1 до 4")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
    
    def main_menu(self):
        while True:
            print("\nГЛАВНОЕ МЕНЮ - РЕШЕТО СУНДАРАМА")
            print("1. Работа с алгоритмом Решета Сундарама")
            print("2. Управление учетной записью")
            print("3. Выход из профиля")
            
            try:
                choice = input("Выберите действие (1-3): ").strip()
                
                if choice == "1":
                    self.sundaram_main()
                elif choice == "2":
                    self.account_management()
                elif choice == "3":
                    print("Выход из профиля выполнен")
                    self.session_token = None
                    break
                else:
                    print("Неверный выбор. Введите число от 1 до 3")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

def main():
    client = Client()
    
    print("\nСИСТЕМА ГЕНЕРАЦИИ ПРОСТЫХ ЧИСЕЛ - РЕШЕТО СУНДАРАМА")
    
    while True:
        print("\nВыберите действие:")
        print("1. Регистрация нового пользователя")
        print("2. Авторизация")
        print("3. Выйти из программы")
        
        try:
            choice = input("Ваш выбор (1-3): ").strip()
            
            if choice == "1":
                if client.register():
                    client.main_menu()
            elif choice == "2":
                if client.authenticate():
                    client.main_menu()
            elif choice == "3":
                print("\nПрограмма завершена.")
                break
            else:
                print("Неверный выбор. Введите число от 1 до 3")
        except ValueError:
            print("Некорректный ввод! Введите число.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()