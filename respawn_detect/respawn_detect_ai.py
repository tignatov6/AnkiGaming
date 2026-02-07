import sys
import os
import time
import cv2
import numpy as np
import mss
import onnxruntime as ort
import ctypes

# === DPI FIX ===
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.anki_connect import hi as hi_anki
import utils.config as config
import utils.profiler

prof = utils.profiler.get_profiler("template_matcher")

MODEL_FILENAME = "matcher.onnx"

MONITORS = [2]

SCALE_FACTOR=1

def hi():
    print(f'hi from {__name__}')

class TemplateMatcher:
    def __init__(self, config):
        self.config = config
        self.templates_path = 'templates'
        self.template_extensions = ['.png', '.jpg']
        
        self.sct = mss.mss()
        # monitors[0] - это весь виртульный экран
        # monitors[1:] - это физические мониторы
        self.virtual_screen = self.sct.monitors[0]
        self.physical_monitors = self.sct.monitors[1:]
        
        self.last_found_monitor_idx = 0 
        print(f"🖥️ Virtual Screen: {self.virtual_screen}")
        print(f"🖥️ Physical monitors: {len(self.physical_monitors)}")

        # === ONNX SETUP ===
        model_path = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)
        self.session = None
        self.template_cache = {} 
        
        if os.path.exists(model_path):
            try:
                sess_options = ort.SessionOptions()
                sess_options.intra_op_num_threads = 2
                sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                
                self.session = ort.InferenceSession(
                    model_path, sess_options=sess_options, providers=['CPUExecutionProvider']
                )
                
                self.input_name_scene = self.session.get_inputs()[0].name
                self.input_name_template = self.session.get_inputs()[1].name
                self.output_name = self.session.get_outputs()[0].name
                print(f"✅ NN Model loaded")
            except Exception as e:
                print(f"❌ Failed to load NN model: {e}")
        else:
            print(f"❌ Model file not found")

    @prof
    def check(self, visualize=False):
        if self.session is None: return False

        # 1. ЗАХВАТ ВСЕГО И СРАЗУ (Самый быстрый способ)
        monitor_images = self.capture_all_and_split(SCALE_FACTOR)
        
        # 2. Определяем порядок проверки (начинаем с последнего успешного)
        indices = list(range(len(monitor_images)))
        if self.last_found_monitor_idx in indices:
            indices.remove(self.last_found_monitor_idx)
            indices.insert(0, self.last_found_monitor_idx)

        templates = self._get_all_templates()

        # 3. Инференс
        for mon_idx in indices:
            screen_img = monitor_images[mon_idx]
            
            # Если после обрезки полос ничего не осталось
            if screen_img.size == 0: continue

            for tmpl_name, tmpl_img in templates:
                is_match = self.find_pattern(
                    screen_img, tmpl_img, tmpl_name, 
                    threshold=self.config.confidence_level, 
                    visualize=visualize, mon_idx=mon_idx
                )
                
                if is_match:
                    self.last_found_monitor_idx = mon_idx
                    return True
                    
        return False

    @prof
    def capture_all_and_split(self, scale_factor=1):
        """
        Делает 1 скриншот всей системы, ресайзит его и режет на мониторы.
        scale_factor: 1.0 = 100%, 0.5 = 50% и т.д.
        """
        # 1. Захват всего пространства (Monitor 0)
        full_sct = self.sct.grab(self.virtual_screen)
        full_img = np.array(full_sct)
        full_rgb = cv2.cvtColor(full_img, cv2.COLOR_BGRA2RGB)

        # 2. РЕЗАЙЗ ВСЕГО ХОЛСТА (если масштаб не 1.0)
        if scale_factor != 1.0:
            h_full, w_full = full_rgb.shape[:2]
            new_w = int(w_full * scale_factor)
            new_h = int(h_full * scale_factor)
            # INTER_LINEAR — оптимальный баланс скорости и качества для уменьшения
            full_rgb = cv2.resize(full_rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        monitor_images = []
        
        # Координаты начала общего холста
        base_x = self.virtual_screen['left']
        base_y = self.virtual_screen['top']

        # 3. Нарезка по масштабированным координатам
        for i, mon in enumerate(self.physical_monitors):
            if i+1 in MONITORS or len(MONITORS) == 0:
                # Вычисляем локальные координаты и применяем масштаб
                rel_x = int((mon['left'] - base_x) * scale_factor)
                rel_y = int((mon['top'] - base_y) * scale_factor)
                w = int(mon['width'] * scale_factor)
                h = int(mon['height'] * scale_factor)

                # Numpy Slice по масштабированной сетке
                mon_img = full_rgb[rel_y:rel_y+h, rel_x:rel_x+w]
                
                # 4. Обрезка черных полос
                clean_img = self.crop_black_borders(mon_img)
                monitor_images.append(clean_img)

        return monitor_images

    def crop_black_borders(self, img):
        if img.size == 0: return img
        # Быстрый чек углов
        if np.any(img[0,0] > 0) and np.any(img[-1,-1] > 0): return img
        
        rows = np.any(img, axis=(1, 2))
        cols = np.any(img, axis=(0, 2))
        
        if not np.any(rows) or not np.any(cols): return img
        
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        return img[ymin:ymax+1, xmin:xmax+1]

    @prof
    def _get_all_templates(self):
        valid = []
        for f in os.listdir(self.templates_path):
            if os.path.splitext(f)[1].lower() in self.template_extensions:
                img = self._get_template_data(os.path.join(self.templates_path, f))
                if img is not None: valid.append((f, img))
        return valid

    def _get_template_data(self, path):
        if path in self.template_cache: return self.template_cache[path]
        img = cv2.imread(path)
        if img is None: return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.template_cache[path] = img
        return img

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

    @prof
    def find_pattern(self, scene_rgb, template_rgb, template_name, threshold=0.9, visualize=False, mon_idx=0):
        scene_padded = self.pad_to_stride(scene_rgb)
        template_padded = self.pad_to_stride(template_rgb)
        
        if template_padded.shape[0] > scene_padded.shape[0] or template_padded.shape[1] > scene_padded.shape[1]:
             return False

        scene_tensor = self.preprocess(scene_padded)
        template_tensor = self.preprocess(template_padded)

        try:
            res = self.session.run([self.output_name], {
                self.input_name_scene: scene_tensor,
                self.input_name_template: template_tensor
            })
            score = float(res[0])
            is_match = score > threshold

            if visualize:
                self._show_debug(scene_padded, template_padded, score, is_match, f"M{mon_idx+1}:{template_name}")
            return is_match
        except Exception as e:
            print(f"Err: {e}")
            return False

    def _show_debug(self, scene, tmpl, score, match, name):
        dbg = cv2.cvtColor(scene, cv2.COLOR_RGB2BGR)
        color = (0, 255, 0) if match else (0, 0, 255)
        text = f"{name} | {score:.2f} | {'YES' if match else 'NO'}"
        
        cv2.rectangle(dbg, (0,0), (450, 40), (0,0,0), -1)
        cv2.putText(dbg, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        h_t, w_t = tmpl.shape[:2]
        thumb = cv2.cvtColor(tmpl, cv2.COLOR_RGB2BGR)
        if h_t > 100:
            scale = 100 / h_t
            thumb = cv2.resize(thumb, (0,0), fx=scale, fy=scale)
        
        h_th, w_th = thumb.shape[:2]
        if 50+h_th < dbg.shape[0] and 10+w_th < dbg.shape[1]:
            dbg[50:50+h_th, 10:10+w_th] = thumb

        if dbg.shape[0] > 800:
            scale_view = 800 / dbg.shape[0]
            dbg = cv2.resize(dbg, (0,0), fx=scale_view, fy=scale_view)
            
        cv2.imshow("Neural Network View", dbg)
        cv2.waitKey(1)

if __name__ == "__main__":
    import pyautogui
    pyautogui.PAUSE = 0
    
    my_config = config.Config()
    if not hasattr(my_config, 'confidence_level'): my_config.confidence_level = 0.85
    
    tm = TemplateMatcher(my_config)

    # Проверка нарезки
    print("--- Testing Split ---")
    imgs = tm.capture_all_and_split(SCALE_FACTOR)
    for i, im in enumerate(imgs):
        print(f"Monitor {i+1} shape: {im.shape}")
    print("---------------------")

    hi()
    hi_anki()
    config.hi()

    print("Started. Ctrl+C to stop.")
    counter = 0
    start_time = time.time()

    try:
        while True:
            counter += 1
            if tm.check(visualize=True):
                print('!!! Found !!!')
            
            if counter % 100 == 0:
                dt = time.time() - start_time
                if dt > 0: print(f"FPS: {10/dt:.2f}")
                utils.profiler.report()
                utils.profiler.clear_stats()
                start_time = time.time()
    except KeyboardInterrupt:
        cv2.destroyAllWindows()