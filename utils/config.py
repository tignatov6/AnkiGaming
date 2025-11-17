import yaml
import os

def hi():
    print(f'hi from {__name__}')

class Config:
    def __init__(self,config_path='config.yaml'):
        self.config_path = config_path # Путь до файла конфига
        self.decks = ['ALL_DECKS'] # Если ['ALL_DECKS'] - то все возможные. Иначе список строк(названий колод) из которых нужно выбирать карточку
        self.confidence_level = 0.7 # Урочень уверенности в том, что шаблон найден, требуемый для подтверждения нахождения.
        self.template_check_rate = 0 # Задержка в секундах между попытками найти шаблон
        
        
        self.default_values = {
            'decks': ['ALL_DECKS'],
            'confidence_level': 0.7,
            'template_check_rate': 0.0
        }

        self.default_config = """

# Название колоды в Anki. По умолчанию это ALL_DECKS — все колоды.
decks:
- ALL_DECKS
# - Linear Algebra
# - History

# Определяет, насколько точным должно быть совпадение с шаблоном для обнаружения экрана смерти/возрождения
confidence_level: 0.7 # Значение в диапазоне: 0-1
# Время в секундах между проверками экрана на наличие шаблона. По умолчанию: 0.
template_check_rate: 0.0 # Любое число. (1, 0.5, 3, 0.01, 0, 10, ...)
"""
        self.load_config()
    
    def load_config(self):
        """
        Метод для обновления внутренних переменных класса. 
        После выполнения во всех переменных класса гарантировано будет присутствовать актуальная информация из файла конфигурации.
        """
        if not os.path.exists(self.config_path):
            self.create_default_config()

        with open(self.config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file) or {}
            for key, value in data.items():
                if key in self.default_values:
                    default_value = self.default_values[key]
                    
                    # Проверяем тип и пытаемся конвертировать
                    if isinstance(value, type(default_value)):
                        try:
                            setattr(self, key, value)  # ✅ Правильный способ
                        except (ValueError, TypeError):
                            setattr(self, key, default_value)
                    else:
                        # Пробуем привести тип (для простых типов)
                        try:
                            converted = type(default_value)(value)
                            setattr(self, key, converted)
                        except (ValueError, TypeError):
                            setattr(self, key, default_value)


    def create_default_config(self):
        #os.makedirs(os.path.dirname(self.config_path), exist_ok=True) 
        with open(self.config_path, 'w', encoding='utf-8') as file:

            file.write(self.default_config)


    def save_config(self):
        #os.makedirs(os.path.dirname(self.config_path), exist_ok=True) 
        with open(self.config_path, 'w', encoding='utf-8') as file:
            data = {
            'decks': self.decks,
            'confidence_level': self.confidence_level,
            'template_check_rate': self.template_check_rate
            }
            yaml.dump(data,file)
    


if __name__ == "__main__":
    try:
        config = Config()
        config.create_default_config()
        config.load_config()
        for key in config.default_values.keys():
            if getattr(config,key) != config.default_values[key]:
                print(f"Ошибка! {key}: {getattr(config,key)} и config.default_values[{key}]: {config.default_values[key]} не совпадают!")
            else:
                print(f"✅ {key}: {getattr(config,key)}")

        config.decks = ['Scream','Soup']
        config.confidence_level = 0.8
        config.template_check_rate = 0.1
        for key in config.default_values.keys():
            print(f"✅ {key}: {getattr(config,key)}")

        config.create_default_config()
        config.save_config()
        config.load_config()
        for key in config.default_values.keys():
            print(f"✅ {key}: {getattr(config,key)}")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    