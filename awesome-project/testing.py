import unittest
import requests
import json
import time
import hashlib

class TestSundaramEndpoints(unittest.TestCase):
    
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.username = f"testuser_{int(time.time())}"
        self.email = f"test_{int(time.time())}@test.com"
        self.password = "Test123!@#"
        self.token = None
    
    def auth_user(self):
        response = requests.post(f"{self.base_url}/users/authenticate", 
                                json={"login": self.username, "password": self.password})
        if response.status_code == 200:
            self.token = response.json().get("session_token")
        return response
    
    def get_signature(self, body=None):
        if not self.token: 
            return None
        current_time = str(int(time.time()))
        body_str = json.dumps(body) if body else "{}"
        return hashlib.sha256(f"{self.token}{body_str}{current_time}".encode()).hexdigest()
    
    def test_01_registration(self):
        response = requests.post(f"{self.base_url}/users/register", 
                                json={"login": self.username, "email": self.email, "password": self.password})
        
        print(f"\n1. Регистрация пользователя:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_02_registration_duplicate(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        
        response = requests.post(f"{self.base_url}/users/register", 
                                json={"login": self.username, "email": "different@test.com", "password": self.password})
        
        print(f"\n2. Регистрация уже зарегистрированного пользователя:")
        print(f"   Ожидаемый код: 400")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 400)
    
    def test_03_auth(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        
        response = self.auth_user()
        print(f"\n3. Авторизация пользователя:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_04_auth_wrong(self):
        response = requests.post(f"{self.base_url}/users/authenticate", 
                                json={"login": "wronguser", "password": "wrongpassword"})
        
        print(f"\n4. Авторизация с неверными данными:")
        print(f"   Ожидаемый код: 401")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 401)

    def test_05_generate_primes(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"limit": 100}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/sundaram/generate", json=data, headers=headers)
        
        print(f"\n5. Генерация простых чисел до 100:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Найдено чисел: {result.get('count', 0)}")
        self.assertEqual(response.status_code, 200)
    
    def test_06_generate_small_limit(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"limit": 1}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/sundaram/generate", json=data, headers=headers)
        
        print(f"\n6. Генерация простых чисел до 1:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_07_get_current_primes(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"limit": 50}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        requests.post(f"{self.base_url}/sundaram/generate", json=data, headers=headers)
        
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.get(f"{self.base_url}/sundaram/current", headers=headers)
        
        print(f"\n7. Получение текущих простых чисел:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_08_delete_current_primes(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"limit": 30}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        requests.post(f"{self.base_url}/sundaram/generate", json=data, headers=headers)
        
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.delete(f"{self.base_url}/sundaram/current", headers=headers)
        
        print(f"\n8. Удаление текущих простых чисел:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)

    def test_09_get_history(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.get(f"{self.base_url}/users/history", headers=headers)
        
        print(f"\n9. Получение истории:")
        print(f"   Ожидаемый код: 200")
        print(f"   Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_10_delete_history(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.delete(f"{self.base_url}/users/history", headers=headers)
        
        print(f"\n10. Удаление истории запросов:")
        print(f"    Ожидаемый код: 200")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_11_generate_invalid_limit(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"limit": -5}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/sundaram/generate", json=data, headers=headers)
        
        print(f"\n11. Генерация с отрицательным лимитом:")
        print(f"    Ожидаемый код: 400")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 400)
    
    def test_12_save_parameters(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"name": "TestParams", "limit": 100}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/sundaram/save_params", json=data, headers=headers)
        
        print(f"\n12. Сохранение параметров:")
        print(f"    Ожидаемый код: 200")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_13_get_saved_parameters(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"name": "GetTestParams", "limit": 50}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        requests.post(f"{self.base_url}/sundaram/save_params", json=data, headers=headers)
        
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.get(f"{self.base_url}/sundaram/saved_params", headers=headers)
        
        print(f"\n13. Получение сохраненных параметров:")
        print(f"    Ожидаемый код: 200")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_14_delete_saved_parameters(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        data = {"name": "ToDeleteParams", "limit": 75}
        signature = self.get_signature(data)
        headers = {"Authorization": signature}
        requests.post(f"{self.base_url}/sundaram/save_params", json=data, headers=headers)
        
        param_name = "ToDeleteParams"
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.delete(f"{self.base_url}/sundaram/saved_params/{param_name}", headers=headers)
        
        print(f"\n14. Удаление сохраненных параметров:")
        print(f"    Ожидаемый код: 200")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_15_change_password(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()

        new_password = "NewTest123!@#"
        change_data = {
            "old_password": self.password,
            "new_password": new_password
        }
        signature = self.get_signature(change_data)
        headers = {"Authorization": signature}
        response = requests.patch(f"{self.base_url}/users/password", json=change_data, headers=headers)
        
        print(f"\n15. Изменение пароля:")
        print(f"    Ожидаемый код: 200")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_16_get_current_empty(self):
        requests.post(f"{self.base_url}/users/register", 
                     json={"login": self.username, "email": self.email, "password": self.password})
        self.auth_user()
        
        signature = self.get_signature()
        headers = {"Authorization": signature}
        response = requests.get(f"{self.base_url}/sundaram/current", headers=headers)
        
        print(f"\n16. Получение текущих результатов (когда нет):")
        print(f"    Ожидаемый код: 404")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 404)
    
    def test_17_unauthorized_access(self):
        headers = {"Authorization": "invalid_signature"}
        response = requests.get(f"{self.base_url}/sundaram/current", headers=headers)
        
        print(f"\n17. Доступ без авторизации:")
        print(f"    Ожидаемый код: 401")
        print(f"    Итог: {response.status_code}")
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()