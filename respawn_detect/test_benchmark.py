import time
import mss
import pyautogui
import numpy as np
import cv2
import ctypes

# DPI Fix
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

ITERATIONS = 1000 

# === Копируем логику обрезки 1-в-1 из основного скрипта ===
def crop_black_borders(img):
    if img.size == 0: return img
    if np.any(img[0,0] > 0) and np.any(img[-1,-1] > 0): return img
    
    rows = np.any(img, axis=(1, 2))
    cols = np.any(img, axis=(0, 2))
    
    if not np.any(rows) or not np.any(cols): return img
    
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    return img[ymin:ymax+1, xmin:xmax+1]

def benchmark_mss_capture_split_crop():
    print(f"\n--- MSS: Capture All -> Convert RGB -> Split -> Crop ---")
    sct = mss.mss()
    virtual_screen = sct.monitors[0]
    physical_monitors = sct.monitors[1:]
    
    base_x = virtual_screen['left']
    base_y = virtual_screen['top']
    
    start = time.time()
    
    for _ in range(ITERATIONS):
        # 1. Grab
        full_sct = sct.grab(virtual_screen)
        full_img = np.array(full_sct)
        
        # 2. Convert BGRA -> RGB (Тяжелая операция!)
        full_rgb = cv2.cvtColor(full_img, cv2.COLOR_BGRA2RGB)
        
        # 3. Split & Crop
        processed_images = []
        for mon in physical_monitors:
            rel_x = mon['left'] - base_x
            rel_y = mon['top'] - base_y
            w = mon['width']
            h = mon['height']
            
            mon_img = full_rgb[rel_y:rel_y+h, rel_x:rel_x+w]
            clean_img = crop_black_borders(mon_img)
            processed_images.append(clean_img)

    dt = time.time() - start
    fps = ITERATIONS / dt
    print(f"Средний FPS: {fps:.2f}")
    return fps

def benchmark_pyautogui_capture_split_crop():
    print(f"\n--- PyAutoGUI: Screenshot All -> Split -> Crop ---")
    
    # PyAutoGUI не дает инфу о мониторах, берем её у MSS для нарезки
    with mss.mss() as sct:
        virtual_screen = sct.monitors[0]
        physical_monitors = sct.monitors[1:]
        base_x = virtual_screen['left']
        base_y = virtual_screen['top']

    start = time.time()
    
    for _ in range(ITERATIONS):
        # 1. Grab (PIL Image)
        img_pil = pyautogui.screenshot(allScreens=True)
        
        # 2. Convert to Numpy (Тяжелая операция!)
        # PyAutoGUI возвращает RGB, конвертить цвета не надо, но надо перегнать данные в array
        full_rgb = np.array(img_pil)
        
        # 3. Split & Crop
        processed_images = []
        for mon in physical_monitors:
            rel_x = mon['left'] - base_x
            rel_y = mon['top'] - base_y
            w = mon['width']
            h = mon['height']
            
            # Проверка границ, т.к. pyautogui может вернуть размер чуть отличный от mss из-за DPI
            if rel_y+h <= full_rgb.shape[0] and rel_x+w <= full_rgb.shape[1]:
                mon_img = full_rgb[rel_y:rel_y+h, rel_x:rel_x+w]
                clean_img = crop_black_borders(mon_img)
                processed_images.append(clean_img)

    dt = time.time() - start
    fps = ITERATIONS / dt
    print(f"Средний FPS: {fps:.2f}")
    return fps

if __name__ == "__main__":
    print("Запуск полного бенчмарка (потолок производительности)...")
    print(f"Итераций: {ITERATIONS}")
    
    fps_mss = benchmark_mss_capture_split_crop()
    fps_py = benchmark_pyautogui_capture_split_crop()
    
    print("\n" + "="*40)
    print("       РЕАЛЬНЫЙ ПОТОЛОК (Capture+Proc)")
    print("="*40)
    print(f"MSS Full Pipeline:       {fps_mss:.2f} FPS")
    print(f"PyAutoGUI Full Pipeline: {fps_py:.2f} FPS")
    print("="*40)
    
    print("\nАНАЛИЗ:")
    print(f"Текущая скорость захвата (MSS): ~{1000/fps_mss:.1f} мс")
    print("Если у тебя в профайлере capture_all_and_split ~76мс,")
    print("значит основное время уходит на cv2.cvtColor и перекладку памяти.")