"""
Modern desktop UI for the Personal Desktop Assistant.

Run with:  python app.py

Layout
    - Left sidebar: brand, status, quick-action buttons, voice/theme toggles
    - Main area: chat-style conversation with the assistant
    - Bottom bar: text entry, Send button and a microphone button

Commands are executed on a worker thread so the window never freezes;
all widget updates are marshalled back to the Tk main thread via `after`.
"""

import datetime
import queue
import threading

import customtkinter as ctk

from assistant_core import COMMANDS, Assistant, greeting

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
USER_BUBBLE = ("#DBEAFE", "#1E3A8A")
BOT_BUBBLE = ("#F1F5F9", "#1F2937")
SIDEBAR = ("#F8FAFC", "#111827")
FONT = "Segoe UI"


# ------------------------------------------------------------------ speech
class Speaker:
    """Background text-to-speech queue. Falls back to silent mode when
    pyttsx3 isn't installed so the UI still works."""

    def __init__(self):
        self.enabled = True
        self._q = queue.Queue()
        self._engine = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init("sapi5")
            voices = self._engine.getProperty("voices")
            self._engine.setProperty("voice", voices[0].id)
        except Exception:
            self._engine = None
        threading.Thread(target=self._loop, daemon=True).start()

    @property
    def available(self):
        return self._engine is not None

    def speak(self, text):
        if self.enabled and self._engine:
            self._q.put(text)

    def _loop(self):
        while True:
            text = self._q.get()
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass


def recognise_speech(on_status):
    """Blocking: listen on the microphone once and return lower-cased text
    or 'None'. Runs on a worker thread."""
    try:
        import speech_recognition as sr
    except ImportError:
        on_status("speech_recognition not installed")
        return "None"
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            on_status("Listening...")
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
        on_status("Recognizing...")
        return r.recognize_google(audio, language="en-in").lower()
    except Exception:
        on_status("Couldn't understand")
        return "None"


