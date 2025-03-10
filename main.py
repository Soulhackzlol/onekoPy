import sys
import os
import random
import math
import pyautogui
from PyQt5.QtWidgets import (
    QApplication, QLabel, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint

def get_resource_path(relative_path):
    """
    Returns the absolute path to the resource,
    working both in development and when compiled with PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DesktopCat(QLabel):
    """
    Displays a floating cat on the desktop with multiple modes:
      - follow: Follows the mouse pointer
      - wait: Remains stationary (sleeping) but can be dragged
      - chill: Mostly remains stationary, but occasionally moves slightly
    Debug logs are included for troubleshooting.
    """
    def __init__(self):
        super().__init__()

        self.debug = False  # Enable/disable debug logging

        # Configure a borderless, always-on-top, transparent window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if self.debug:
            print("[INIT] Window configured (borderless, always on top, transparent)")

        # Load the sprite sheet (oneko.gif, 256×128, 8×4 frames)
        sprite_path = get_resource_path("oneko.gif")
        self.spriteSheet = QPixmap(sprite_path)
        self.spriteSize = 32
        if self.debug:
            print(f"[INIT] Loading sprite sheet from: {sprite_path}")
            print(f"[INIT] Sprite sheet dimensions: {self.spriteSheet.width()}x{self.spriteSheet.height()}")

        # Cat state variables
        self.mode = "follow"   # Options: follow, wait, chill
        self.dragging = False  # Flag for mouse dragging
        self.dragOffset = QPoint(0, 0)

        # Initial position (x, y) on screen
        self.catX = 200
        self.catY = 200
        self.lastValidMousePos = (self.catX, self.catY)
        
        # oneko logic variables
        self.frameCount = 0
        self.idleTime = 0
        self.idleAnimation = None
        self.idleAnimationFrame = 0
        self.nekoSpeed = 10

        # For "chill" mode: occasional small movement
        self.chillCounter = 0

        # Sprite sets with negative offsets
        self.spriteSets = {
            "idle": [[-3, -3]],
            "alert": [[-7, -3]],
            "scratchSelf": [[-5, 0], [-6, 0], [-7, 0]],
            "scratchWallN": [[0, 0], [0, -1]],
            "scratchWallS": [[-7, -1], [-6, -2]],
            "scratchWallE": [[-2, -2], [-2, -3]],
            "scratchWallW": [[-4, 0], [-4, -1]],
            "tired": [[-3, -2]],
            "sleeping": [[-2, 0], [-2, -1]],
            "N": [[-1, -2], [-1, -3]],
            "NE": [[0, -2], [0, -3]],
            "E": [[-3, 0], [-3, -1]],
            "SE": [[-5, -1], [-5, -2]],
            "S": [[-6, -3], [-7, -2]],
            "SW": [[-5, -3], [-6, -1]],
            "W": [[-4, -2], [-4, -3]],
            "NW": [[-1, 0], [-1, -1]],
        }

        # Set initial size and position
        self.setFixedSize(self.spriteSize, self.spriteSize)
        self.move(self.catX, self.catY)
        if self.debug:
            print(f"[INIT] Initial cat position: ({self.catX}, {self.catY})")

        # Main timer (10 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(100)
        if self.debug:
            print("[INIT] Timer started (10 FPS)")

        self.show()

    def setMode(self, mode):
        """Change the cat's mode: follow, wait, or chill."""
        self.mode = mode
        self.idleAnimation = None
        self.idleAnimationFrame = 0
        self.idleTime = 0
        if mode == "chill":
            self.chillCounter = random.randint(50, 200)
        if self.debug:
            print(f"[MODE] Mode changed to: {mode}")

    def updateFrame(self):
        """Called ~10 times per second to update the logic and sprite."""
        self.frameCount += 1
        if self.debug:
            print(f"[FRAME] FrameCount: {self.frameCount}, Mode: {self.mode}")
        if self.mode == "follow":
            self.logicFollow()
        elif self.mode == "wait":
            self.logicWait()
        elif self.mode == "chill":
            self.logicChill()

    # ----------------- MODE LOGIC METHODS -----------------
    def logicFollow(self):
        """
        Follow mode:
          - If the mouse is within the screen, the cat pursues it and updates the last valid position.
          - If the mouse is outside, the cat moves toward the last valid mouse position and, upon reaching it,
            remains idle until the mouse returns.
        """
        sw, sh = pyautogui.size()
        mx, my = pyautogui.position()
        if self.debug:
            print(f"[FOLLOW] Mouse position: ({mx}, {my}), Screen: ({sw}, {sh})")
        
        # Update last valid position if the mouse is within the screen
        if 0 <= mx <= sw and 0 <= my <= sh:
            targetX, targetY = mx, my
            self.lastValidMousePos = (mx, my)
        else:
            targetX, targetY = self.lastValidMousePos
            if self.debug:
                print(f"[FOLLOW] Mouse out of bounds. Using last valid position: {self.lastValidMousePos}")

        diffX = self.catX - targetX
        diffY = self.catY - targetY
        dist = math.sqrt(diffX**2 + diffY**2)
        if self.debug:
            print(f"[FOLLOW] Difference: ({diffX:.1f}, {diffY:.1f}), Distance: {dist:.1f}")

        # If the cat is already close to the target, enter idle mode
        if dist < self.nekoSpeed or dist < 48:
            if self.debug:
                print("[FOLLOW] Close to target; entering idle mode")
            self.doIdle()
            return

        self.idleAnimation = None
        self.idleAnimationFrame = 0

        if self.idleTime > 1:
            self.setSprite("alert", 0)
            self.idleTime = min(self.idleTime, 7)
            self.idleTime -= 1
            return

        direction = ""
        if diffY / dist > 0.5:
            direction += "N"
        elif diffY / dist < -0.5:
            direction += "S"

        if diffX / dist > 0.5:
            direction += "W"
        elif diffX / dist < -0.5:
            direction += "E"

        if self.debug:
            print(f"[FOLLOW] Calculated direction: {direction}")

        self.setSprite(direction, self.frameCount)
        # Move towards the target
        self.catX -= (diffX / dist) * self.nekoSpeed
        self.catY -= (diffY / dist) * self.nekoSpeed

        # Ensure the cat remains within the screen bounds
        self.catX = max(16, min(sw - 16, self.catX))
        self.catY = max(16, min(sh - 16, self.catY))
        if self.debug:
            print(f"[FOLLOW] New position: ({self.catX:.1f}, {self.catY:.1f})")
        self.move(int(self.catX), int(self.catY))

    def logicWait(self):
        """
        Wait mode:
          - The cat does not pursue the mouse.
          - It remains in a 'sleeping' (or idle) state.
          - The user can drag the cat to reposition it.
        """
        if not self.idleAnimation:
            self.idleAnimation = "sleeping"
            self.idleAnimationFrame = 0
            if self.debug:
                print("[WAIT] Activating sleeping animation")
        if self.idleAnimation == "sleeping":
            if self.idleAnimationFrame < 8:
                self.setSprite("tired", 0)
            else:
                self.setSprite("sleeping", self.idleAnimationFrame // 4)
            if self.idleAnimationFrame > 192:
                self.idleAnimationFrame = 0
            else:
                self.idleAnimationFrame += 1

    def logicChill(self):
        """
        Chill mode:
          - Similar to wait mode (remains asleep), but every X frames it briefly "wakes up"
            and moves slightly (as if adjusting its position), then returns to sleep.
        """
        if self.chillCounter > 0:
            self.chillCounter -= 1
        else:
            # Brief random movement upon "waking"
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)
            self.catX += dx
            self.catY += dy
            sw, sh = pyautogui.size()
            self.catX = max(16, min(sw - 16, self.catX))
            self.catY = max(16, min(sh - 16, self.catY))
            self.move(int(self.catX), int(self.catY))
            if self.debug:
                print(f"[CHILL] Random movement: dx={dx}, dy={dy}")
            self.chillCounter = random.randint(50, 200)
        if not self.idleAnimation:
            self.idleAnimation = "sleeping"
            self.idleAnimationFrame = 0
        if self.idleAnimation == "sleeping":
            if self.idleAnimationFrame < 8:
                self.setSprite("tired", 0)
            else:
                self.setSprite("sleeping", self.idleAnimationFrame // 4)
            if self.idleAnimationFrame > 192:
                self.idleAnimationFrame = 0
            else:
                self.idleAnimationFrame += 1

    def doIdle(self):
        """
        Idle behavior for follow mode.
        Increases idle time and, after a threshold and random chance, activates an idle animation.
        """
        self.idleTime += 1
        if self.debug:
            print(f"[IDLE] Idle time: {self.idleTime}")
        if self.idleTime > 10 and random.randint(0, 200) == 0 and self.idleAnimation is None:
            sw, sh = pyautogui.size()
            available = ["sleeping", "scratchSelf"]
            if self.catX < 32:
                available.append("scratchWallW")
            if self.catY < 32:
                available.append("scratchWallN")
            if self.catX > sw - 32:
                available.append("scratchWallE")
            if self.catY > sh - 32:
                available.append("scratchWallS")
            self.idleAnimation = random.choice(available)
            self.idleAnimationFrame = 0
            if self.debug:
                print(f"[IDLE] Activated animation: {self.idleAnimation}")
        if self.idleAnimation == "sleeping":
            if self.idleAnimationFrame < 8:
                self.setSprite("tired", 0)
            else:
                self.setSprite("sleeping", self.idleAnimationFrame // 4)
            if self.idleAnimationFrame > 192:
                self.idleAnimation = None
                self.idleAnimationFrame = 0
            else:
                self.idleAnimationFrame += 1
        elif self.idleAnimation in (
            "scratchWallN", "scratchWallS",
            "scratchWallE", "scratchWallW", "scratchSelf"
        ):
            self.setSprite(self.idleAnimation, self.idleAnimationFrame)
            if self.idleAnimationFrame > 9:
                self.idleAnimation = None
                self.idleAnimationFrame = 0
            else:
                self.idleAnimationFrame += 1
        else:
            self.setSprite("idle", 0)

    def setSprite(self, name, frame):
        """
        Translates the offset (ox, oy) into a real sub-image from the sprite sheet
        Logs the details if debugging is enabled.
        """
        if name not in self.spriteSets:
            name = "idle"
        frames = self.spriteSets[name]
        ox, oy = frames[frame % len(frames)]
        xPix = -ox * self.spriteSize
        yPix = -oy * self.spriteSize
        if self.debug:
            print(f"[setSprite] Animation: {name}, Frame: {frame}, Offset: ({ox},{oy}), Crop: ({xPix},{yPix})")
        rect = QRect(xPix, yPix, self.spriteSize, self.spriteSize)
        framePix = self.spriteSheet.copy(rect)
        self.setPixmap(framePix)

    # ----------------- DRAGGABLE HANDLING -----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            # Record the offset of the mouse press relative to the window's top-left
            self.dragOffset = event.pos()
            if self.debug:
                print("[DRAG] mousePressEvent - starting drag")
            event.accept()

    def mouseMoveEvent(self, event):
        """Allows the cat to be dragged when in 'wait' or 'chill' mode."""
        if self.dragging and (self.mode in ["wait", "chill"]):
            globalPos = event.globalPos()
            newX = globalPos.x() - self.dragOffset.x()
            newY = globalPos.y() - self.dragOffset.y()
            self.catX = newX
            self.catY = newY
            sw, sh = pyautogui.size()
            self.catX = max(0, min(sw - self.width(), self.catX))
            self.catY = max(0, min(sh - self.height(), self.catY))
            if self.debug:
                print(f"[DRAG] Moving to ({self.catX}, {self.catY})")
            self.move(int(self.catX), int(self.catY))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            if self.debug:
                print("[DRAG] mouseReleaseEvent - ending drag")
            event.accept()

# ----------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    if getattr(sys, 'frozen', False):
        print("[MAIN] Running in compiled (frozen) mode")
    else:
        print("[MAIN] Running in development mode")

    # Create the "pet" (the cat)
    cat = DesktopCat()

    # Create the system tray icon using a local icon (for Windows)
    trayIconPath = get_resource_path("gatito.ico")
    trayIcon = QSystemTrayIcon(QIcon(trayIconPath), parent=app)
    if trayIcon.icon().isNull():
        print("[MAIN] Warning: Tray icon failed to load from:", trayIconPath)
    else:
        print(f"[MAIN] Tray icon loaded from: {trayIconPath}")
    trayMenu = QMenu()

    # Actions for the tray menu
    followAction = QAction("Follow")
    waitAction = QAction("Wait")
    chillAction = QAction("Chill")
    exitAction = QAction("Exit")

    followAction.triggered.connect(lambda: cat.setMode("follow"))
    waitAction.triggered.connect(lambda: cat.setMode("wait"))
    chillAction.triggered.connect(lambda: cat.setMode("chill"))
    exitAction.triggered.connect(app.quit)

    trayMenu.addAction(followAction)
    trayMenu.addAction(waitAction)
    trayMenu.addAction(chillAction)
    trayMenu.addSeparator()
    trayMenu.addAction(exitAction)

    trayIcon.setContextMenu(trayMenu)
    trayIcon.show()
    print("[MAIN] Tray icon displayed")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
