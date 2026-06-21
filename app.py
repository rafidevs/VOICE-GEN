from flask import Flask, render_template, request, jsonify, send_file, url_for, send_from_directory
import edge_tts
import os
import uuid
import asyncio
import time
import tempfile
from gtts import gTTS

app = Flask(__name__, static_folder='static')

AUDIO_DIR = os.path.join(tempfile.gettempdir(), 'voicegen_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

GENERATION_TIMEOUT = 60

VOICES = [
    {"id": "bn-BD-NabanitaNeural", "name": "Nabanita", "desc": "মিষ্টি ও স্বাভাবিক", "accent": "বাংলাদেশ নেটিভ", "emoji": "🌺", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "native"},
    {"id": "bn-IN-TanishaaNeural", "name": "Tanishaa", "desc": "উষ্ণ ও স্পষ্ট", "accent": "ভারত নেটিভ", "emoji": "🌹", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "native"},
    {"id": "bn-BD-NabanitaNeural", "name": "Meghna", "desc": "কিশোরী ও প্রাণবন্ত", "accent": "বাংলাদেশ", "emoji": "🌸", "rate": "+10%", "pitch": "+8Hz", "engine": "edge", "tier": "native"},
    {"id": "bn-IN-TanishaaNeural", "name": "Rimi", "desc": "তীক্ষ্ণ ও দুরন্ত", "accent": "ভারত", "emoji": "🌼", "rate": "+15%", "pitch": "+10Hz", "engine": "edge", "tier": "native"},
    {"id": "bn-BD-NabanitaNeural", "name": "Shila", "desc": "শান্ত ও মোলায়েম", "accent": "বাংলাদেশ", "emoji": "🌷", "rate": "-15%", "pitch": "-4Hz", "engine": "edge", "tier": "native"},
    {"id": "bn-IN-TanishaaNeural", "name": "Dipa", "desc": "গম্ভীর ও আভিজাত", "accent": "ভারত", "emoji": "💐", "rate": "-10%", "pitch": "-2Hz", "engine": "edge", "tier": "native"},
    {"id": "en-US-AvaMultilingualNeural", "name": "Ava", "desc": "প্রাণবন্ত মেয়ে", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "✨", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "multi"},
    {"id": "en-US-AvaMultilingualNeural", "name": "Ada", "desc": "কিশোরী তীক্ষ্ণ", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "💎", "rate": "+12%", "pitch": "+8Hz", "engine": "edge", "tier": "multi"},
    {"id": "en-US-AvaMultilingualNeural", "name": "Amanda", "desc": "ধীর ও গম্ভীর", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🌙", "rate": "-12%", "pitch": "-3Hz", "engine": "edge", "tier": "multi"},
    {"id": "en-US-EmmaMultilingualNeural", "name": "Emma", "desc": "মৃদু ও স্নিগ্ধ", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "💫", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "multi"},
    {"id": "en-US-EmmaMultilingualNeural", "name": "Arabella", "desc": "উঁচু কণ্ঠ মিষ্টি", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🦋", "rate": "+5%", "pitch": "+6Hz", "engine": "edge", "tier": "multi"},
    {"id": "en-US-EmmaMultilingualNeural", "name": "Cora", "desc": "শান্ত ও গভীর", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🌊", "rate": "-10%", "pitch": "-2Hz", "engine": "edge", "tier": "multi"},
    {"id": "fr-FR-VivienneMultilingualNeural", "name": "Vivienne", "desc": "মার্জিত ও সুন্দর", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🎀", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "multi"},
    {"id": "fr-FR-VivienneMultilingualNeural", "name": "Evelyn", "desc": "প্রাণবন্ত ও মধুর", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🌸", "rate": "+8%", "pitch": "+4Hz", "engine": "edge", "tier": "multi"},
    {"id": "fr-FR-VivienneMultilingualNeural", "name": "Isabella", "desc": "কোমল ও মৃদু", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🌺", "rate": "-8%", "pitch": "-1Hz", "engine": "edge", "tier": "multi"},
    {"id": "de-DE-SeraphinaMultilingualNeural", "name": "Seraphina", "desc": "অভিজাত ও শক্তিশালী", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🔥", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "multi"},
    {"id": "de-DE-SeraphinaMultilingualNeural", "name": "Isidora", "desc": "উঁচু কণ্ঠ স্পষ্ট", "accent": "মাল্টিঙ্গুয়াল", "emoji": "⭐", "rate": "+8%", "pitch": "+5Hz", "engine": "edge", "tier": "multi"},
    {"id": "de-DE-SeraphinaMultilingualNeural", "name": "Serena", "desc": "গম্ভীর ও ধীরস্থির", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🕊️", "rate": "-10%", "pitch": "-3Hz", "engine": "edge", "tier": "multi"},
    {"id": "pt-BR-ThalitaMultilingualNeural", "name": "Thalita", "desc": "প্রাণবন্ত ও মধুর", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🌻", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "multi"},
    {"id": "pt-BR-ThalitaMultilingualNeural", "name": "Lola", "desc": "কিশোরী ও দুরন্ত", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🎀", "rate": "+12%", "pitch": "+8Hz", "engine": "edge", "tier": "multi"},
    {"id": "pt-BR-ThalitaMultilingualNeural", "name": "Nancy", "desc": "শান্ত ও বিশ্বস্ত", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🌿", "rate": "-8%", "pitch": "-2Hz", "engine": "edge", "tier": "multi"},
    {"id": "pt-BR-ThalitaMultilingualNeural", "name": "Phoebe", "desc": "মিষ্টি ও ধীর", "accent": "মাল্টিলিঙ্গুয়াল", "emoji": "🍀", "rate": "-15%", "pitch": "+2Hz", "engine": "edge", "tier": "multi"},
    {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao", "desc": "কোমল ও সুন্দর", "accent": "এশিয়ান", "emoji": "🌸", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "asia"},
    {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaochen", "desc": "তীক্ষ্ণ ও দুরন্ত", "accent": "এশিয়ান", "emoji": "🌺", "rate": "+10%", "pitch": "+6Hz", "engine": "edge", "tier": "asia"},
    {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoyu", "desc": "গভীর ও মৃদু", "accent": "এশিয়ান", "emoji": "🌹", "rate": "-10%", "pitch": "-2Hz", "engine": "edge", "tier": "asia"},
    {"id": "es-ES-XimenaNeural", "name": "Ximena", "desc": "স্পষ্ট ও মার্জিত", "accent": "এশিয়ান", "emoji": "🌷", "rate": "+0%", "pitch": "+0Hz", "engine": "edge", "tier": "asia"},
    {"id": "bn", "name": "Google-BD", "desc": "Google বাংলা স্বাভাবিক", "accent": "Google TTS BD", "emoji": "🔴", "rate": "+0%", "pitch": "+0Hz", "engine": "gtts", "gtts_lang": "bn", "gtts_slow": False, "tier": "google"},
    {"id": "bn", "name": "Google-Slow", "desc": "Google বাংলা ধীর কণ্ঠ", "accent": "Google TTS BD", "emoji": "🔵", "rate": "-20%", "pitch": "+0Hz", "engine": "gtts", "gtts_lang": "bn", "gtts_slow": True, "tier": "google"},
]


def cleanup_old_files():
    now = time.time()
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR, exist_ok=True)
        return
    for f in os.listdir(AUDIO_DIR):
        path = os.path.join(AUDIO_DIR, f)
        if os.path.isfile(path) and now - os.path.getmtime(path) > 3600:
            try:
                os.remove(path)
            except:
                pass


async def generate_edge(text, voice_id, rate, pitch):
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
    await asyncio.wait_for(communicate.save(filepath), timeout=GENERATION_TIMEOUT)
    return filename


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def generate_gtts(text, lang, slow):
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(filepath)
    return filename


@app.route('/')
def index():
    return render_template('index.html', voices=VOICES)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    text = data.get('text', '').strip()
    voice_name = data.get('voice_name', 'Nabanita')
    custom_speed = data.get('speed', 0)

    if not text:
        return jsonify({"error": "Please enter some text"}), 400

    if len(text) > 25000:
        return jsonify({"error": "Text is too long (max 25000 characters)"}), 400

    cleanup_old_files()

    voice_info = next((v for v in VOICES if v["name"] == voice_name), VOICES[0])

    try:
        if voice_info["engine"] == "gtts":
            filename = generate_gtts(text, voice_info["gtts_lang"], voice_info["gtts_slow"])
        else:
            rate = voice_info.get("rate", "+0%")
            pitch = voice_info.get("pitch", "+0Hz")
            if custom_speed != 0:
                base_rate = int(rate.replace('%', '').replace('+', '')) if rate != "+0%" else 0
                new_rate = base_rate + custom_speed
                rate = f"{'+' if new_rate >= 0 else ''}{new_rate}%"
            filename = run_async(generate_edge(text, voice_info["id"], rate, pitch))

        return jsonify({
            "success": True,
            "filename": filename,
            "url": f"/audio/{filename}",
            "voice_name": voice_info["name"],
            "text_length": len(text)
        })
    except asyncio.TimeoutError:
        return jsonify({"error": "Voice generation timed out. Try shorter text or a different voice."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=f"voice_{filename}")
    return jsonify({"error": "File not found"}), 404


@app.route('/voices')
def get_voices():
    return jsonify(VOICES)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
