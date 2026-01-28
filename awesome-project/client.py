import requests
import json
from pydantic import BaseModel
from typing import Union

class Item(BaseModel):
    name: str
    description: Union[str, None] = "Описание...."
    price: float
    id: Union[int, None] = -1

    def __str__(self):
        return f"{self.name} {self.description} за {self.price} рублей"

def all_items(token):
    headers = {'Authorization': token}
    response = requests.get("http://localhost:8000/items", headers=headers)
    if response.status_code == 200:
        json_items = json.loads(response.text)
        for json_item in json_items:
            item = Item(**json_item)
            if item.description is not None:
                print(item)
    else:
        print(f"Ошибка получения товаров: {response.text}")

def register_user():
    print("\nРегистрация:")
    name = input("Введите логин: ")
    password = input("Введите пароль: ")
    
    user_data = {"name": name, "password": password}
    response = requests.post("http://localhost:8000/users/", json=user_data)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        print("Регистрация успешна!")
        print(f"Логин: {response_data['name']}")
        print(f"Токен: {response_data['token']}")
        return response_data['token']
    else:
        print(f"Ошибка регистрации: {response.text}")
        return None
    return None

def auth_user():
    print("\n=== АВТОРИЗАЦИЯ ===")
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    
    auth_data = {"login": login, "password": password}
    response = requests.post("http://localhost:8000/users/auth", json=auth_data)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        print("Авторизация успешна!")
        print(f"Логин: {response_data['name']}")
        print(f"Токен: {response_data['token']}")
        return response_data['token']
    else:
        print(f"Ошибка авторизации: {response.text}")
        return None
    return None

def main_menu():
    token = None
    
    while True:
        print("Меню:")
        print("1. Регистрация")
        print("2. Авторизация")
        print("3. Просмотр товаров")
        print("4. Выход")
        
        choice = input("Выберите пункт меню: ")
        
        if choice == "1":
            token = register_user()
        elif choice == "2":
            token = auth_user()
        elif choice == "3":
            if token:
                print("\nСписок товаров:")
                all_items(token)
            else:
                print("Сначала авторизуйтесь!")
        elif choice == "4":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main_menu()