# --------------------------------------------------------------------- app
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jarvis - Personal Desktop Assistant")
        self.geometry("1080x700")
        self.minsize(860, 560)

        self.speaker = Speaker()
        self.assistant = Assistant(self)
        self._busy = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

        self._tick_clock()
        self.after(300, self._welcome)

    # ------------------------------------------------------------- sidebar
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SIDEBAR)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_rowconfigure(3, weight=1)

        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="ew")
        ctk.CTkLabel(brand, text="J", width=44, height=44, corner_radius=12,
                     fg_color=ACCENT, text_color="white",
                     font=(FONT, 22, "bold")).pack(side="left")
        text = ctk.CTkFrame(brand, fg_color="transparent")
        text.pack(side="left", padx=12)
        ctk.CTkLabel(text, text="JARVIS", font=(FONT, 18, "bold"),
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(text, text="Desktop Assistant", font=(FONT, 12),
                     text_color="gray", anchor="w").pack(anchor="w")

        status = ctk.CTkFrame(sb, fg_color="transparent")
        status.grid(row=1, column=0, padx=20, pady=(8, 4), sticky="ew")
        self.status_dot = ctk.CTkLabel(status, text="●", text_color="#22C55E",
                                       font=(FONT, 14), width=16)
        self.status_dot.pack(side="left")
        self.status_lbl = ctk.CTkLabel(status, text="Ready", font=(FONT, 12),
                                       text_color="gray", anchor="w")
        self.status_lbl.pack(side="left", padx=6)

        ctk.CTkLabel(sb, text="QUICK ACTIONS", font=(FONT, 11, "bold"),
                     text_color="gray", anchor="w").grid(
            row=2, column=0, padx=20, pady=(16, 4), sticky="w")

        actions = ctk.CTkScrollableFrame(sb, fg_color="transparent")
        actions.grid(row=3, column=0, padx=10, pady=0, sticky="nsew")
        actions.grid_columnconfigure((0, 1), weight=1)
        for i, (cmd, label, desc) in enumerate(COMMANDS):
            ctk.CTkButton(
                actions, text=label, height=34, corner_radius=8,
                font=(FONT, 12), fg_color=("#E2E8F0", "#1F2937"),
                hover_color=("#CBD5E1", "#374151"),
                text_color=("#0F172A", "#E5E7EB"),
                command=lambda c=cmd: self._quick(c),
            ).grid(row=i // 2, column=i % 2, padx=4, pady=4, sticky="ew")

        toggles = ctk.CTkFrame(sb, fg_color="transparent")
        toggles.grid(row=4, column=0, padx=20, pady=16, sticky="ew")
        self.voice_var = ctk.BooleanVar(value=self.speaker.available)
        sw = ctk.CTkSwitch(toggles, text="Voice replies", font=(FONT, 12),
                           variable=self.voice_var, command=self._toggle_voice,
                           progress_color=ACCENT)
        sw.pack(anchor="w", pady=(0, 8))
        if not self.speaker.available:
            sw.configure(state="disabled", text="Voice replies (install pyttsx3)")
        self.theme_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(toggles, text="Dark mode", font=(FONT, 12),
                      variable=self.theme_var, command=self._toggle_theme,
                      progress_color=ACCENT).pack(anchor="w")

    # ---------------------------------------------------------------- main
    def _build_main(self):
        main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(22, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.greet_lbl = ctk.CTkLabel(header, text=greeting(),
                                      font=(FONT, 24, "bold"), anchor="w")
        self.greet_lbl.grid(row=0, column=0, sticky="w")
        self.clock_lbl = ctk.CTkLabel(header, text="", font=(FONT, 14),
                                      text_color="gray")
        self.clock_lbl.grid(row=0, column=1, sticky="e")

        self.chat = ctk.CTkScrollableFrame(main, corner_radius=16,
                                           fg_color=("#FFFFFF", "#0B1220"))
        self.chat.grid(row=1, column=0, padx=28, pady=8, sticky="nsew")
        self.chat.grid_columnconfigure(0, weight=1)
        self._row = 0

        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.grid(row=2, column=0, padx=28, pady=(8, 22), sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            bar, height=46, corner_radius=12, font=(FONT, 14),
            placeholder_text="Type a command, e.g. 'the time' or 'open notepad'")
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", lambda e: self._send())
        self.send_btn = ctk.CTkButton(bar, text="Send", width=90, height=46,
                                      corner_radius=12, font=(FONT, 14, "bold"),
                                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                      command=self._send)
        self.send_btn.grid(row=0, column=1, padx=(10, 0))
        self.mic_btn = ctk.CTkButton(bar, text="🎤", width=56, height=46,
                                     corner_radius=12, font=(FONT, 18),
                                     fg_color=("#E2E8F0", "#1F2937"),
                                     hover_color=("#CBD5E1", "#374151"),
                                     text_color=("#0F172A", "#E5E7EB"),
                                     command=self._listen_click)
        self.mic_btn.grid(row=0, column=2, padx=(10, 0))
        self.entry.focus()

    # ------------------------------------------------------------- bubbles
    def _bubble(self, text, who):
        is_user = who == "user"
        wrap = ctk.CTkFrame(self.chat, fg_color="transparent")
        wrap.grid(row=self._row, column=0, sticky="e" if is_user else "w",
                  padx=12, pady=6)
        self._row += 1
        stamp = datetime.datetime.now().strftime("%H:%M")
        ctk.CTkLabel(wrap, text=("You" if is_user else "Jarvis") + "  ·  " + stamp,
                     font=(FONT, 10), text_color="gray").pack(
            anchor="e" if is_user else "w", padx=6)
        ctk.CTkLabel(
            wrap, text=text, justify="left", wraplength=520,
            font=(FONT, 13), corner_radius=14, padx=14, pady=10,
            fg_color=USER_BUBBLE if is_user else BOT_BUBBLE,
            text_color=("#0F172A", "#F9FAFB"),
        ).pack(anchor="e" if is_user else "w")
        self.after(50, lambda: self.chat._parent_canvas.yview_moveto(1.0))

    def _set_status(self, text, colour="#22C55E"):
        self.status_lbl.configure(text=text)
        self.status_dot.configure(text_color=colour)

    def _tick_clock(self):
        now = datetime.datetime.now()
        self.clock_lbl.configure(text=now.strftime("%A, %d %B  •  %H:%M:%S"))
        self.greet_lbl.configure(text=greeting())
        self.after(1000, self._tick_clock)

    def _welcome(self):
        self.say(greeting() + " Welcome back. I am your personal desktop "
                 "assistant. How may I help you?")

    # ------------------------------------------- Assistant UI interface
    # These are called from the worker thread, so they hop to the main
    # thread with `after`. `ask` blocks the worker until the dialog closes.
    def say(self, text):
        self.after(0, lambda: self._bubble(text, "bot"))
        self.speaker.speak(text)

    def status(self, text):
        self.after(0, lambda: self._set_status(text, "#F59E0B"))

    def ask(self, prompt):
        result = {}
        done = threading.Event()

        def show():
            dlg = ctk.CTkInputDialog(text=prompt, title="Jarvis needs input",
                                     button_fg_color=ACCENT,
                                     button_hover_color=ACCENT_HOVER)
            result["value"] = dlg.get_input()
            done.set()

        self.after(0, show)
        done.wait()
        value = result.get("value")
        if value:
            self.after(0, lambda: self._bubble(value, "user"))
        return value

    def listen(self):
        text = recognise_speech(self.status)
        if text != "None":
            self.after(0, lambda: self._bubble(text, "user"))
        return text

    # ------------------------------------------------------------ actions
    def _quick(self, cmd):
        self.entry.delete(0, "end")
        self.entry.insert(0, cmd)
        self._send()

    def _send(self):
        text = self.entry.get().strip()
        if not text or self._busy:
            return
        self.entry.delete(0, "end")
        self._bubble(text, "user")
        if text.lower() in ("help", "?"):
            self._bubble("Here's what I can do:\n" + "\n".join(
                f"•  {c}  —  {d}" for c, _, d in COMMANDS), "bot")
            return
        self._run_command(text)

    def _listen_click(self):
        if self._busy:
            return

        def job():
            text = recognise_speech(self.status)
            if text == "None":
                self.after(0, lambda: self._set_status("Ready"))
                self.after(0, lambda: self.mic_btn.configure(fg_color=("#E2E8F0", "#1F2937")))
                return
            self.after(0, lambda: self._bubble(text, "user"))
            self.after(0, lambda: self.mic_btn.configure(fg_color=("#E2E8F0", "#1F2937")))
            self._run_command(text)

        self.mic_btn.configure(fg_color=ACCENT)
        threading.Thread(target=job, daemon=True).start()

    def _run_command(self, text):
        self._busy = True
        self._set_status("Working...", "#F59E0B")
        self.send_btn.configure(state="disabled")

        def job():
            keep_going = True
            try:
                keep_going = self.assistant.handle(text)
            except Exception as e:  # noqa: BLE001
                self.say(f"Something went wrong: {e}")
            finally:
                self.after(0, self._done, keep_going)

        threading.Thread(target=job, daemon=True).start()

    def _done(self, keep_going):
        self._busy = False
        self.send_btn.configure(state="normal")
        self._set_status("Ready")
        if not keep_going:
            self.after(1500, self.destroy)

    def _toggle_voice(self):
        self.speaker.enabled = self.voice_var.get()

    def _toggle_theme(self):
        ctk.set_appearance_mode("dark" if self.theme_var.get() else "light")


if __name__ == "__main__":
    App().mainloop()
