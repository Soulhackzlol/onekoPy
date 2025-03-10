
![image (7)](https://github.com/user-attachments/assets/471d9236-4789-414a-af82-4791cb694884)

```                    __         ____       
  ____  ____  ___  / /______  / __ \__  __
 / __ \/ __ \/ _ \/ //_/ __ \/ /_/ / / / /
/ /_/ / / / /  __/ ,< / /_/ / ____/ /_/ / 
\____/_/ /_/\___/_/|_|\____/_/    \__, /  
                                 /____/    
```                                               
onekoPy is a Python-based implementation of the classic 'Oneko' desktop cat that follows your mouse pointer. It includes additional features and modes for more interaction.

## Features
- **Follow Mode**: The cat follows your mouse cursor across the screen.
- **Wait Mode**: The cat stays idle but can be dragged.
- **Chill Mode**: The cat remains still but occasionally moves slightly (needs a rework tbh).
- **System Tray Menu**: Allows you to switch between modes easily.
- **Draggable**: In certain modes, you can manually move the cat.
- **Idle Animations**: The cat occasionally performs idle actions.

## Installation

### Requirements
Ensure you have Python 3 installed along with the following dependencies:
```sh
pip install pyautogui PyQt5
```

### Running the Program
To start the cat, simply run:
```sh
python onekoPy.py
```

If you want to compile it as an executable (optional):
```sh
pip install pyinstaller
pyinstaller --onefile --noconsole onekoPy.py
```

## Usage
Upon running, the cat will appear on your screen and start following your mouse. You can change its behavior via the system tray menu.

### Controls
- **Right-click on the tray icon** to switch modes or exit the program.
- **Left-click and drag** the cat when in wait/chill mode.

## Customization
To use a different sprite or icon, replace the `oneko.gif` or `gatito.ico` files with your own.

## License
This project is open-source and available under the MIT License.

---
Enjoy your virtual pet! 🐱
