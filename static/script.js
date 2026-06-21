class VoiceGenApp {
    constructor() {
        this.selectedVoiceName = 'Nabanita';
        this.audioElement = null;
        this.currentFile = null;
        this.isPlaying = false;
        this.animationId = null;
        this.waveData = [];
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupVoicePills();
        this.setupVoiceDetail();
        this.setupSpeedSlider();
        this.setupFileUpload();
        this.setupTextarea();
        this.setupGenerate();
        this.setupPlayer();
        this.initWaveCanvas();
    }

    setupTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                const tab = btn.dataset.tab;
                document.querySelector(`.${tab}-tab`).classList.add('active');
            });
        });
    }

    setupVoicePills() {
        const firstNative = document.querySelector('.voice-pill-native');
        if (firstNative) firstNative.classList.add('selected');

        document.querySelectorAll('.voice-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                document.querySelectorAll('.voice-pill').forEach(p => p.classList.remove('selected'));
                pill.classList.add('selected');
                this.selectedVoiceName = pill.dataset.voiceName;
                this.showVoiceDetail(pill);
            });
        });
    }

    showVoiceDetail(pill) {
        const detail = document.getElementById('voiceDetail');
        detail.style.display = 'flex';
        document.getElementById('detailEmoji').textContent = pill.textContent.trim().split(' ')[0];
        document.getElementById('detailName').textContent = pill.dataset.voiceName;
        document.getElementById('detailDesc').textContent = pill.dataset.desc;
        document.getElementById('detailAccent').textContent = pill.dataset.accent;
    }

    setupVoiceDetail() {
        document.getElementById('detailClose').addEventListener('click', () => {
            document.getElementById('voiceDetail').style.display = 'none';
        });
    }

    setupSpeedSlider() {
        const slider = document.getElementById('speedSlider');
        const display = document.getElementById('speedValue');
        slider.addEventListener('input', () => {
            const v = parseInt(slider.value);
            if (v === 0) display.textContent = 'স্বাভাবিক';
            else if (v > 0) display.textContent = `+${v}% দ্রুত`;
            else display.textContent = `${v}% ধীর`;
        });
    }

    setupFileUpload() {
        const zone = document.getElementById('fileZone');
        const input = document.getElementById('fileInput');
        const info = document.getElementById('fileInfo');
        const removeBtn = document.getElementById('removeFile');

        zone.addEventListener('click', () => input.click());
        zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
        zone.addEventListener('drop', e => { e.preventDefault(); zone.classList.remove('dragover'); if (e.dataTransfer.files[0]) this.handleFile(e.dataTransfer.files[0]); });
        input.addEventListener('change', () => { if (input.files[0]) this.handleFile(input.files[0]); });
        removeBtn.addEventListener('click', () => { this.currentFile = null; input.value = ''; zone.style.display = ''; info.style.display = 'none'; });
    }

    handleFile(file) {
        if (!file.name.match(/\.(txt|md)$/i)) { this.showToast('.txt/.md ফাইল সমর্থন', 'error'); return; }
        this.currentFile = file;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileZone').style.display = 'none';
        document.getElementById('fileInfo').style.display = 'flex';
        const reader = new FileReader();
        reader.onload = e => { document.getElementById('textInput').value = e.target.result; this.updateCharCount(); };
        reader.readAsText(file);
    }

    setupTextarea() {
        document.getElementById('textInput').addEventListener('input', () => this.updateCharCount());
    }

    updateCharCount() {
        const text = document.getElementById('textInput').value;
        const count = text.length;
        const el = document.getElementById('charCount');
        el.textContent = count;
        const container = el.parentElement;
        container.classList.remove('warning', 'error');
        if (count > 20000) container.classList.add('warning');
        if (count > 25000) container.classList.add('error');
    }

    setupGenerate() {
        document.getElementById('generateBtn').addEventListener('click', () => this.generate());
    }

    async generate() {
        const text = document.getElementById('textInput').value.trim();
        if (!text) { this.showToast('টেক্সট লিখুন', 'error'); return; }

        const speed = parseInt(document.getElementById('speedSlider').value);
        const btn = document.getElementById('generateBtn');
        btn.disabled = true;
        btn.querySelector('.btn-content').style.display = 'none';
        btn.querySelector('.btn-loading').style.display = 'flex';

        try {
            const res = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, voice_name: this.selectedVoiceName, speed })
            });
            const data = await res.json();
            if (data.error) { this.showToast(data.error, 'error'); return; }
            this.showResult(data);
            this.showToast('ভয়েস তৈরি হয়েছে!', 'success');
        } catch (err) {
            this.showToast('সার্ভার সংযোগ ত্রুটি', 'error');
        } finally {
            btn.disabled = false;
            btn.querySelector('.btn-content').style.display = 'flex';
            btn.querySelector('.btn-loading').style.display = 'none';
        }
    }

    showResult(data) {
        const section = document.getElementById('resultSection');
        section.style.display = '';
        document.getElementById('resultVoiceName').textContent = data.voice_name;
        document.getElementById('resultChars').textContent = data.text_length;
        if (this.audioElement) { this.audioElement.pause(); this.isPlaying = false; }
        this.audioElement = new Audio(data.url);
        this.audioElement.volume = document.getElementById('volumeSlider').value / 100;
        this.audioElement.addEventListener('loadedmetadata', () => { document.getElementById('totalTime').textContent = this.formatTime(this.audioElement.duration); });
        this.audioElement.addEventListener('timeupdate', () => this.updateProgress());
        this.audioElement.addEventListener('ended', () => this.onAudioEnd());
        this.currentFilename = data.filename;
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressHandle').style.left = '0%';
        document.getElementById('currentTime').textContent = '0:00';
        document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
        document.getElementById('downloadBtn').onclick = () => { const a = document.createElement('a'); a.href = `/download/${this.currentFilename}`; a.download = `voice_${this.currentFilename}`; a.click(); };
        document.getElementById('regenerateBtn').onclick = () => this.generate();
        this.generateWaveData();
        this.drawWaveform(0);
    }

    setupPlayer() {
        document.getElementById('playBtn').addEventListener('click', () => this.togglePlay());
        document.getElementById('progressBar').addEventListener('click', e => {
            if (!this.audioElement) return;
            const rect = document.getElementById('progressBar').getBoundingClientRect();
            this.audioElement.currentTime = (e.clientX - rect.left) / rect.width * this.audioElement.duration;
        });
        document.getElementById('volumeSlider').addEventListener('input', () => {
            if (this.audioElement) this.audioElement.volume = document.getElementById('volumeSlider').value / 100;
            this.updateVolumeIcon();
        });
        document.getElementById('volumeBtn').addEventListener('click', () => {
            const vs = document.getElementById('volumeSlider');
            vs.value = vs.value > 0 ? 0 : 80;
            vs.dispatchEvent(new Event('input'));
        });
    }

    togglePlay() {
        if (!this.audioElement) return;
        if (this.isPlaying) {
            this.audioElement.pause(); this.isPlaying = false;
            document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
            if (this.animationId) cancelAnimationFrame(this.animationId);
        } else {
            this.audioElement.play(); this.isPlaying = true;
            document.getElementById('playBtn').innerHTML = '<i class="fas fa-pause"></i>';
            this.animateWaveform();
        }
    }

    updateProgress() {
        if (!this.audioElement) return;
        const pct = this.audioElement.currentTime / this.audioElement.duration * 100;
        document.getElementById('progressFill').style.width = pct + '%';
        document.getElementById('progressHandle').style.left = pct + '%';
        document.getElementById('currentTime').textContent = this.formatTime(this.audioElement.currentTime);
    }

    onAudioEnd() {
        this.isPlaying = false;
        document.getElementById('playBtn').innerHTML = '<i class="fas fa-play"></i>';
        if (this.animationId) cancelAnimationFrame(this.animationId);
        this.drawWaveform(0);
    }

    formatTime(sec) {
        if (!sec || isNaN(sec)) return '0:00';
        return `${Math.floor(sec / 60)}:${Math.floor(sec % 60).toString().padStart(2, '0')}`;
    }

    updateVolumeIcon() {
        const v = document.getElementById('volumeSlider').value;
        const icon = v === 0 ? 'fa-volume-xmark' : v < 50 ? 'fa-volume-low' : 'fa-volume-high';
        document.getElementById('volumeBtn').innerHTML = `<i class="fas ${icon}"></i>`;
    }

    initWaveCanvas() {
        const canvas = document.getElementById('waveCanvas');
        if (!canvas) return;
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width * 2; canvas.height = rect.height * 2;
        this.canvasCtx = canvas.getContext('2d');
        this.canvasCtx.scale(2, 2);
    }

    generateWaveData() {
        this.waveData = [];
        for (let i = 0; i < 120; i++) {
            const base = 0.3 + Math.random() * 0.4;
            this.waveData.push(Math.max(0.1, base + Math.sin(i * 0.15) * 0.15));
        }
    }

    drawWaveform(progress) {
        const ctx = this.canvasCtx;
        const canvas = document.getElementById('waveCanvas');
        if (!ctx || !canvas) return;
        const w = canvas.width / 2, h = canvas.height / 2;
        ctx.clearRect(0, 0, w, h);
        const bars = this.waveData.length, barWidth = w / bars, playedBars = Math.floor(progress * bars);
        for (let i = 0; i < bars; i++) {
            const barH = this.waveData[i] * h * 0.7, x = i * barWidth, y = (h - barH) / 2;
            ctx.fillStyle = i < playedBars ? 'rgba(236,72,153,0.9)' : i === playedBars ? 'rgba(124,58,237,0.8)' : 'rgba(100,100,200,0.25)';
            ctx.beginPath(); ctx.roundRect(x + 1, y, barWidth - 2, barH, 2); ctx.fill();
        }
    }

    animateWaveform() {
        if (!this.isPlaying) return;
        if (this.audioElement) this.drawWaveform(this.audioElement.currentTime / this.audioElement.duration);
        this.animationId = requestAnimationFrame(() => this.animateWaveform());
    }

    showToast(msg, type = '') {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.className = 'toast show ' + type;
        setTimeout(() => toast.className = 'toast', 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => new VoiceGenApp());
window.addEventListener('resize', () => {
    const canvas = document.querySelector('#waveCanvas');
    if (canvas) { const rect = canvas.parentElement.getBoundingClientRect(); canvas.width = rect.width * 2; canvas.height = rect.height * 2; canvas.getContext('2d').scale(2, 2); }
});
