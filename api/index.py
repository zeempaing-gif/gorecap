import os
import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="TTS Pro - Burmese Persona Voice Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="my">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TTS Pro - မြန်မာအသံစနစ်</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <style>body { font-family: 'Padauk', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-4 sm:p-6 flex flex-col items-center">
  <div class="max-w-4xl w-full space-y-4">
    <header class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 to-orange-600 flex items-center justify-center text-xl shadow-lg shadow-amber-500/20">🎙️</div>
        <div>
          <h1 class="text-lg sm:text-xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">TTS Pro (မြန်မာအသံစနစ်)</h1>
          <p class="text-xs text-slate-400">ကာရိုက်တာ (၁၀) မျိုးပါ အသံဖန်တီးခန်း • Vercel Cloud</p>
        </div>
      </div>
      <div class="text-xs px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1.5 font-bold">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>Online</span>
      </div>
    </header>

    <main class="grid grid-cols-1 lg:grid-cols-12 gap-4">
      <section class="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-bold text-amber-400">👥 မြန်မာအသံ ရွေးချယ်ရန်</h2>
          <span id="selectedBadge" class="text-xs text-amber-300 font-bold bg-amber-950 px-2 py-0.5 rounded-full border border-amber-800">ရွေးထားသည်: နေတိုး</span>
        </div>
        <div id="voiceCardsList" class="space-y-2 max-h-[420px] overflow-y-auto pr-1"></div>
      </section>

      <section class="lg:col-span-6 space-y-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
          <span class="text-xs font-bold text-slate-300">မြန်မာစာသား ရိုက်ထည့်ရန်</span>
          <textarea id="textInput" rows="5" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500">သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>

          <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800 text-xs">
            <div>
              <div class="flex justify-between text-slate-400 mb-1">
                <span>အမြန်နှုန်း</span>
                <span id="speedVal" class="text-amber-400">မူရင်း</span>
              </div>
              <input id="speedRange" type="range" min="-20" max="20" step="2" value="0" class="w-full accent-amber-500" oninput="updateLabels()" />
            </div>
            <div>
              <div class="flex justify-between text-slate-400 mb-1">
                <span>အသံအမြင့် (Pitch)</span>
                <span id="pitchVal" class="text-amber-400">မူရင်း</span>
              </div>
              <input id="pitchRange" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-amber-500" oninput="updateLabels()" />
            </div>
          </div>

          <button id="generateBtn" type="button" onclick="handleGenerate()" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 active:scale-95 transition-all">
            <span id="generateSpinner" class="hidden animate-spin">🌀</span>
            <span id="generateText">🎙 အသံဖန်တီးမည် (Generate Voice)</span>
          </button>
        </div>

        <div id="playerSection" class="hidden bg-slate-900 border border-amber-500/40 rounded-2xl p-4 space-y-3">
          <div class="text-xs font-bold text-amber-300" id="playerTitle">အသံဖိုင် အသင့်ဖြစ်ပါပြီ</div>
          <audio id="mainAudio" controls class="w-full rounded-lg outline-none"></audio>
          <button type="button" onclick="downloadCurrentMp3()" class="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-2">
            <span>📥</span>
            <span>MP3 ဒေါင်းလုဒ်ဆွဲမည်</span>
          </button>
        </div>
      </section>
    </main>
  </div>

  <audio id="previewAudio" class="hidden"></audio>

  <script>
    const PERSONAS = [
      { id: "u-han", name: "ဦးဟန်", icon: "👨", badge: "အမျိုးသားကြီး", role: "တည်ကြည် ခန့်ညားသော လူကြီးသံ (သတင်း/စာအုပ်)" },
      { id: "u-kyi", name: "ဦးကြည်", icon: "👴", badge: "အဖိုး/လူကြီးသံ", role: "ဩဇာတိက္ကမပြည့်ဝသော လေးနက်သည့်အသံ" },
      { id: "nay-toe", name: "နေတိုး", icon: "👦", badge: "လူငယ်အမျိုးသား", role: "တက်ကြွသော လူငယ်သံ (Movie Recap အကောင်းဆုံး)" },
      { id: "tay-za", name: "တေဇ", icon: "🧑", badge: "လူငယ်အမျိုးသား", role: "သဘာဝကျပြီး ရှင်းလင်းပြတ်သားသော ဇာတ်ကြောင်းပြောသံ" },
      { id: "zaw-zaw", name: "ဇော်ဇော်", icon: "🧒", badge: "ဆယ်ကျော်သက်", role: "သွက်လက်ပေါ့ပါးသော လူငယ်စကားပြောဟန်" },
      { id: "daw-yin", name: "ဒေါ်ရင်", icon: "👩", badge: "အမျိုးသမီးကြီး", role: "နွေးထွေးကြင်နာတတ်သော မိခင်သံ" },
      { id: "daw-soe", name: "ဒေါ်စိုး", icon: "🧕", badge: "အမျိုးသမီးကြီး", role: "တည်ငြိမ်ရင့်ကျက်သော အိမ်ထောင်ရှင်အမျိုးသမီးသံ" },
      { id: "tha-zin", name: "သဇင်", icon: "👧", badge: "မိန်းကလေးငယ်", role: "ချိုသာသွက်လက်သော အပျိုမလေးသံ (TikTok/Recap)" },
      { id: "may-hnin", name: "မေနှင်း", icon: "🌸", badge: "မိန်းကလေးငယ်", role: "ကြည်လင်အေးချမ်းသော ကောင်မလေးသံ (ပုံပြင်/ဝတ္ထု)" },
      { id: "nu-nu", name: "နုနု", icon: "🎀", badge: "မိန်းကလေးငယ်", role: "နူးညံ့ချစ်စဖွယ် ကလေးမလေးသံ" }
    ];

    let selectedId = "nay-toe";
    let playingPreviewId = null;
    let currentBlob = null;
    const previewAudioEl = document.getElementById("previewAudio");
    const mainAudioEl = document.getElementById("mainAudio");
    const textInputEl = document.getElementById("textInput");

    function renderVoices() {
      const c = document.getElementById("voiceCardsList");
      c.innerHTML = "";
      PERSONAS.forEach(p => {
        const isSel = p.id === selectedId;
        const isPrev = p.id === playingPreviewId;
        const div = document.createElement("div");
        div.className = `p-2.5 rounded-xl border flex items-center justify-between gap-2 cursor-pointer transition-all ${
          isSel ? "bg-amber-950/40 border-amber-500 ring-1 ring-amber-500" : "bg-slate-950/60 border-slate-800"
        }`;
        div.onclick = () => selectVoice(p.id);
        div.innerHTML = `
          <div class="flex items-center gap-2.5">
            <span class="text-2xl">${p.icon}</span>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="font-bold text-xs text-slate-100">${p.name}</span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">${p.badge}</span>
                ${isSel ? '<span class="text-[9px] text-amber-400 font-bold">✓ ရွေးထားသည်</span>' : ''}
              </div>
              <p class="text-[11px] text-slate-400">${p.role}</p>
            </div>
          </div>
          <button type="button" onclick="playPreview('${p.id}', event)" class="px-2.5 py-1.5 rounded-lg text-xs font-bold shrink-0 ${
            isPrev ? 'bg-amber-500 text-slate-950 animate-pulse' : 'bg-slate-800 text-amber-300'
          }">
            ${isPrev ? '⏹ ရပ်မည်' : '🔈 စမ်းနားထောင်'}
          </button>
        `;
        c.appendChild(div);
      });
    }

    function selectVoice(id) {
      selectedId = id;
      const p = PERSONAS.find(x => x.id === id);
      document.getElementById("selectedBadge").innerText = `ရွေးထားသည်: ${p.name}`;
      renderVoices();
    }

    async function playPreview(id, ev) {
      ev.stopPropagation();
      if (playingPreviewId === id) {
        previewAudioEl.pause();
        playingPreviewId = null;
        renderVoices();
        return;
      }
      playingPreviewId = id;
      renderVoices();

      try {
        let res = await fetch(`/api/preview/${id}`);
        if (!res.ok) res = await fetch(`/preview/${id}`);
        if (res.ok) {
          const blob = await res.blob();
          previewAudioEl.src = URL.createObjectURL(blob);
          await previewAudioEl.play();
          return;
        }
      } catch (e) {}

      playingPreviewId = null;
      renderVoices();
      alert("အသံစမ်းဖွင့်၍ မရသေးပါ။ စက္ကန့် ၃၀ ခန့်စောင့်ပြီး ပြန်လည်စမ်းသပ်ပေးပါ။");
    }

    previewAudioEl.onended = () => {
      playingPreviewId = null;
      renderVoices();
    };

    function updateLabels() {
      const s = parseInt(document.getElementById("speedRange").value);
      const p = parseInt(document.getElementById("pitchRange").value);
      document.getElementById("speedVal").innerText = s === 0 ? "မူရင်း" : `${s > 0 ? '+' : ''}${s}%`;
      document.getElementById("pitchVal").innerText = p === 0 ? "မူရင်း" : `${p > 0 ? '+' : ''}${p}Hz`;
    }

    async function handleGenerate() {
      const text = textInputEl.value.trim();
      if (!text) return alert("စာသား အရင်ရိုက်ထည့်ပါ");
      const btn = document.getElementById("generateBtn");
      const spinner = document.getElementById("generateSpinner");
      const btnText = document.getElementById("generateText");
      btn.disabled = true;
      spinner.classList.remove("hidden");
      btnText.innerText = "အသံဖန်တီးနေပါသည်...";

      try {
        let res = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: text,
            persona_id: selectedId,
            user_rate_offset: parseInt(document.getElementById("speedRange").value),
            user_pitch_offset: parseInt(document.getElementById("pitchRange").value)
          })
        });

        if (!res.ok) {
          res = await fetch("/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: text,
              persona_id: selectedId,
              user_rate_offset: parseInt(document.getElementById("speedRange").value),
              user_pitch_offset: parseInt(document.getElementById("pitchRange").value)
            })
          });
        }

        if (res.ok) {
          currentBlob = await res.blob();
          mainAudioEl.src = URL.createObjectURL(currentBlob);
          document.getElementById("playerSection").classList.remove("hidden");
          await mainAudioEl.play();
        } else {
          const errData = await res.json().catch(() => ({}));
          alert("အသံဖန်တီးရာတွင် အဆင်မပြေဖြစ်သွားပါသည်: " + (errData.detail || "Server Busy"));
        }
      } catch (e) {
        alert("ချိတ်ဆက်မှု မအောင်မြင်ပါ။ ခဏစောင့်ပြီး ပြန်လည်စမ်းသပ်ပေးပါ။");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        btnText.innerText = "🎙️ အသံဖန်တီးမည် (Generate Voice)";
      }
    }

    function downloadCurrentMp3() {
      if (!currentBlob) return;
      const a = document.createElement("a");
      a.href = URL.createObjectURL(currentBlob);
      a.download = `TTS_Pro_${selectedId}_${Date.now()}.mp3`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }

    renderVoices();
  </script>
