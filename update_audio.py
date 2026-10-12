import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. CSS الخاص بالزر واللوحة المنبثقة للصوت
audio_css = """
<style>
/* زر الصوت في شريط التحريك */
.audio-btn {
  background: linear-gradient(135deg, #ec4899, #8b5cf6) !important;
  color: white !important;
  font-weight: bold;
  border-radius: 9999px !important;
  box-shadow: 0 4px 14px rgba(236, 72, 153, 0.4);
  transition: all 0.2s ease;
}
.audio-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(236, 72, 153, 0.6);
}
/* نافذة استوديو الصوت */
#audioStudioModal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(8px);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  padding: 16px;
}
.audio-box {
  background: #18181b;
  border: 1px solid #3f3f46;
  border-radius: 20px;
  max-width: 440px;
  width: 100%;
  padding: 24px;
  color: #fff;
  direction: rtl;
  box-shadow: 0 20px 40px rgba(0,0,0,0.7);
}
.sfx-btn {
  background: #27272a;
  border: 1px solid #3f3f46;
  color: #e4e4e7;
  padding: 10px;
  border-radius: 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.sfx-btn:active {
  transform: scale(0.95);
  background: #3b82f6;
  color: white;
}
</style>
"""

# 2. واجهة نافذة الصوت
audio_modal_html = """
<!-- استوديو صوت ودبلجة باسم ورندا -->
<div id="audioStudioModal">
  <div class="audio-box">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
      <h3 style="margin:0; font-size:18px; display:flex; align-items:center; gap:8px;">
        🎙️ <span>استوديو دبلجة باسم ورندا</span>
      </h3>
      <button onclick="closeAudioModal()" style="background:none; border:none; color:#a1a1aa; font-size:22px; cursor:pointer;">✕</button>
    </div>

    <!-- قسم تسجيل الصوت المباشر -->
    <div style="background:#27272a; border-radius:14px; padding:16px; margin-bottom:16px; text-align:center;">
      <div id="recordStatus" style="font-size:14px; margin-bottom:12px; color:#a1a1aa;">جاهز لتسجيل أصوات الشخصيات!</div>
      <div style="display:flex; justify-content:center; gap:10px;">
        <button id="startRecBtn" onclick="toggleVoiceRecord()" style="background:#ef4444; color:white; border:none; padding:10px 20px; border-radius:12px; font-weight:bold; cursor:pointer; display:flex; align-items:center; gap:6px;">
          <span>🔴</span> <span id="recBtnText">بدء التسجيل</span>
        </button>
        <button id="playRecBtn" onclick="playRecordedAudio()" style="background:#3b82f6; color:white; border:none; padding:10px 16px; border-radius:12px; font-weight:bold; cursor:pointer; display:none;">
          ▶️ تشغيل الصوت
        </button>
        <button id="delRecBtn" onclick="deleteRecordedAudio()" style="background:#71717a; color:white; border:none; padding:10px 12px; border-radius:12px; cursor:pointer; display:none;" title="حذف">
          🗑️
        </button>
      </div>
    </div>

    <!-- مؤثرات صوتية كرتونية فورية -->
    <div style="margin-bottom:20px;">
      <div style="font-size:13px; color:#d4d4d8; margin-bottom:8px; font-weight:600;">⚡ مؤثرات كرتونية سريعة:</div>
      <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:8px;">
        <button class="sfx-btn" onclick="playSFX('boing')">🦘 قفزة بطل (Boing)</button>
        <button class="sfx-btn" onclick="playSFX('laser')">⚡ ليزر خارق</button>
        <button class="sfx-btn" onclick="playSFX('punch')">💥 ضربة نينجا</button>
        <button class="sfx-btn" onclick="playSFX('cheer')">🎉 نغمة الفوز</button>
      </div>
    </div>

    <!-- خيارات التصدير مع الصوت -->
    <div style="display:flex; flex-direction:column; gap:8px;">
      <button onclick="exportVideoWithAudio()" style="background:linear-gradient(135deg, #10b981, #059669); color:white; border:none; padding:12px; border-radius:12px; font-weight:bold; cursor:pointer; font-size:14px;">
        🎬 تصدير فيديو ناطق مع الصوت (للواتساب)
      </button>
      <button onclick="closeAudioModal()" style="background:#3f3f46; color:#fff; border:none; padding:10px; border-radius:12px; font-size:13px; cursor:pointer;">
        تم ورجوع للرسم
      </button>
    </div>
  </div>
</div>
"""

