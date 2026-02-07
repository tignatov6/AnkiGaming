import random
import sys
import os
import re

# Добавляем путь для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.anki_connect import AnkiConnect
    anki = AnkiConnect()
except ImportError:
    print("Ошибка: Не найден anki_connect.py")
    anki = None

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsDropShadowEffect, QTextBrowser,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QColor, QCursor 
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None


class LatexRenderer:
    """Конвертер LaTeX в HTML (без внешних зависимостей)"""
    
    GREEK = {
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ', r'\epsilon': 'ε',
        r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ', r'\iota': 'ι', r'\kappa': 'κ',
        r'\lambda': 'λ', r'\mu': 'μ', r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π',
        r'\rho': 'ρ', r'\sigma': 'σ', r'\tau': 'τ', r'\upsilon': 'υ', r'\phi': 'φ',
        r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω', r'\Delta': 'Δ', r'\Sigma': 'Σ',
        r'\cdot': '·', r'\times': '×', r'\pm': '±', r'\infty': '∞', r'\approx': '≈',
        r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\rightarrow': '→', r'\leftarrow': '←',
        r'\Rightarrow': '⇒', r'\forall': '∀', r'\exists': '∃', r'\subset': '⊂',
        r'\in': '∈', r'\cup': '∪', r'\cap': '∩', r'\emptyset': '∅', r'\sqrt': '√',
        r'\int': '∫', r'\sum': '∑', r'\prod': '∏', r'\partial': '∂', r'\nabla': '∇',
    }
    
    @classmethod
    def render(cls, text):
        if not text:
            return text
            
        # Display math \[ ... \]
        text = re.sub(
            r'\\\[\s*(.*?)\s*\\\]',
            lambda m: f'<div style="text-align:center; margin:12px 0; font-size:1.1em;">{cls._render_expr(m.group(1))}</div>',
            text,
            flags=re.DOTALL
        )
        
        # Inline math \( ... \)
        text = re.sub(
            r'\\\(\s*(.*?)\s*\\\)',
            lambda m: cls._render_expr(m.group(1)),
            text,
            flags=re.DOTALL
        )
        
        return text
    
    @classmethod
    def _render_expr(cls, expr):
        expr = expr.strip()
        expr = expr.replace('\\%', '%')
        
        # \frac{a}{b}
        expr = re.sub(
            r'\\frac\{([^}]+)\}\{([^}]+)\}',
            r'<span style="display:inline-block;vertical-align:middle;text-align:center;font-size:0.9em;margin:0 2px;">'
            r'<span style="display:block;border-bottom:1px solid currentColor;padding:0 4px 2px 4px;">\1</span>'
            r'<span style="display:block;padding-top:2px;">\2</span></span>',
            expr
        )
        
        # \sqrt{x}
        expr = re.sub(
            r'\\sqrt\{([^}]+)\}',
            r'<span style="white-space:nowrap;font-size:1.1em;">√<span style="border-top:1.5px solid;padding-top:1px;">\1</span></span>',
            expr
        )
        
        # Индексы
        expr = re.sub(r'\^\{([^}]+)\}', r'<sup style="font-size:0.75em;opacity:0.8;">\1</sup>', expr)
        expr = re.sub(r'_\{([^}]+)\}', r'<sub style="font-size:0.75em;opacity:0.8;">\1</sub>', expr)
        expr = re.sub(r'\^([a-zA-Z0-9])', r'<sup style="font-size:0.75em;opacity:0.8;">\1</sup>', expr)
        expr = re.sub(r'_([a-zA-Z0-9])', r'<sub style="font-size:0.75em;opacity:0.8;">\1</sub>', expr)
        
        # Греческие
        for latex, char in sorted(cls.GREEK.items(), key=lambda x: -len(x[0])):
            pattern = re.escape(latex) + r'(?![a-zA-Z])'
            expr = re.sub(pattern, char, expr)
        
        expr = expr.replace('\\,', ' ').replace('\\;', ' ').replace('\\ ', ' ')
        
        return f'<span style="color: #d1d1d1; font-family:Cambria,Times New Roman,serif;font-style:italic;letter-spacing:0.5px;">{expr}</span>'