</body>
</html>
"""

PERSONA_VOICES = [
    {"id": "u-han", "base_voice": "my-MM-ThihaNeural", "base_rate": "-4%", "base_pitch": "-12Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဦးဟန် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "u-kyi", "base_voice": "my-MM-ThihaNeural", "base_rate": "-6%", "base_pitch": "-18Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဦးကြည် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "nay-toe", "base_voice": "my-MM-ThihaNeural", "base_rate": "+4%", "base_pitch": "+4Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် နေတိုး ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "tay-za", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် တေဇ ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "zaw-zaw", "base_voice": "my-MM-ThihaNeural", "base_rate": "+7%", "base_pitch": "+12Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဇော်ဇော် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "daw-yin", "base_voice": "my-MM-NilarNeural", "base_rate": "-4%", "base_pitch": "-8Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်ရင် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "daw-soe", "base_voice": "my-MM-NilarNeural", "base_rate": "-6%", "base_pitch": "-14Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်စိုး ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "tha-zin", "base_voice": "my-MM-NilarNeural", "base_rate": "+3%", "base_pitch": "+6Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ သဇင် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"},
    {"id": "may-hnin", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ မေနှင်း ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"},
    {"id": "nu-nu", "base_voice": "my-MM-NilarNeural", "base_rate": "+2%", "base_pitch": "+12Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ နုနု ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်ရှင်။"}
]
PERSONA_DICT = {p["id"]: p for p in PERSONA_VOICES}

class GenerateTTSRequest(BaseModel):
    text: str
    persona_id: str = "nay-toe"
    user_rate_offset: int = 0
    user_pitch_offset: int = 0

@app.get("/")
def read_root():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api")
def read_api_root():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/health")
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/preview/{persona_id}")
@app.get("/preview/{persona_id}")
async def get_persona_preview(persona_id: str):
    persona = PERSONA_DICT.get(persona_id, PERSONA_VOICES[2])
    try:
        communicate = edge_tts.Communicate(
            text=persona["sample_text"],
            voice=persona["base_voice"],
            rate=persona["base_rate"],
            pitch=persona["base_pitch"]
        )
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
@app.post("/tts")
async def generate_speech(req: GenerateTTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="စာသား ထည့်သွင်းပေးရန် လိုအပ်ပါသည်။")
    
    persona = PERSONA_DICT.get(req.persona_id, PERSONA_VOICES[2])
    base_r = int(persona["base_rate"].replace("%", "").replace("+", ""))
    total_rate = base_r + req.user_rate_offset
    rate_str = f"{'+' if total_rate >= 0 else ''}{total_rate}%"
    
    base_p = int(persona["base_pitch"].replace("Hz", "").replace("+", ""))
    total_pitch = base_p + req.user_pitch_offset
    pitch_str = f"{'+' if total_pitch >= 0 else ''}{total_pitch}Hz"

    try:
        communicate = edge_tts.Communicate(
            text=req.text.strip(),
            voice=persona["base_voice"],
            rate=rate_str,
            pitch=pitch_str
        )
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
