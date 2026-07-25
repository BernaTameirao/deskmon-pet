# Deskmon Pet

**Deskmon Pet** is a small **Python + PyQt5** desktop application that brings animated pets to your screen.  
They walk, jump and can even be dragged with your mouse — all in real time!

<img width="639" height="360" alt="0604" src="https://github.com/user-attachments/assets/5b91a43b-d99c-4b34-bbca-0c8c2dbb4fd3" />

---

## Features

- Multiple desktop pets with unique animations.
- Pets can freely walk around the desktop.
- Drag-and-drop interaction.
- Pet battles with randomized outcomes.
- Level progression through battles.
- Pets can evolve through level or items.
- Wild pets can randomly appear on the screen.
- Pets can be unlocked through capture.
- Save system to preserve unlocked pets.

---

## Technologies Used

- [Python 3.10+](https://www.python.org/)
- [PyQt5](https://pypi.org/project/PyQt5/)

---

## Project Structure

```
desktop-pet/
├── src/
│   ├── main.py
│   ├── PetManager.py
│   ├── ...
│   └── Pet.py
├── imgs/
├── requirements.txt
├── ...
└── README.md
```

> Each pet should have its images in the format:  
> `name_0.png`, `name_1.png`, `name_2.png`, etc.

---

## How to Run

### 1. Get the project

You can get the project in two ways:

#### Option A — Clone the repository

```bash
git clone https://github.com/BernaTameirao/deskmon-pet.git
```

#### Option B — Download ZIP
- Download the repository as a .zip file from GitHub
- Extract it
- Open the folder in your terminal

### 2. Enter the project directory

```bash
cd ./deskmon-pet
```

### 3. Install dependencies

```bash
pip install -r ./requirements.txt
```

### 4. Download the sprite images

```bash
python ./src/SpriteDownloader.py
```

### 5. Run the application

```bash
python ./src/main.py
```

Pets will appear on your desktop.  
They will move automatically, and you can drag them around or interact with them using the mouse.

---

## Requirements

- Python 3.12 or higher  
- Operating System: Windows
- Dependencies listed in `requirements.txt`

---
## Copyright (C) 2026 Bernardo Tameirão

This project is licensed under the GNU General Public License v3.
See LICENSE for details.
