# Gauss for NetSuite

Small tool for managing your NetSuite app **account customization** using sdfcli (SuiteCloud Development Framework).

## Requirements

You need install:

- GIT 2.5 or newler [download here](https://git-scm.com/download/win)
- Java JRE 8.x or newler [download here](https://www.java.com/es/download/) 
- Python 3.x [download here](https://www.python.org/downloads/) 
- PIP *mark the checkbox in pyhthon installing*


> **important!**
> mark the checkbox on add Python to environment Path

[![Captura.jpg](https://i.postimg.cc/15Tswq91/Captura.jpg)](https://postimg.cc/56whMjYs)

> Click on disabled path length limit

[![Captura1.jpg](https://i.postimg.cc/WpkQCHVC/Captura1.jpg)](https://postimg.cc/V5zGb4dW)

---

## Clone gauss repository

Open a new windows console (cmd) and type:

> ```git clone https://github.com/raloz/gauss.git c:\Users\%username%\AppData\local\gauss```

then run 

> ```python -m pip install --upgrade pip```

for upgrading yor pip version.

---

## Installing PIP modules

Gauss needs a few modules for working, install this modules from PIP, type in your cmd:

> ```pip install colored```

> ```pip install PyInquirer```

## Add gauss path to environment

- This PC *right click into properties* 
- Click on system advanced settings
- Go to the adevance settings tab
- Click on envoronment variables 
- Select Path variable and click on edit button to add gauss path
- Add a new path c:\Users\%username%\AppData\local\gauss

Finally Restart your PC

---

# Notes

You can create this scripts/record types:

- Client Script
- Map/reduce Script
- Restlet
- Suitelet
- Userevent Script

Type:

Open a new cmd terminal and type:

> gauss.py --help

[![Captura.jpg](https://i.postimg.cc/vB9XCVb1/Captura.jpg)](https://postimg.cc/62WdvT7w)

*optional*

You can create keybindings in your **vscode**, justo go to:

- File
- Preferences
- Keyboard shortcuts
- Open Keyboard Shortcuts JSON
- Paste: 

```
// Place your key bindings in this file to override the defaults
[
    {
        "key": "shift+alt+u",
        "command": "workbench.action.terminal.sendSequence",
        "args": {
          "text": "gauss.py --upload ${relativeFile}\n"
        }
    },
    {
        "key": "ctrl+shift+alt+u",
        "command": "workbench.action.terminal.sendSequence",
        "args": {
          "text": "gauss.py --deploy\n"
        }
    }
]
```