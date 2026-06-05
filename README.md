🚀 F34kY C0re
F34kY C0re is a lightweight automation tool for Windows PC. It includes three main modules: BunnyHop (BHop), Auto Clicker, and Key Presser. Built with Python using tkinter and global keyboard hooks.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

✨ Features
🎮 BunnyHop (BHop): Auto-jump with 64-tick rate timing. Works while holding Space.

🖱️ Auto Clicker: Left-click automation with adjustable CPS. Includes click counter and compact overlay window.

⌨️ Key Presser: Auto-press any keyboard key with adjustable delay.

🎨 Modern UI: Dark theme with customizable accent color, background, and fonts.

💾 Config Persistence: Settings are automatically saved to F34kY_Core.json.

🔝 Always on Top: Small status windows stay above other applications.

🖥️ Interface Overview
Main window features three cards for each module, settings button, and exit button. When activated:

BHop: Separate overlay showing ENABLED/DISABLED status

Clicker/Presser: Compact dark windows showing current status and action counter

⌨️ Default Hotkeys
Action	Key
Toggle Main Menu	\ (Backslash)
BHop: Toggle	ALT (while holding Space)
BHop: Emergency Exit	END
Auto Clicker: Toggle	X (after module activation)
Key Presser: Toggle	E (after module activation)
Note: Clicker and Presser trigger keys can be changed in settings.

🛠️ Installation & Usage
Make sure you have Python 3.7+ installed.

Clone the repository or download F34kY_Core.py:

bash
git clone https://github.com/yourusername/F34kY_Core.git
cd F34kY_Core
Install required dependencies:

bash
pip install keyboard pyautogui
(tkinter comes bundled with Python by default)

Run the program:

bash
python F34kY_Core.py
⚙️ Settings
In the settings window, you can customize:

Accent Color: Pick any color using the color picker

Background & Card Colors: Custom RGB values

Font & Size: Any font installed on your system

Menu Key: Remap the main menu toggle key

Clicker/Presser Keys: Set custom trigger keys

📁 Configuration File
All settings are stored in F34kY_Core.json. You can manually edit this file or use the in-app settings menu.

⚠️ Disclaimer
This software is provided for educational purposes only to demonstrate global keyboard hooks and input automation techniques.

Using this software in online games may violate the game's Terms of Service and could result in account penalties. The author assumes no responsibility for any misuse or damages caused by this software.

📄 License
This project is for personal and educational use only.