# 3. محرك الجافاسكريبت للصوت والمزامنة
audio_js = """
<script>
// محرك الصوت المطور لباسم ورندا
let audioContext = null;
let mediaRecorder = null;
let audioChunks = [];
let recordedAudioBlob = null;
let recordedAudioElement = new Audio();
let isRecordingVoice = false;

function getAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }
  return audioContext;
}

// فتح وإغلاق النافذة
function openAudioModal() {
  document.getElementById('audioStudioModal').style.display = 'flex';
  getAudioContext();
}
function closeAudioModal() {
  document.getElementById('audioStudioModal').style.display = 'none';
}

// 1. مؤثرات كرتونية مولدة بالترددات بدون إنترنت
function playSFX(type) {
  const ctx = getAudioContext();
  const now = ctx.currentTime;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain);
  gain.connect(ctx.destination);

  if (type === 'boing') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, now);
    osc.frequency.exponentialRampToValueAtTime(600, now + 0.15);
    osc.frequency.exponentialRampToValueAtTime(200, now + 0.35);
    gain.gain.setValueAtTime(0.5, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
    osc.start(now);
    osc.stop(now + 0.35);
  } else if (type === 'laser') {
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(900, now);
    osc.frequency.exponentialRampToValueAtTime(80, now + 0.2);
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
    osc.start(now);
    osc.stop(now + 0.2);
  } else if (type === 'punch') {
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(250, now);
    osc.frequency.exponentialRampToValueAtTime(40, now + 0.18);
    gain.gain.setValueAtTime(0.6, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
    osc.start(now);
    osc.stop(now + 0.18);
  } else if (type === 'cheer') {
    const notes = [261.63, 329.63, 392.00, 523.25];
    notes.forEach((freq, idx) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.connect(g);
      g.connect(ctx.destination);
      o.type = 'sine';
      o.frequency.setValueAtTime(freq, now + idx * 0.08);
      g.gain.setValueAtTime(0.3, now + idx * 0.08);
      g.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.2);
      o.start(now + idx * 0.08);
      o.stop(now + idx * 0.08 + 0.2);
    });
  }
}

// 2. تسجيل صوت باسم ورندا
async function toggleVoiceRecord() {
  const statusEl = document.getElementById('recordStatus');
  const btnText = document.getElementById('recBtnText');
  const startBtn = document.getElementById('startRecBtn');

  if (!isRecordingVoice) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = () => {
        recordedAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        recordedAudioElement.src = URL.createObjectURL(recordedAudioBlob);
        document.getElementById('playRecBtn').style.display = 'inline-flex';
        document.getElementById('delRecBtn').style.display = 'inline-flex';
        statusEl.innerHTML = "✅ تم حفظ الصوت بنجاح! سيتم تشغيله مع الأنميشن.";
      };
      mediaRecorder.start();
      isRecordingVoice = true;
      btnText.innerText = "إيقاف التسجيل ⏹️";
      startBtn.style.background = "#f59e0b";
      statusEl.innerHTML = "🔴 جارٍ التسجيل... تكلم يا بطل!";
    } catch (err) {
      alert("يرجى إعطاء الإذن للمتصفح لاستخدام الميكروفون.");
    }
  } else {
    mediaRecorder.stop();
    isRecordingVoice = false;
    btnText.innerText = "تسجيل جديد 🔴";
    startBtn.style.background = "#ef4444";
  }
}

function playRecordedAudio() {
  if (recordedAudioElement.src) {
    recordedAudioElement.currentTime = 0;
    recordedAudioElement.play();
  }
}

function deleteRecordedAudio() {
  recordedAudioBlob = null;
  recordedAudioElement.src = "";
  document.getElementById('playRecBtn').style.display = 'none';
  document.getElementById('delRecBtn').style.display = 'none';
  document.getElementById('recordStatus').innerText = "تم حذف الصوت، يمكنك التسجيل من جديد.";
}

// ربط تشغيل الصوت تلقائياً مع زر تشغيل الأنميشن
document.addEventListener("DOMContentLoaded", () => {
  const checkPlay = setInterval(() => {
    const playBtn = document.getElementById('playBtn') || document.querySelector('[onclick*="play"]');
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        if (recordedAudioBlob && recordedAudioElement.src) {
          recordedAudioElement.currentTime = 0;
          recordedAudioElement.play().catch(()=>{});
        }
      });
      clearInterval(checkPlay);
    }
  }, 500);
});

// 3. تصدير فيديو ناطق مع الصوت (Canvas + Audio to WebM)
async function exportVideoWithAudio() {
  const canvas = document.getElementById('drawingCanvas') || document.querySelector('canvas');
  if (!canvas) {
    alert("لم يتم العثور على لوحة الرسم!");
    return;
  }
  alert("جارٍ تجهيز الفيديو الناطق... انتظر ثوانٍ قليلة.");
  
  const stream = canvas.captureStream(12);
  if (recordedAudioBlob) {
    const audioCtx = getAudioContext();
    const response = await fetch(URL.createObjectURL(recordedAudioBlob));
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
    const dest = audioCtx.createMediaStreamDestination();
    const source = audioCtx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(dest);
    source.start();
    stream.addTrack(dest.stream.getAudioTracks()[0]);
  }

  const rec = new MediaRecorder(stream, { mimeType: 'video/webm' });
  const chunks = [];
  rec.ondataavailable = e => chunks.push(e.data);
  rec.onstop = () => {
    const blob = new Blob(chunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `باسم_أنميشن_${Date.now()}.webm`;
    a.click();
    closeAudioModal();
  };

  rec.start();
  // تسجيل مدة 4 ثواني للمشهد
  setTimeout(() => rec.stop(), 4000);
}
</script>
"""

