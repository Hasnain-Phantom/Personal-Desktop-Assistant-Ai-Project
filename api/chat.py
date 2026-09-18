"""
Vercel serverless function: POST /api/chat  {"query": "..."}  ->  {"reply": "...", "url": "..."}

Web-safe subset of the assistant commands (no desktop access on a server).
Uses only the standard library so Vercel needs no extra packages.
"""

import datetime
import json
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler


def greeting(now):
    h = now.hour
    if h < 12:
        return "Good Morning!"
    if h < 17:
        return "Good Afternoon!"
    if h < 20:
        return "Good Evening!"
    return "Good Night!"


def wikipedia_summary(topic):
    topic = topic.strip()
    if not topic:
        return "What should I search Wikipedia for?"
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + urllib.parse.quote(topic.replace(" ", "_")))
    req = urllib.request.Request(url, headers={"User-Agent": "JarvisAssistant/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.load(r)
    except Exception:
        return f"Sorry, I couldn't find anything on Wikipedia for '{topic}'."
    extract = data.get("extract")
    if not extract:
        return f"Sorry, I couldn't find anything on Wikipedia for '{topic}'."
    sentences = extract.split(". ")
    return "According to Wikipedia: " + ". ".join(sentences[:2]).rstrip(".") + "."


def handle(query, tz_offset_min=0):
    """tz_offset_min is the browser's UTC offset in minutes (east positive)."""
    q = (query or "").lower().strip()
    tz = datetime.timezone(datetime.timedelta(minutes=tz_offset_min))
    now = datetime.datetime.now(tz)
    if not q:
        return {"reply": "Say something and I'll do my best."}

    if "search wikipedia for" in q:
        return {"reply": wikipedia_summary(q.replace("search wikipedia for", ""))}
    if "wikipedia" in q:
        return {"reply": wikipedia_summary(
            q.replace("search wikipedia", "").replace("wikipedia", "").replace("jarvis", ""))}

    if "open youtube" in q:
        return {"reply": "Opening YouTube.", "url": "https://www.youtube.com"}
    if "open google" in q:
        return {"reply": "Opening Google.", "url": "https://www.google.com"}

    if "youtube" in q:
        term = q.replace("search on youtube", "").replace("youtube search", "") \
                .replace("youtube", "").replace("jarvis", "").strip()
        return {"reply": f"Searching YouTube for '{term}'.",
                "url": "https://www.youtube.com/results?search_query=" + urllib.parse.quote(term)}
    if "google" in q:
        term = q.replace("search on google", "").replace("google search", "") \
                .replace("google", "").replace("jarvis", "").strip()
        return {"reply": f"This is what I found on Google for '{term}'.",
                "url": "https://www.google.com/search?q=" + urllib.parse.quote(term)}

    if "the time" in q:
        return {"reply": "Sir, the time is " + now.strftime("%H:%M")}
    if "the date" in q or "today" in q:
        return {"reply": "Today is " + now.strftime("%A, %d %B %Y")}

    if "tired" in q:
        return {"reply": "Playing your favourite songs, sir.",
                "url": "https://www.youtube.com/watch?v=U935BSVJIM0"}

    if "hello" in q or "hi jarvis" in q:
        return {"reply": greeting(now) + " Hello sir, how are you?"}
    if "i am fine" in q:
        return {"reply": "That's great, sir."}
    if "how are you" in q:
        return {"reply": "Perfect, sir."}
    if "thank you" in q:
        return {"reply": "You are welcome, sir."}
    if "who are you" in q or "your name" in q:
        return {"reply": "I am Jarvis, your personal desktop assistant, now on the web."}

    return {"reply": "Sorry, I don't know that command yet. Type 'help' to see what I can do."}


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"reply": "Bad request."})
        try:
            offset = int(data.get("tz", 0))
        except (TypeError, ValueError):
            offset = 0
        self._send(200, handle(data.get("query", ""), offset))

    def do_GET(self):
        self._send(200, {"reply": "Jarvis API is running. POST {\"query\": \"...\"}."})