class OverlayWindow(QWidget):
    # Сигнал, который испускается при ответе на карту
    card_answered = pyqtSignal(bool, int)

    def __init__(self):
        super().__init__()
        self.is_interactive = True
        self.current_card_data = None 
        self.is_showing_answer = False
        self.media_path = None
        self.media_player = QMediaPlayer()
        
        self.setWindowTitle("Anki Overlay")
        self.resize(600, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.init_ui()
        self.update_click_through()

    def init_ui(self):
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 600, 400)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #2F3136; 
                border-radius: 15px;
                border: 1px solid #40444B;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 15, 15, 15)

        self.header = QLabel("Anki: Загрузка...")
        self.header.setStyleSheet("color: #7289DA; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)

        # QTextBrowser с поддержкой кликов по ссылкам (кнопкам звука)
        self.card_browser = QTextBrowser()
        self.card_browser.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                color: #dcddde;
                font-size: 16px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QTextBrowser a {
                color: #43B581;
                text-decoration: none;
                font-weight: bold;
            }
            QTextBrowser QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QTextBrowser QScrollBar::handle:vertical {
                background: #40444B;
                border-radius: 4px;
                min-height: 30px;
            }
            QTextBrowser QScrollBar::handle:vertical:hover {
                background: #5865F2;
            }
            QTextBrowser QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.card_browser.viewport().setAutoFillBackground(False)
        self.card_browser.setOpenLinks(False)  # Отключаем авто-открытие ссылок
        self.card_browser.anchorClicked.connect(self.on_anchor_clicked)  # Ловим клики по ссылкам
        layout.addWidget(self.card_browser)

        self.btn_show_answer = QPushButton("Показать ответ")
        self.btn_show_answer.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_show_answer.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #4752C4; }
        """)
        self.btn_show_answer.clicked.connect(self.on_show_answer_clicked)
        layout.addWidget(self.btn_show_answer)

        self.answer_buttons_widget = QWidget()
        self.answer_buttons_layout = QHBoxLayout(self.answer_buttons_widget)
        self.answer_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.answer_buttons_layout.setSpacing(10)

        self.create_answer_btn("Снова (1)", "#FF4444", 1)
        self.create_answer_btn("Трудно (2)", "#FF8800", 2)
        self.create_answer_btn("Хорошо (3)", "#00CC00", 3)
        self.create_answer_btn("Легко (4)", "#00AAFF", 4)

        layout.addWidget(self.answer_buttons_widget)
        self.answer_buttons_widget.hide()

    def create_answer_btn(self, text, hover_color, ease_value):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #36393F;
                color: white;
                border: 1px solid #202225;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: #FFFFFF;
                border: 1px solid {hover_color};
            }}
        """)
        btn.clicked.connect(lambda: self.submit_answer(ease_value))
        self.answer_buttons_layout.addWidget(btn)

    def on_anchor_clicked(self, url):
        """Обработка кликов по ссылкам (кнопкам звука)"""
        if url.scheme() == "sound":
            filename = url.toString(QUrl.RemoveScheme)[2:]  # убираем sound://
            self.play_sound(filename)

    def play_sound(self, filename):
        """Воспроизводит звуковой файл"""
        if not self.media_path:
            return
            
        filepath = os.path.join(self.media_path, filename)
        if os.path.exists(filepath):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.media_player.play()
        else:
            print(f"Файл не найден: {filepath}")

    def process_sounds_to_buttons(self, html):
        """
        Заменяет [sound:...] на стилизованные кнопки (ссылки) прямо в тексте
        """
        def sound_to_button(match):
            filename = match.group(1)
            # Создаем "кнопку" через стилизованную ссылку
            return f'''
                <a href="sound://{filename}" style="
                    display:inline-block;
                    background-color:#43B581;
                    color:white;
                    padding:2px 8px;
                    margin:0 2px;
                    border-radius:4px;
                    text-decoration:none;
                    font-size:0.85em;
                    font-weight:bold;
                    vertical-align:middle;
                    font-family:Segoe UI,sans-serif;
                ">▶</a>
            '''
        
        # Заменяем [sound:...] на кнопки
        processed = re.sub(r'\[sound:(.*?)\]', sound_to_button, html)
        return processed

    def load_card(self, card_id):
        if not anki:
            self.card_browser.setText("Ошибка: Нет anki_connect")
            return

        try:
            self.answer_buttons_widget.hide()
            self.btn_show_answer.show()
            self.btn_show_answer.setText("Показать ответ")
            self.is_showing_answer = False
            self.media_player.stop()

            try:
                self.media_path = anki.getMediaDirPath()
            except:
                self.media_path = None

            card_info_list = anki.cardsInfo([card_id])
            if not card_info_list:
                self.card_browser.setText("Карта не найдена.")
                return
            
            card_info = card_info_list[0]
            model_name = card_info['modelName']
            deck_name = card_info['deckName']
            fields = card_info['fields']
            
            templates_dict = anki.modelTemplates(modelName=model_name)
            print(templates_dict
                  )
            if templates_dict and isinstance(templates_dict, dict):
                template = next(iter(templates_dict.values()))
            else:
                template = {'Front': '{{Front}}', 'Back': '{{Back}}'}

            css_data = anki.modelStyling(modelName=model_name)
            css = css_data.get('css', '') if css_data else ""
            
            # === ИЗМЕНЕНИЯ ЗДЕСЬ (CSS) ===
            # Принудительно устанавливаем прозрачный фон и серый цвет текста
            force_css = """
                /* Агрессивный сброс стилей для всех основных текстовых тегов */
                body, div, p, span, h1, h2, h3, h4, h5, h6, 
                font, table, td, th, ul, ol, li, dl, dt, dd, blockquote, section { 
                    background-color: transparent !important; 
                    color: #d1d1d1 !important; /* Светло-серый цвет для всего текста */
                }
                
                /* Класс .card часто используется в Anki, перекрываем его отдельно */
                .card { 
                    background-color: transparent !important; 
                    color: #d1d1d1 !important;
                }
                
                /* Жирный текст делаем ярко-белым для контраста */
                b, strong, th { color: #ffffff !important; }
                
                /* Курсив */
                i, em { color: #e0e0e0 !important; }
                
                /* Ссылки (чтобы отличались) */
                a { color: #00b0f4 !important; }
                
                /* Мелкий текст */
                small { color: #aaaaaa !important; }
                
                /* Изображения */
                img { max-width: 100%; height: auto; border-radius: 5px; }
            """
            # Добавляем наш CSS после CSS колоды, чтобы наши rules с !important сработали
            css = css + "\n" + force_css

            def render_template(template_html):
                html = template_html
                for field_name, field_data in fields.items():
                    value = field_data['value']
                    
                    # Заменяем поля
                    html = html.replace(f'{{{{{field_name}}}}}', value)
                    
                    # Условные поля
                    start_tag = f'{{{{#{field_name}}}}}'
                    end_tag = f'{{{{/{field_name}}}}}'
                    if start_tag in html:
                        if value.strip():
                            html = html.replace(start_tag, '').replace(end_tag, '')
                        else:
                            pattern = f'{re.escape(start_tag)}(.*?){re.escape(end_tag)}'
                            html = re.sub(pattern, '', html, flags=re.DOTALL)
                return html

            front_html = render_template(template.get('Front', '{{Front}}'))
            back_html = render_template(template.get('Back', '{{Back}}'))

            # Замена {{FrontSide}}
            if '{{FrontSide}}' in back_html:
                back_html = back_html.replace('{{FrontSide}}', front_html)

            # Заменяем звуки на кнопки
            front_html = self.process_sounds_to_buttons(front_html)
            back_html = self.process_sounds_to_buttons(back_html)

            # LaTeX рендеринг
            front_html = LatexRenderer.render(front_html)
            back_html = LatexRenderer.render(back_html)

            self.current_card_data = {
                'id': card_id,
                'front': front_html,
                'back': back_html,
                'css': css,
                'deck': deck_name
            }
            
            self.header.setText(f"Колода: {deck_name}")
            self.render_card(side='front')
            
        except Exception as e:
            self.card_browser.setText(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()

    def render_card(self, side='front'):
        if not self.current_card_data: 
            return
            
        css = self.current_card_data['css']
        content = self.current_card_data[side]

        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{css}
</style>
</head>
<body>
<div class="card">{content}</div>
</body>
</html>"""
        
        if self.media_path:
            self.card_browser.document().setBaseUrl(QUrl.fromLocalFile(self.media_path + "/"))
        
        self.card_browser.setHtml(full_html)

    def on_show_answer_clicked(self):
        if not self.current_card_data: 
            return
        self.render_card(side='back')
        self.btn_show_answer.hide()
        self.answer_buttons_widget.show()
        self.is_showing_answer = True

    def submit_answer(self, ease):
        if not self.current_card_data: 
            return
        card_id = self.current_card_data['id']
        
        try:
            anki.answerCards(answers=[{"cardId": card_id, "ease": ease}])
            self.header.setText("Ответ принят...")
            
            # === ИСПРАВЛЕНИЕ ОШИБКИ ЗДЕСЬ ===
            # Было: self.card_card_answered.emit(True, card_id)
            # Стало: self.card_answered.emit(True, card_id)
            self.card_answered.emit(True, card_id)
            
        except Exception as e:
            print(f"Ошибка ответа: {e}")

    def toggle_interaction_mode(self):
        self.is_interactive = not self.is_interactive
        if self.is_interactive:
            self.container.setStyleSheet(self.container.styleSheet().replace("rgba(47, 49, 54, 150)", "#2F3136"))
            self.header.setText("Режим: Интерактивный")
        else:
            self.container.setStyleSheet(self.container.styleSheet().replace("#2F3136", "rgba(47, 49, 54, 150)"))
            self.header.setText("Режим: Locked")
        self.update_click_through()

    def update_click_through(self):
        if not win32gui: 
            return
        try:
            hwnd = self.winId().__int__()
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if not self.is_interactive:
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
            else:
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style & ~win32con.WS_EX_TRANSPARENT)
        except Exception: 
            pass

    def mousePressEvent(self, event):
        if self.is_interactive and event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.is_interactive and hasattr(self, 'old_pos'):
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()


if __name__ == "__main__":
    import keyboard
    
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.show()

    def get_next_card():
        if not anki: 
            return None
        cards = anki.findCards("is:due")
        if cards:
            return random.choice(cards)
        
        cards = anki.findCards("is:new")
        if cards:
            return random.choice(cards)
            
        cards = anki.findCards("")
        if cards:
            return random.choice(cards)
            
        return None

    def load_next_cycle(success=True, prev_card_id=None):
        if prev_card_id:
            print(f"Карта {prev_card_id} решена. Ищем следующую...")
        
        next_id = get_next_card()
        
        if next_id:
            print(f"Загрузка карты: {next_id}")
            QTimer.singleShot(150, lambda: overlay.load_card(next_id))
        else:
            overlay.header.setText("Все карты пройдены!")
            overlay.card_browser.setHtml("<h2 align='center' style='color:#43B581'>Поздравляем! На сегодня всё.</h2>")
            overlay.answer_buttons_widget.hide()
            overlay.btn_show_answer.hide()

    overlay.card_answered.connect(load_next_cycle)
    print("Старт приложения...")
    load_next_cycle() 

    keyboard.add_hotkey('insert', overlay.toggle_interaction_mode)
    
    sys.exit(app.exec_())