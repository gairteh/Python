'''
2024-03-28
source: 
  https://zetcode.com/gui/pyqt5/eventssignals/
  https://stackoverflow.com/questions/67725534/how-to-draw-directly-on-screen-in-windows-with-python
 
실행하면 기본적으로 main screen에서만 마우스 주변에 빨간색 네모를 보여준다.
키보드 2 키를 누르면 전체 스크린에서 연두색 네모를 보여준다. (다소 cpu를 사용하여 느리다)
키보드 1 키를 누르면 main screen에서만 빨간색 네모를 보여준다.
  
_1.py 버전보다 좀더 간소화했음.
 
키:
a: all screens
1: the main screen
2: the 2nd screen
n: the nth screen
 
화면이 총 2개인데 2보다 큰 숫자를 누르면 아무 변화 없음.
 

pip install pyqt5
pip install Pillow
pip install pywin32
pip install keyboard
'''
 
import sys
 
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QApplication
from PIL import ImageGrab
from io import BytesIO
import win32clipboard
import keyboard

# Global variables for circle parameters
square_width = 50
 
class GameOverlay(QWidget):
    def __init__(self, app, ts):
        super().__init__()
 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        geometries = get_screen_geometries()
        self.geometries = geometries
        # ex: geometries = [PyQt5.QtCore.QRect(0, 0, 3840, 2160), PyQt5.QtCore.QRect(-2160, 0, 2160, 3840)]
        united_rect = QRect()
            
        for geometry in self.geometries: 
            united_rect = united_rect.united(geometry)
        #ex: united_rect = PyQt5.QtCore.QRect(-2160, 0, 6000, 3840)
        self.target_screen = ts
        # self.target_screen == "all" 일 수도 있기 때문에 우선 int인지 확인.
        if isinstance(self.target_screen, int):
            # 만약 self.target_screen의 값이 모니터 개수보다 많으면 마지막 모니터를 할당
            if self.target_screen > len(self.geometries):
                self.target_screen = len(self.geometries)
                
        # self.target_screen = "main"
        if self.target_screen == "all":
            self.setGeometry(united_rect.left(), united_rect.top(), united_rect.width(), united_rect.height())  # Set the overlay size to match the screen
            self.outline_color = Qt.green
 
        for i in range (1, len(self.geometries)+1):
            if self.target_screen == i:
                self.setGeometry(self.geometries[i-1].left(), self.geometries[i-1].top(), self.geometries[i-1].width(), self.geometries[i-1].height())  # Set the overlay size to match the screen
                self.outline_color = Qt.red
        self.x
        self.y
        self.width
        self.height
 
        self.show()
        
        # 이게 없으면 ESC키를 눌렀을 때, self.app.quit()를 실행해야 하는데 self.app이 없어서 에러가 난다.
        self.app = app  # self.app refers to the external given app
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw the square around the mouse cursor
        mouse_pos = QApplication.desktop().cursor().pos()
        self.x = mouse_pos.x() - square_width
        self.y = mouse_pos.y() - square_width
        self.width = square_width
        self.height = square_width
        # 마우스가 왼쪽 최상단에 있을 때, mouse_pos_local.x(), mouse_pos_local.y()은 각각 0, 0이 나온다.
        mouse_pos_local = self.mapFromGlobal(mouse_pos)
        # Draw the rectangle outline
        painter.setPen(QColor(self.outline_color))
        # -1, -1, +1, +1 보정을 안 해주면, 예를들어 네모 가이드도 50px, 캡쳐도 50px이라서 네모의 위쪽과 왼쪽의 선이 캡쳐에 포함된다. 그래서 네모 가이드는 실제로 가로가 51px이고 시작위치는 마우스로부터 -51px 위치인 것이다.
        painter.drawRect(mouse_pos_local.x() - square_width -1 , mouse_pos_local.y() - square_width - 1, square_width + 1, square_width + 1)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            imagecapture(self.x, self.y, self.x + self.width, self.y + self.height)

    def keyPressEvent(self, event):
        global square_width
        # print(event.key())
        if event.key() == Qt.Key_Up:
            square_width += 10
            self.update()
        elif event.key() == Qt.Key_Down:
            square_width -= 10
            self.update()
        elif event.key() == Qt.Key_Escape:
            self.app.quit()
        elif event.key() == Qt.Key.Key_A:
            self.rect = GameOverlay(self.app, "all")
            # print(self.rect)
            self.timer = QTimer()
            self.timer.timeout.connect(self.rect.update)
            self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
            self.close()
        elif event.key() == Qt.Key.Key_X:
            imagecapture(self.x, self.y, self.x + self.width, self.y + self.height)
        # if a number key is pressed (currently the keypad is ignored):
        elif event.key() >= Qt.Key.Key_0 and event.key() <= Qt.Key.Key_9:
            key = event.key() - Qt.Key.Key_0
            # 만약 입력한 숫자의 값이 모니터 개수보다 많으면 모니터를 변경하지 않고, 적을 때만 변경함.
            if key <= len(self.geometries):
                if event.key() == Qt.Key.Key_1:
                    self.rect = GameOverlay(self.app, 1)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_2:
                    self.rect = GameOverlay(self.app, 2)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_3:
                    self.rect = GameOverlay(self.app, 3)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_4:
                    self.rect = GameOverlay(self.app, 4)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_5:
                    self.rect = GameOverlay(self.app, 5)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_6:
                    self.rect = GameOverlay(self.app, 6)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_7:
                    self.rect = GameOverlay(self.app, 7)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_8:
                    self.rect = GameOverlay(self.app, 8)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
                elif event.key() == Qt.Key.Key_9:
                    self.rect = GameOverlay(self.app, 9)
                    self.timer = QTimer()
                    self.timer.timeout.connect(self.rect.update)
                    self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
                    self.close()
 
def get_screen_geometries():
    screens = QApplication.screens()
    screen_geometries = []
    
    for screen in screens:
        screen_geometries.append(screen.geometry())
    # print("Screen geometries:", screen_geometries)
    # ex: Screen geometries: [PyQt5.QtCore.QRect(0, 0, 3840, 2160), PyQt5.QtCore.QRect(-2160, 0, 2160, 3840)]
    return screen_geometries
 
def imagecapture(left, top, right, bottom):
    # with width or height is negative, exchange.
    if right < left:
        temp = left
        left = right
        right = temp
    if bottom < top:
        temp = top
        top = bottom
        bottom = temp

    # Capture the square
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)

    # Convert the image to bytes and save it to clipboard
    img_byte_array = BytesIO() 
    screenshot.save(img_byte_array, format='PNG')

    output = BytesIO() # <class '_io.BytesIO'>
    screenshot.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:] # <class 'bytes'>
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def main():
    app = QApplication(sys.argv)
    rect = GameOverlay(app,  "all")
    timer = QTimer()
    timer.timeout.connect(rect.update)
    timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)
 
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()
 
 