# زر الصوت ليتم وضعه جنب زر التشغيل في التايم لاين
audio_trigger_btn = """<button id="openAudioBtn" onclick="openAudioModal()" class="audio-btn" style="padding: 6px 14px; border:none; cursor:pointer; font-size:13px; display:inline-flex; align-items:center; gap:6px;">🎙️ دبلجة وأصوات</button>"""

# حقن الكود بالملف
if "audioStudioModal" not in html:
    # إضافة الزر بجانب زر Play أو في شريط التحكم
    if 'id="playBtn"' in html:
        html = html.replace('id="playBtn"', 'id="playBtn"')
        html = re.sub(r'(<button[^>]*id=["\']playBtn["\'][^>]*>.*?</button>)', r'\1\n' + audio_trigger_btn, html)
    else:
        # إضافة الزر قبل شريط الفريمات أو أسفل الشاشة
        html = html.replace('</body>', f'<div style="position:fixed; bottom:12px; left:12px; z-index:999;">{audio_trigger_btn}</div>\n</body>')

    # إضافة CSS والنافذة والسكريبت قبل </body>
    injection = f"\n{audio_css}\n{audio_modal_html}\n{audio_js}\n</body>"
    html = html.replace('</body>', injection)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[+] تم تحديث index.html وإضافة استوديو الدبلجة بنجاح!")
else:
    print("[!] ميزة الصوت موجودة مسبقاً في index.html")
