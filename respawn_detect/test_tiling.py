import time
import cv2
import numpy as np
import mss
import onnxruntime as ort
import os
import ctypes

# DPI Fix
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(SCRIPT_DIR, "matcher.onnx")
TEMPLATE_PATH = "templates"
ITERATIONS = 50
OVERLAP_PX = 100  # Размер перекрытия (должен быть больше размера самого большого шаблона)

class TilingBenchmark:
    def __init__(self):
        self.load_model()
        self.load_image()
        
    def load_model(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Нет модели {MODEL_PATH}")
        
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(MODEL_PATH, sess_options=opts, providers=['CPUExecutionProvider'])
        
        self.input_name_scene = self.session.get_inputs()[0].name
        self.input_name_template = self.session.get_inputs()[1].name
        self.output_name = self.session.get_outputs()[0].name

    def load_image(self):
        # 1. Захватываем реальный экран через MSS
        with mss.mss() as sct:
            mon = sct.monitors[1]  # Берем 1-й монитор
            sct_img = sct.grab(mon)
            img = np.array(sct_img)
            self.scene_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            
        # 2. Загружаем любой шаблон для инференса
        files = [f for f in os.listdir(TEMPLATE_PATH) if f.endswith('.png')]
        if not files:
            # Создаем фейковый шаблон если нет файлов
            self.template_rgb = np.zeros((50, 50, 3), dtype=np.uint8)
        else:
            p = os.path.join(TEMPLATE_PATH, files[0])
            self.template_rgb = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
            
        # Препроцессинг шаблона (он константный)
        self.template_tensor = self.preprocess(self.pad_to_stride(self.template_rgb))
        
        print(f"Разрешение монитора для теста: {self.scene_rgb.shape}")

    def pad_to_stride(self, img, stride=32):
        h, w = img.shape[:2]
        pad_h = (stride - h % stride) % stride
        pad_w = (stride - w % stride) % stride
        if pad_h > 0 or pad_w > 0:
            return cv2.copyMakeBorder(img, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        return img

    def preprocess(self, img):
        img = img.astype(np.float32) / 255.0
        img = (img - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
        return np.expand_dims(img.transpose(2, 0, 1), axis=0)

    def get_tiles(self, img, rows, cols):
        """Режет изображение на куски с перекрытием"""
        h, w = img.shape[:2]
        tiles = []
        
        # Высота и ширина базового блока
        h_step = h // rows
        w_step = w // cols
        
        for r in range(rows):
            for c in range(cols):
                # Координаты
                y1 = r * h_step
                x1 = c * w_step
                
                # Добавляем overlap к правой и нижней границе
                y2 = min(h, (r + 1) * h_step + OVERLAP_PX)
                x2 = min(w, (c + 1) * w_step + OVERLAP_PX)
                
                tile = img[y1:y2, x1:x2]
                tiles.append(tile)
        return tiles

    def run_inference(self, scene_chunk):
        """Прогон одного куска через нейросеть"""
        # Паддинг + Препроцессинг + Run
        padded = self.pad_to_stride(scene_chunk)
        tensor = self.preprocess(padded)
        
        self.session.run([self.output_name], {
            self.input_name_scene: tensor,
            self.input_name_template: self.template_tensor
        })

    def benchmark_config(self, rows, cols, scale=1.0):
        print(f"\n--- Testing Grid: {rows}x{cols} (Scale: {scale}) ---")
        
        # 1. Подготовка сцены (Ресайз если нужен)
        if scale != 1.0:
            scene_to_process = cv2.resize(self.scene_rgb, (0,0), fx=scale, fy=scale)
        else:
            scene_to_process = self.scene_rgb
            
        start_time = time.time()
        total_tiles_processed = 0
        
        for _ in range(ITERATIONS):
            # 2. Нарезка (входит в бенчмарк)
            if rows == 1 and cols == 1:
                tiles = [scene_to_process]
            else:
                tiles = self.get_tiles(scene_to_process, rows, cols)
            
            # 3. Инференс каждого тайла (симуляция сценария "никогда не найден")
            for tile in tiles:
                self.run_inference(tile)
                total_tiles_processed += 1
                
        total_time = time.time() - start_time
        
        # Расчеты для сценария "никогда не найден" (обработка всех тайлов)
        avg_time_per_full_pass = total_time / ITERATIONS
        never_found_fps = 1.0 / avg_time_per_full_pass
        
        # Расчеты для сценария "найден в первом тайле" (теоретический максимум)
        avg_time_per_tile = total_time / total_tiles_processed
        best_case_fps = 1.0 / (avg_time_per_tile + (total_time - total_tiles_processed * avg_time_per_tile) / ITERATIONS)
        
        print(f"  Tiles count: {rows*cols}")
        print(f"  Never Found FPS: {never_found_fps:.2f} (обработка всех тайлов)")
        print(f"  Best Case FPS: {best_case_fps:.2f} (найден в первом тайле)")
        
        return never_found_fps, best_case_fps

if __name__ == "__main__":
    bm = TilingBenchmark()
    
    results = []
    
    # Конфигурации для теста
    configs = [
        (1, 1, 1.0),  # Оригинал
        (1, 1, 0.5),  # Просто уменьшить в 2 раза (без нарезки)
        (2, 1, 1.0),  # Делим пополам вертикально (верх/низ)
        (2, 2, 1.0),  # 4 куска
        (3, 2, 1.0),  # 6 кусков
        (3, 3, 1.0),  # 9 кусков
        (4, 3, 1.0),  # 12 кусков
    ]
    
    print(f"\nЗапуск теста на {ITERATIONS} итераций...")
    print(f"Overlap: {OVERLAP_PX}px")
    print("Сценарий 'Never Found': нейросеть обрабатывает ВСЕ тайлы (шаблон не найден)")
    print("Сценарий 'Best Case': нейросеть находит шаблон в ПЕРВОМ тайле")
    
    for r, c, s in configs:
        nf_fps, bc_fps = bm.benchmark_config(r, c, s)
        results.append({
            "name": f"{r}x{c} (x{s})",
            "never_found": nf_fps,
            "best_case": bc_fps
        })
        
    print("\n" + "="*80)
    print(f"{'Конфигурация':<15} | {'Never Found FPS':<15} | {'Best Case FPS':<15}")
    print("-" * 80)
    for res in results:
        print(f"{res['name']:<15} | {res['never_found']:<15.2f} | {res['best_case']:<15.2f}")
    print("="*80)
    
    print("\nАНАЛИТИКА ПРОИЗВОДИТЕЛЬНОСТИ:")
    print("-" * 50)
    
    # Находим конфигурацию с лучшей производительностью в сценарии "никогда не найден"
    stable_config = max(results, key=lambda x: x['never_found'])
    print(f"✅ Самый стабильный (при отсутствии шаблона): {stable_config['name']} | {stable_config['never_found']:.2f} FPS")
    
    # Находим конфигурацию с лучшей производительностью в сценарии "найден в первом тайле"
    fast_config = max(results, key=lambda x: x['best_case'])
    print(f"⚡ Самый быстрый поиск (при удачном расположении): {fast_config['name']} | {fast_config['best_case']:.2f} FPS")
    
    # Рекомендация по балансу
    print("\n💡 РЕКОМЕНДАЦИЯ ПО НАСТРОЙКАМ:")
    print("-" * 50)
    
    # Рассчитываем баланс между стабильностью и скоростью
    for res in results:
        res['balance_score'] = (res['never_found'] * 0.6) + (res['best_case'] * 0.4)
    
    balanced_config = max(results, key=lambda x: x['balance_score'])
    print(f"⚖️ Лучший баланс стабильности и скорости: {balanced_config['name']}")
    print(f"   Never Found FPS: {balanced_config['never_found']:.2f}")
    print(f"   Best Case FPS: {balanced_config['best_case']:.2f}")
    
    # Дополнительная аналитика
    print("\n🔍 КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ:")
    print("-" * 50)
    if results[0]['never_found'] > results[-1]['never_found']:
        print("• Уменьшение разрешения часто эффективнее нарезки на тайлы")
    else:
        print("• Нарезка на тайлы даёт лучшую производительность при высоких разрешениях")
    
    if results[0]['best_case'] < results[-1]['best_case']:
        print("• Теоретическая максимальная скорость растёт с количеством тайлов")
    else:
        print("• Уменьшение разрешения даёт лучшую теоретическую скорость")