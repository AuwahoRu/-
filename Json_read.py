
import json
from typing import Optional, Any, Dict, List, Union
from pathlib import Path


class JSONFileHandler:
    """Базовый класс для работы с JSON файлами"""
    
    def __init__(self, filename: str):
        self.filepath = Path(filename)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def read(self) -> Optional[Any]:
        """Чтение данных из JSON файла"""
        try:
            if self.filepath.exists():
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка чтения файла {self.filepath}: {e}")
            return None
    
    def write(self, data: Any) -> bool:
        """Запись данных в JSON файл"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except (TypeError, IOError) as e:
            print(f"Ошибка записи в файл {self.filepath}: {e}")
            return False


class UserSettings(JSONFileHandler):
    """Класс для управления пользовательскими настройками"""
    
    DEFAULT_USER_DATA = [
        {
            "type": "love",
            "message": 10,
            "time": 8,
            "con": True
        }
    ]
    
    def __init__(self, filename: str):
        super().__init__(filename)
        self._cache = None
        self._users_cache = None
    
    def _ensure_structure(self) -> Dict:
        """Гарантирует наличие правильной структуры данных"""
        if self._cache is None:
            data = self.read() or {"User": []}
            self._cache = data
        return self._cache
    
    def _save_and_clear_cache(self) -> bool:
        """Сохраняет данные и очищает кэш"""
        result = self.write(self._cache)
        if result:
            self._cache = None
            self._users_cache = None
        return result
    
    def _get_users_dict(self) -> Dict[str, List]:
        """Преобразует данные в удобный словарь пользователей"""
        data = self._ensure_structure()
        return {
            username: user_data
            for user in data.get('User', [])
            for username, user_data in user.items()
        }
    
    def get_user_data(self, username: str) -> Optional[List]:
        """Получить данные конкретного пользователя"""
        users_dict = self._get_users_dict()
        return users_dict.get(username)
    
    def get_user_message(self, username: str, index: int = 0, field: str = 'message') -> Optional[Any]:
        """Получить конкретное поле пользователя"""
        user_data = self.get_user_data(username)
        if user_data and 0 <= index < len(user_data):
            return user_data[index].get(field)
        return None
    
    def get_all_users(self) -> List[str]:
        """Получить список всех пользователей"""
        if self._users_cache is None:
            self._users_cache = list(self._get_users_dict().keys())
        return self._users_cache.copy()
    
    def user_exists(self, username: str) -> bool:
        """Проверить существует ли пользователь"""
        return username in self.get_all_users()
    
    def add_user(self, username: str, user_data: Optional[List] = None) -> bool:
        """Добавить нового пользователя"""
        if self.user_exists(username):
            print(f"⚠️ Пользователь {username} уже существует!")
            return False
        
        data = self._ensure_structure()
        data.setdefault('User', []).append({
            username: user_data or self.DEFAULT_USER_DATA.copy()
        })
        
        return self._save_and_clear_cache()
    
    def update_user(self, username: str, new_data: Union[Dict, List], index: int = 0) -> bool:
        """Обновить данные существующего пользователя"""
        if not self.user_exists(username):
            print(f"⚠️ Пользователь {username} не найден!")
            return False
        
        data = self._ensure_structure()
        
        for user in data['User']:
            if username in user:
                if isinstance(new_data, dict):
                    user[username][index].update(new_data)
                else:
                    user[username] = new_data
                break
        
        return self._save_and_clear_cache()
    
    def delete_user(self, username: str) -> bool:
        """Удалить пользователя"""
        if not self.user_exists(username):
            print(f"⚠️ Пользователь {username} не найден!")
            return False
        
        data = self._ensure_structure()
        data['User'] = [u for u in data['User'] if username not in u]
        
        return self._save_and_clear_cache()
    
    def add_message_to_user(self, username: str, message_data: Dict) -> bool:
        """Добавить новое сообщение пользователю"""
        if not self.user_exists(username):
            print(f"⚠️ Пользователь {username} не найден!")
            return False
        
        data = self._ensure_structure()
        
        for user in data['User']:
            if username in user:
                user[username].append(message_data)
                break
        
        return self._save_and_clear_cache()
    
    def print_user_info(self, username: str) -> None:
        """Вывести информацию о пользователе"""
        user_data = self.get_user_data(username)
        if not user_data:
            print(f"❌ Пользователь {username} не найден")
            return
        
        print(f"\n📊 Информация о пользователе: {username}")
        print("━" * 40)
        
        for i, msg in enumerate(user_data, 1):
            print(f"📝 Сообщение #{i}:")
            print(f"  📌 Тип: {msg.get('type', 'N/A')}")
            print(f"  💬 Сообщение: {msg.get('message', 'N/A')}")
            print(f"  ⏰ Время: {msg.get('time', 'N/A')}")
            print(f"  🔘 Состояние: {msg.get('con', 'N/A')}")
            if i < len(user_data):
                print("  " + "─" * 35)





