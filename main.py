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

class Feeder(QLabel):
    """
    Draggable feeder window.
    """
    def __init__(self):
        super().__init__()
        # Borderless, always-on-top, transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        feeder_path = get_resource_path("feeder.png")
        print("[FEEDER] Loading from:", feeder_path)

        self.feederImage = QPixmap(feeder_path)
        if self.feederImage.isNull():
            print("[FEEDER] WARNING: Null pixmap. Check file name and path.")
        else:
            print("[FEEDER] Feeder image loaded successfully!")

        self.feederSize = 42
        self.setFixedSize(self.feederSize, self.feederSize)

        # Scale the feeder image
        scaledFeeder = self.feederImage.scaled(
            self.feederSize, self.feederSize,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(scaledFeeder)

        self.move(400, 400)
        self.dragging = False
        self.dragOffset = QPoint(0, 0)

        self.show()
        print("[FEEDER] Feeder spawned and shown at (400, 400)")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragOffset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            newPos = event.globalPos() - self.dragOffset
            self.move(newPos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

class DesktopCat(QLabel):
    """
    The oneko-like cat with modes:
      - follow: follows the mouse
      - wait: stays in place (sleeping)
      - chill: spawns a feeder and, every 5 minutes, moves to eat, then returns.
    """
    def __init__(self):
        super().__init__()

        self.debug = False  # Set to True to see console logs

        # Borderless, always-on-top, transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if self.debug:
            print("[INIT] Window configured (borderless, always on top, transparent)")

        # Load sprite sheet
        sprite_path = get_resource_path("oneko.gif")
        self.spriteSheet = QPixmap(sprite_path)
        self.spriteSize = 32
        if self.debug:
            print(f"[INIT] Loading sprite sheet from: {sprite_path}")
            print(f"[INIT] Sprite sheet dimensions: {self.spriteSheet.width()}x{self.spriteSheet.height()}")

        # Initial cat position
        self.catX = 200
        self.catY = 200
        self.mode = "follow"   # follow, wait, chill
        self.dragging = False
        self.dragOffset = QPoint(0, 0)
        self.lastValidMousePos = (self.catX, self.catY)

        # oneko-like logic
        self.frameCount = 0
        self.idleTime = 0
        self.idleAnimation = None
        self.idleAnimationFrame = 0
        self.nekoSpeed = 10

        # Chill/eating logic
        self.feeder = None
        self.eatingTimer = None
        self.eatingCycleActive = False
        self.eatingPhase = None  # "move_to_feeder", "eating", "move_to_sleep"
        self.eatingCounter = 0
        self.sleepingSpot = (self.catX, self.catY)

        # Sprites with negative offsets
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

        # Configure initial label size & position
        self.setFixedSize(self.spriteSize, self.spriteSize)
        self.move(self.catX, self.catY)
        if self.debug:
            print(f"[INIT] Cat initial position: ({self.catX}, {self.catY})")

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
            # Spawn or show the feeder
            if self.feeder is None:
                self.feeder = Feeder()
                self.feeder.show()
                if self.debug:
                    print("[MODE] Feeder spawned and shown")
            else:
                self.feeder.show()
                if self.debug:
                    print("[MODE] Feeder already exists and is shown")

            # Start an eating timer (5 minutes)
            if self.eatingTimer is None:
                self.eatingTimer = QTimer()
                self.eatingTimer.timeout.connect(self.startEatingCycle)
                self.eatingTimer.start(300000)  # 5 minutes
                if self.debug:
                    print("[MODE] Eating timer started (5-minute interval)")
        else:
            # Stop feeder and eating cycle
            if self.eatingTimer is not None:
                self.eatingTimer.stop()
                self.eatingTimer = None
            if self.feeder is not None:
                self.feeder.close()
                self.feeder = None
            self.eatingCycleActive = False
            self.eatingPhase = None

        if self.debug:
            print(f"[MODE] Mode changed to: {mode}")

    def startEatingCycle(self):
        """
        Initiates the eating cycle in chill mode.
        The cat moves from its current position to the feeder,
        eats, then returns to the same position.
        """
        if self.mode != "chill":
            return
        # Store the cat's current position so we can return here afterwards
        self.sleepingSpot = (self.catX, self.catY)

        if self.debug:
            print("[EATING] Starting eating cycle from sleepingSpot=", self.sleepingSpot)

        self.eatingCycleActive = True
        self.eatingPhase = "move_to_feeder"
        self.eatingCounter = 0

    def updateFrame(self):
        """Called ~10 times per second to update logic and sprite."""
        self.frameCount += 1
        if self.debug:
            print(f"[FRAME] FrameCount={self.frameCount}, Mode={self.mode}")

        if self.mode == "follow":
            self.logicFollow()
        elif self.mode == "wait":
            self.logicWait()
        elif self.mode == "chill":
            self.logicChill()

    # ----------------- MODE LOGIC ----------------- #

    def logicFollow(self):
        """
        Follow mode:
          - If mouse is within screen, cat chases it.
          - If mouse is out of screen, cat moves to last known position and idles.
        """
        sw, sh = pyautogui.size()
        mx, my = pyautogui.position()
        if self.debug:
            print(f"[FOLLOW] Mouse=({mx},{my}), Screen=({sw},{sh})")
        
        if 0 <= mx <= sw and 0 <= my <= sh:
            targetX, targetY = mx, my
            self.lastValidMousePos = (mx, my)
        else:
            targetX, targetY = self.lastValidMousePos
            if self.debug:
                print(f"[FOLLOW] Mouse out of bounds, using last valid pos={self.lastValidMousePos}")

        diffX = self.catX - targetX
        diffY = self.catY - targetY
        dist = math.sqrt(diffX**2 + diffY**2)

        if dist < self.nekoSpeed or dist < 48:
            if self.debug:
                print("[FOLLOW] Close to target => doIdle()")
            self.doIdle()
            return

        # Cancel idle animation
        self.idleAnimation = None
        self.idleAnimationFrame = 0

        # Alert animation if idleTime is high
        if self.idleTime > 1:
            self.setSprite("alert", 0)
            self.idleTime = min(self.idleTime, 7)
            self.idleTime -= 1
            return

        # Compute direction
        direction = ""
        if diffY / dist > 0.5:
            direction += "N"
        elif diffY / dist < -0.5:
            direction += "S"
        if diffX / dist > 0.5:
            direction += "W"
        elif diffX / dist < -0.5:
            direction += "E"

        self.setSprite(direction, self.frameCount)
        self.catX -= (diffX / dist) * self.nekoSpeed
        self.catY -= (diffY / dist) * self.nekoSpeed

        # Screen bounds
        self.catX = max(16, min(sw - 16, self.catX))
        self.catY = max(16, min(sh - 16, self.catY))
        self.move(int(self.catX), int(self.catY))

    def logicWait(self):
        """Wait mode: cat sleeps, user can drag it."""
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

    def logicChill(self):
        """
        Chill mode: cat sleeps unless an eating cycle is active.
        Then it moves to the feeder, eats, and returns.
        """
        if self.eatingCycleActive:
            if self.eatingPhase == "move_to_feeder":
                if not self.feeder:
                    # No feeder => abort
                    self.eatingCycleActive = False
                    self.eatingPhase = None
                    return

                feeder_center = (
                    self.feeder.x() + self.feeder.width() / 2,
                    self.feeder.y() + self.feeder.height() + 5
                )
                diffX = self.catX - feeder_center[0]
                diffY = self.catY - feeder_center[1]
                dist = math.sqrt(diffX**2 + diffY**2)

                if dist < self.nekoSpeed or dist < 10:
                    self.eatingPhase = "eating"
                    self.eatingCounter = 0
                else:
                    self.catX -= (diffX / dist) * self.nekoSpeed
                    self.catY -= (diffY / dist) * self.nekoSpeed
                    sw, sh = pyautogui.size()
                    self.catX = max(16, min(sw - 16, self.catX))
                    self.catY = max(16, min(sh - 16, self.catY))
                    self.move(int(self.catX), int(self.catY))

                    # Optional movement sprite
                    direction = ""
                    if diffY / dist > 0.5:
                        direction += "N"
                    elif diffY / dist < -0.5:
                        direction += "S"
                    if diffX / dist > 0.5:
                        direction += "W"
                    elif diffX / dist < -0.5:
                        direction += "E"
                    self.setSprite(direction, self.frameCount)
                return

            elif self.eatingPhase == "eating":
                self.eatingCounter += 1
                # "scratchSelf" used as a placeholder for eating
                self.setSprite("scratchSelf", self.eatingCounter)

                # 5 seconds of eating
                if self.eatingCounter > 50:
                    self.eatingPhase = "move_to_sleep"
                return

            elif self.eatingPhase == "move_to_sleep":
                targetX, targetY = self.sleepingSpot
                diffX = self.catX - targetX
                diffY = self.catY - targetY
                dist = math.sqrt(diffX**2 + diffY**2)

                if dist < self.nekoSpeed or dist < 10:
                    # Done
                    self.eatingCycleActive = False
                    self.eatingPhase = None
                else:
                    self.catX -= (diffX / dist) * self.nekoSpeed
                    self.catY -= (diffY / dist) * self.nekoSpeed
                    sw, sh = pyautogui.size()
                    self.catX = max(16, min(sw - 16, self.catX))
                    self.catY = max(16, min(sh - 16, self.catY))
                    self.move(int(self.catX), int(self.catY))

                    direction = ""
                    if diffY / dist > 0.5:
                        direction += "N"
                    elif diffY / dist < -0.5:
                        direction += "S"
                    if diffX / dist > 0.5:
                        direction += "W"
                    elif diffX / dist < -0.5:
                        direction += "E"
                    self.setSprite(direction, self.frameCount)
                return

        # If no eating cycle, cat sleeps in place
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
        Idle for follow mode. 
        If idleTime passes threshold + random chance, pick an idle animation.
        """
        self.idleTime += 1

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
        """Crop from sprite sheet based on negative offsets (oneko.js style)."""
        if name not in self.spriteSets:
            name = "idle"
        frames = self.spriteSets[name]
        ox, oy = frames[frame % len(frames)]
        xPix = -ox * self.spriteSize
        yPix = -oy * self.spriteSize

        rect = QRect(xPix, yPix, self.spriteSize, self.spriteSize)
        framePix = self.spriteSheet.copy(rect)
        self.setPixmap(framePix)

    # ----------------- DRAGGABLE ----------------- #
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragOffset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Allows the cat to be dragged in 'wait' or 'chill' mode."""
        if self.dragging and (self.mode in ["wait", "chill"]):
            globalPos = event.globalPos()
            newX = globalPos.x() - self.dragOffset.x()
            newY = globalPos.y() - self.dragOffset.y()
            sw, sh = pyautogui.size()
            self.catX = max(0, min(sw - self.width(), newX))
            self.catY = max(0, min(sh - self.height(), newY))
            self.move(int(self.catX), int(self.catY))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

# ----------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    if getattr(sys, 'frozen', False):
        print("[MAIN] Running in compiled (frozen) mode")
    else:
        print("[MAIN] Running in development mode")

    cat = DesktopCat()

    trayIconPath = get_resource_path("gatito.ico")
    trayIcon = QSystemTrayIcon(QIcon(trayIconPath), parent=app)
    if trayIcon.icon().isNull():
        print("[MAIN] Warning: Tray icon failed to load from:", trayIconPath)
    else:
        print(f"[MAIN] Tray icon loaded from: {trayIconPath}")

    trayMenu = QMenu()
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
