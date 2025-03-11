
![image (7)](https://github.com/user-attachments/assets/471d9236-4789-414a-af82-4791cb694884)

```                    __         ____       
  ____  ____  ___  / /______  / __ \__  __
 / __ \/ __ \/ _ \/ //_/ __ \/ /_/ / / / /
/ /_/ / / / /  __/ ,< / /_/ / ____/ /_/ / 
\____/_/ /_/\___/_/|_|\____/_/    \__, /  
                                 /____/    
```                                               
# onekoPy 🐱  
*A Python-based virtual desktop cat that follows your cursor—with extra features and modes for more interactivity!*

The latest update introduces:  
✅ A **draggable feeder** in **Chill Mode**  
✅ An **improved eating cycle** where the cat sleeps until every 5 minutes when it moves, "eats," and returns to its spot  

---

## 🎮 Features

### 🏃 Follow Mode
- The cat follows your mouse cursor across the screen.

### 😴 Wait Mode
- The cat stays idle (in a sleeping state) but can be repositioned via drag-and-drop.

### 💤 Chill Mode
- The cat remains in a **sleeping pose** without random movement.
- Every **5 minutes**, an **eating cycle** is triggered:
  1. The cat moves smoothly to a **draggable feeder**.
  2. Performs an **eating animation** for ~5 seconds.
  3. Returns **precisely** to its original sleeping spot.

### 🎛️ System Tray Menu
- Easily switch between modes or exit the application via a tray icon.

### 🖱️ Draggable Elements
- In **Wait** and **Chill** modes, you can **manually reposition** the cat (and the feeder in Chill mode).

### 🎭 Idle Animations
- The cat occasionally performs idle animations in **Follow Mode**.

### 🛠️ Enhanced Debug Logging
- Optional logging helps troubleshoot behavior and verify resource loading.

### 🖥️ PyInstaller Compatibility
- Designed to be compiled into a **standalone executable for Windows**.

---

## 📥 Download & Run (No Installation Required)  
1. Go to **[Releases](https://github.com/Soulhackzlol/onekoPy/releases)**.  
2. Download the **latest version**.  
3. **Run it!** 🎉  

---

## 🔧 Installation (For Developers)
### 🔹 Requirements
Ensure you have Python 3 installed along with the following dependencies:
```sh
pip install pyautogui PyQt5
```

### 🚀 Running the Program
To start the cat, simply run:
```sh
python main.py
```

If you want to compile it as an executable (optional):
```sh
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "oneko.gif;." --add-data "gatito.ico;." --add-data "feeder.png;." --icon=gatito.ico main.py
```
This will create an executable in the dist folder.

## 🕹️ Usage and Controls
Upon running, the cat will appear on your screen and start following your mouse. You can change its behavior via the system tray menu.

- **Right-click on the tray icon** to switch modes or exit the program.
- **Left-click and drag** the cat when in wait/chill mode.

## 🎨 Customization
Want a different look? Replace these files with your own images:

- oneko.gif (cat sprite)
- gatito.ico (icon)
- feeder.png (feeder)
⚠️ Ensure images maintain the correct dimensions (e.g., the sprite sheet should be 256×128 pixels).

## 📜 License
This project is open-source and available under the MIT License.

---
Enjoy your virtual pet! 🐱
