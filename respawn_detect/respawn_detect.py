# для импорта модулей из корня проекта
import sys
import os
import glob
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.anki_connect import hi as hi_anki
import utils.config as config
import utils.profiler
from screeninfo import get_monitors
import mss
import cv2
import pyautogui
import numpy as np
import time
import pyscreeze
from PIL import Image
import numpy as np

prof = utils.profiler.get_profiler("template_matcher")

pyautogui.useImageNotFoundException(False)

def hi():
    print(f'hi from {__name__}')

class TemplateMatcher:
    def __init__(self, config, use_gray=False):
        self.config = config
        self.templates_path = 'templates'
        self.template_extensions = ['.png','.jpg']
        self.use_gray = use_gray
        self.monitors = []
        self.update_monitors()

    @prof
    def check(self, return_template_path = False):
        """
        Проверяет наличие любого шаблона из директории templates на текущем скриншоте экрана.
        
        Параметры:
        return_template_path : bool, optional (default=False)
            Если True - возвращает кортеж (найдено, путь_к_шаблону)
            Если False - возвращает только булево значение (найдено/не найдено)
        
        Возвращает:
        bool или (bool, str/None)
            - При return_template_path=False: 
                True если найдено совпадение, иначе False
            - При return_template_path=True:
                (True, путь_к_шаблону) если найдено совпадение
                (False, None) если совпадений нет
        
        Алгоритм работы:
        1. Делает скриншот экрана
        2. Итерируется по всем файлам в директории шаблонов
        3. Для каждого подходящего файла (png/jpg) пытается найти совпадение на скриншоте
        4. При первом найденном совпадении прерывает поиск
        
        
        Особенности:
        - Использует confidence_level из конфигурации
        - Прекращает поиск при первом совпадении
        - Поддерживает многомониторные конфигурации (allScreens=True)
        """

        screen_img = self.get_screen_img()
        
        for filename in os.listdir(self.templates_path):
            template_path = os.path.join(self.templates_path, filename)
                
            if os.path.isfile(template_path):
                _, extension = os.path.splitext(filename)
                if extension.lower() in self.template_extensions:
                    if self.find_pattern(screen_img, template_path, self.config.confidence_level):
                        if return_template_path:
                            return True, template_path
                        return True
        if return_template_path:
            return False, None
        return False

    @prof
    def get_screen_img(self, allScreens=True, monitor_id=0, region=(0.25,0.25,0.5,0.5)):
        """
        Захват изображения экрана с поддержкой мультимониторных конфигураций.
        
        Использует pyautogui.screenshot() для корректной обработки DPI scaling.
        
        Args:
            allScreens (bool): Если True, захватывает все мониторы в одно изображение.
                            По умолчанию True.
            monitor_id (int, optional): Индекс монитора из self.monitors для захвата.
                                        Игнорируется если allScreens=True.
            region (tuple, optional): Относительная область захвата (x, y, width, height),
                                    где все значения в диапазоне 0.0-1.0.
                                    Применяется к указанному монитору.
                                    Пример: (0.25, 0.25, 0.5, 0.5) - центральная четверть.
        
        Returns:
            PIL.Image: Захваченное изображение экрана в формате RGB.
        
        Raises:
            IndexError: Если monitor_id выходит за пределы списка мониторов.
        
        Examples:
            >>> screen = obj.get_screen_img()  # Все мониторы
            >>> screen = obj.get_screen_img(allScreens=False, monitor_id=0)  # Первый монитор
            >>> screen = obj.get_screen_img(allScreens=False, monitor_id=1, 
            ...                             region=(0, 0, 0.5, 0.5))  # Верхняя левая четверть второго монитора
        
        Note:
            Перед использованием monitor_id рекомендуется вызвать update_monitors()
            для актуализации списка мониторов.
        """
        if allScreens:
            pil_img = pyautogui.screenshot(allScreens=True)
            
        elif monitor_id is not None and monitor_id < len(self.monitors):  # ✅ Исправлено
            monitor = self.monitors[monitor_id]
            
            if region is not None:
                # region - относительные координаты (x, y, w, h) в диапазоне 0.0-1.0
                abs_x = int(monitor.x + region[0] * monitor.width)
                abs_y = int(monitor.y + region[1] * monitor.height)
                abs_width = int(region[2] * monitor.width)
                abs_height = int(region[3] * monitor.height)
                pil_img = pyautogui.screenshot(region=(abs_x, abs_y, abs_width, abs_height))
            else:
                # Весь монитор
                pil_img = pyautogui.screenshot(region=(monitor.x, monitor.y, 
                                                        monitor.width, monitor.height))
        else:
            # Fallback
            pil_img = pyautogui.screenshot()
        #pil_img.show()
        return pil_img

    @prof
    def update_monitors(self):
        self.monitors = get_monitors()
        for m in self.monitors:
            print(f"Монитор: {m.name}")
            print(f"  Разрешение: {m.width}x{m.height}")
            print(f"  Координаты: x={m.x}, y={m.y}")
            print(f"  Основной: {m.is_primary}\n")

    @prof
    def prepare_image(self, source, keep_alpha=False):
        pass

    @prof
    def find_pattern(self,haystack_source, needle_source, threshold=0.95):
        """
        haystack_source: Где ищем (путь или скриншот pyautogui)
        needle_source: Что ищем (путь или картинка, желательно с прозрачностью)
        """
        location = pyautogui.locate(needle_source, haystack_source, confidence=threshold)
        if location:
            print(f"Найдено совпадение с шаблоном: {needle_source}")
            return True
        return False
        

if __name__ == "__main__":
    # Убираем паузы PyAutoGUI для скорости
    pyautogui.PAUSE = 0
    
    my_config = config.Config()
    
    # use_gray=False -> ЦВЕТНОЙ ПОИСК
    template_matcher = TemplateMatcher(my_config, use_gray=False)

    print("Делаем тестовый скриншот...")
    screen_img = template_matcher.get_screen_img()
    print(f"Скриншот получен. Размер: {screen_img.size}")

    hi()
    hi_anki()
    config.hi()

    print("Starting loop...")

    counter = 0
    start_time = time.time()

    while True:
        counter += 1
        
        if template_matcher.check():
            print('!!! Found !!!')
            # Можно добавить небольшую паузу, если нашло, чтобы не спамить
            # time.sleep(1)
        
        REPORT_INTERVAL = 10
        if counter % REPORT_INTERVAL == 0:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > 0:
                fps = REPORT_INTERVAL / elapsed_time
                print(f"\nFPS: {fps:.2f}")
            
            utils.profiler.report() 
            utils.profiler.clear_stats() 
            start_time = time.time()