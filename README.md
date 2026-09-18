# Personal-Desktop-Assistant-Ai-Project
 An intelligent desktop assistant built using Python to help you manage tasks, search information, and automate routine processes seamlessly. Designed to enhance productivity with voice commands, natural language processing, and smart integration features.

## Running the desktop UI

The assistant now has a modern graphical interface (`app.py`) built with
[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), alongside the
original terminal version (`Personal Desktop Assistant.py`).

```bash
pip install -r requirements.txt
python app.py
```

- **Type** a command in the box (e.g. `the time`, `open notepad`,
  `search wikipedia for python`) or click a **Quick Action** in the sidebar.
- Click the **🎤** button to give a voice command.
- Type `help` to list every supported command.
- Toggle **Voice replies** and **Dark mode** from the sidebar.

Only `customtkinter` is required for the window itself; other packages are
loaded on demand, and the assistant tells you which one to install if a
feature needs it.

### Project layout

| File | Purpose |
| --- | --- |
| `app.py` | Graphical UI (chat window, quick actions, mic button) |
| `assistant_core.py` | All command logic, shared by the UI and terminal version |
| `Personal Desktop Assistant.py` | Original terminal-only assistant |
| `Dictapp.py`, `SearchNow.py`, `Translator.py`, `alarm.py`, `FocusMode.py`, `FocusGraph.py`, `keyboard.py` | Feature helpers |
