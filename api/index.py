import os
import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="TTS Pro & Groq Video Transcript AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="my" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>TTS Pro & Groq Video Transcript</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Padauk', 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 5px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    .switch-checkbox:checked + .switch-label { background-color: #f59e0b; }
    .switch-checkbox:checked + .switch-label .switch-dot { transform: translateX(100%); background-color: #030712; }
  </style>
</head>
<body class="bg-[#090d16] text-slate-100 min-h-screen flex flex-col items-center antialiased">

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Header Navigation -->
  <header class="w-full border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-lg shadow-lg shadow-amber-500/20 font-bold text-slate-950">
          ⚡
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-bold tracking-tight text-white">TTS Pro & Groq Transcript</h1>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Groq Powered
            </span>
          </div>
          <p class="text-[11px] text-slate-400 hidden sm:block">Ultra-fast Groq AI ဗီဒီယို ဇာတ်ညွှန်းဘာသာပြန်နှင့် မြန်မာအသံစနစ်</p>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs font-bold">
        <button id="tabTranscriptBtn" onclick="switchMainTab('transcript')" class="px-3 py-1.5 rounded-lg bg-amber-500 text-slate-950 transition-all flex items-center gap-1.5">
          <span>📝</span>
          <span>Transcript</span>
        </button>
        <button id="tabTtsBtn" onclick="switchMainTab('tts')" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5">
          <span>🎙️</span>
          <span>TTS Studio</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Body Content -->
  <main class="max-w-5xl w-full p-4 sm:p-6 space-y-6 flex-1">

    <!-- ========================================== -->
    <!-- SECTION 1: TRANSCRIPT (Groq AI)            -->
    <!-- ========================================== -->
    <div id="sectionTranscript" class="space-y-6">

      <!-- Header Info Banner -->
      <div class="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-amber-500/15 via-orange-500/5 to-transparent border border-amber-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-base font-bold text-amber-300 flex items-center gap-2">
            <span>⚡</span>
            <span>Groq Video Transcript & Burmese Script Generator</span>
          </h2>
          <p class="text-xs text-slate-300 mt-1 leading-relaxed">
            မည်သည့် ဘာသာစကားပြော Video ကိုမဆို ထည့်သွင်းပါ။ Groq AI ဖြင့် မူရင်းဗီဒီယိုထက် ၃၀ စက္ကန့် ပိုရှည်သော လူတိုင်းနားလည်လွယ်သည့် သဘာဝကျ မြန်မာဇာတ်ညွှန်း ရေးသားပေးပါမည်။
          </p>
        </div>
        <div class="flex items-center gap-2 text-xs shrink-0 bg-slate-900/90 border border-slate-800 px-3 py-2 rounded-xl text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>အင်္ဂလိပ်စာလုံး လုံးဝမပါ</span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left: Upload & Config Controls -->
        <div class="lg:col-span-5 space-y-4">

          <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 space-y-4 backdrop-blur-sm shadow-xl">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300 block">၁။ Video / Audio ဖိုင် ရွေးချယ်ပါ</span>

            <div
              onclick="document.getElementById('videoFileInput').click()"
              class="border-2 border-dashed border-slate-700 hover:border-amber-500/70 rounded-2xl p-6 text-center cursor-pointer transition-all bg-slate-950/60 hover:bg-slate-900/50 group"
            >
              <input type="file" id="videoFileInput" accept="video/*,audio/*" class="hidden" onchange="handleVideoSelected(event)" />
              <div class="w-12 h-12 mx-auto rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                🎥
              </div>
              <p class="text-xs font-bold text-slate-200 mt-3" id="uploadPromptText">Video ဖိုင်ကို ဤနေရာတွင် နှိပ်၍ ရွေးပါ</p>
              <p class="text-[11px] text-slate-500 mt-1">MP4, MKV, WebM, MP3, WAV (Groq Whisper Speed)</p>
            </div>

            <!-- Video Player Preview -->
            <div id="videoPreviewBox" class="hidden space-y-2">
              <video id="previewVideoEl" controls class="w-full rounded-xl max-h-48 bg-black border border-slate-800"></video>
              <div class="flex items-center justify-between text-xs px-2 text-slate-400">
                <span>ဗီဒီယို ကြာချိန်:</span>
                <span id="videoDurationLabel" class="font-bold text-amber-400 font-mono">00:00</span>
              </div>
              <div class="p-2.5 rounded-xl bg-amber-950/40 border border-amber-800/60 text-[11px] text-amber-300 flex items-center justify-between">
                <span>⏱ ဖန်တီးမည့် Script အလျား:</span>
                <span id="targetDurationLabel" class="font-bold font-mono">+၃၀ စက္ကန့် ပိုရှည်မည်</span>
              </div>
            </div>

            <!-- Add Timestamp Toggle Switch -->
            <div class="pt-3 border-t border-slate-800 flex items-center justify-between">
              <div>
                <div class="text-xs font-bold text-slate-200">Add Time Stamp</div>
                <div class="text-[10px] text-slate-400">မိနစ်အလိုက် အချိန်မှတ် (ဥပမာ [00:00]) ထည့်သွင်းမည်</div>
              </div>
              <div class="relative inline-block w-11 h-6 align-middle select-none">
                <input type="checkbox" id="timestampSwitch" class="switch-checkbox hidden" />
                <label for="timestampSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
                  <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
                </label>
              </div>
            </div>

            <!-- Groq API Key -->
            <div class="pt-3 border-t border-slate-800 space-y-1.5">
              <div class="flex items-center justify-between">
                <label class="text-[11px] font-bold text-slate-300">Groq API Key (console.groq.com)</label>
                <a href="https://console.groq.com/keys" target="_blank" class="text-[10px] text-amber-400 hover:underline">Key ရယူရန် (Free) ↗</a>
              </div>
              <input
                type="password"
                id="groqApiKeyInput"
                placeholder="gsk_... (Groq API Key ထည့်ပါ)"
                class="w-full bg-[#030712] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 font-mono"
              />
              <p class="text-[10px] text-slate-500">Groq Console မှရရှိသော `gsk_` ဖြင့်စသော Key ကို ထည့်ပါ (Browser ထဲတွင် အလိုအလျောက် မှတ်ထားပေးပါမည်)။</p>
            </div>

            <!-- Start Process Button -->
            <button
              id="startTranscriptBtn"
              onclick="generateGroqTranscript()"
              class="w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:brightness-110 active:scale-[0.99] text-slate-950 font-bold text-xs shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              <span id="transSpinner" class="hidden animate-spin">🌀</span>
              <span id="transBtnText">⚡ Groq ဖြင့် စာညွှန်းထုတ်ယူမည် (+30s)</span>
            </button>
          </div>

        </div>

        <!-- Right: Output Script Result -->
        <div class="lg:col-span-7 space-y-4">
          <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 space-y-3 backdrop-blur-sm shadow-xl flex flex-col h-full min-h-[480px]">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-300">၂။ မြန်မာဇာတ်ညွှန်း ရလဒ် (Pure Burmese Script)</span>
              </div>
              <div class="flex items-center gap-2">
                <span id="scriptWordCount" class="text-[11px] text-slate-400 font-mono">၀ စကားလုံး</span>
              </div>
            </div>

            <!-- Text Box -->
            <div class="relative flex-1">
              <textarea
                id="transcriptOutputText"
                placeholder="Video ဖိုင် ရွေးချယ်ပြီး Groq ဖြင့် ဘာသာပြန်လိုက်ပါက ဤနေရာတွင် အပိုစာသားနှင့် အင်္ဂလိပ်စာလုံး လုံးဝမပါသော သဘာဝကျသည့် မြန်မာဘာသာပြန် ဇာတ်ညွှန်း ထွက်ပေါ်လာမည် ဖြစ်ပါသည်..."
                class="w-full h-full min-h-[360px] bg-[#030712] border border-slate-800/80 rounded-xl p-4 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 custom-scroll font-sans"
              ></textarea>
            </div>

            <!-- Buttons -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800">
              <button
                type="button"
                onclick="copyTranscriptScript()"
                class="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 font-bold text-xs border border-amber-500/30 flex items-center justify-center gap-2 transition-all active:scale-95 shadow-sm"
              >
                <span>📋</span>
                <span id="copyBtnText">Script အားလုံး ကူးယူမည် (One-Click Copy)</span>
              </button>

              <button
                type="button"
                onclick="sendScriptToTts()"
                class="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:brightness-110 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-emerald-600/20"
              >
                <span>🎙️</span>
                <span>TTS အသံထုတ်ခန်းသို့ ပို့မည်</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 2: TTS STUDIO                      -->
    <!-- ========================================== -->
    <div id="sectionTts" class="hidden space-y-6">

      <div class="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-orange-500/5 to-transparent border border-amber-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-sm font-bold text-amber-300 flex items-center gap-1.5">
            <span>✨</span>
            <span>မြန်မာအသံ ကာရိုက်တာ (၁၀) မျိုးဖြင့် အသံဖန်တီးခန်း</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5 leading-relaxed">
            စာသားများကို ရိုက်ထည့်၍ဖြစ်စေ၊ Transcript မှ ရရှိလာသော ဇာတ်ညွှန်းကိုဖြစ်စေ MP3 အသံဖိုင် တိုက်ရိုက် ထုတ်ယူပါ
          </p>
        </div>
        <div id="activeVoicePill" class="text-xs font-bold text-amber-300 bg-amber-950/80 border border-amber-800/80 px-3 py-1.5 rounded-xl shrink-0">
          ရွေးထားသည်: နေတိုး
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Voice Selector -->
        <section class="lg:col-span-6 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 space-y-4 backdrop-blur-sm">
          <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider">အသံကဏ္ဍခွဲများ</span>
            <div class="flex gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-[11px]">
              <button onclick="filterVoices('all')" class="cat-pill px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-bold transition-all" data-cat="all">အားလုံး</button>
              <button onclick="filterVoices('men')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="men">လူကြီး</button>
              <button onclick="filterVoices('boy')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="boy">လူငယ်</button>
              <button onclick="filterVoices('women')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="women">အမျိုးသမီး</button>
              <button onclick="filterVoices('girl')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="girl">မိန်းကလေး</button>
            </div>
          </div>
          <div id="voiceCardsList" class="space-y-2.5 max-h-[460px] overflow-y-auto pr-1.5 custom-scroll"></div>
        </section>

        <!-- Right: Text Input & TTS Controls -->
        <section class="lg:col-span-6 space-y-5">
          <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 sm:p-5 space-y-4 backdrop-blur-sm shadow-xl">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-300">မြန်မာစာသား ထည့်သွင်းရန်</span>
              <div class="flex items-center gap-2 text-xs text-slate-400">
                <span id="charCount" class="font-mono text-[11px] text-amber-400 font-semibold">၀ အက္ခရာ</span>
                <span>•</span>
                <button onclick="clearText()" class="text-rose-400 hover:underline">ဖျက်မည်</button>
              </div>
            </div>

            <textarea
              id="textInput"
              rows="6"
              placeholder="အသံဖန်တီးလိုသော မြန်မာစာသားများကို ရိုက်ထည့်ပါ..."
              class="w-full bg-[#030712] border border-slate-800 rounded-xl p-3.5 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500/80 transition-all resize-y"
            >သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>

            <div class="grid grid-cols-2 gap-4 pt-3 border-t border-slate-800/80">
              <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-slate-400">စကားပြောနှုန်း</span>
                  <span id="speedVal" class="text-amber-400 font-mono font-bold">မူရင်း</span>
                </div>
                <input id="speedRange" type="range" min="-20" max="20" step="2" value="0" class="w-full accent-amber-500" oninput="updateTuningLabels()" />
              </div>
              <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-slate-400">အသံအမြင့် (Pitch)</span>
                  <span id="pitchVal" class="text-amber-400 font-mono font-bold">မူရင်း</span>
                </div>
                <input id="pitchRange" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-amber-500" oninput="updateTuningLabels()" />
              </div>
            </div>

            <button
              id="generateBtn"
              type="button"
              onclick="handleGenerateVoice()"
              class="w-full py-4 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:brightness-110 active:scale-[0.99] text-slate-950 font-bold text-sm shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2.5 transition-all"
            >
              <span id="genSpinner" class="hidden animate-spin">🌀</span>
              <span id="genText">🎙 အသံဖန်တီးမည် (Generate Speech)</span>
            </button>
          </div>

          <!-- Audio Player Section -->
          <div id="playerSection" class="hidden bg-gradient-to-b from-slate-900 to-slate-950 border border-amber-500/40 rounded-2xl p-5 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="playerVoiceTitle" class="text-xs font-bold text-amber-300">အသံဖိုင် အဆင်သင့်ဖြစ်ပါပြီ</span>
              </div>
              <span class="text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">MP3 Ready</span>
            </div>
            <audio id="mainAudio" controls class="w-full rounded-xl outline-none"></audio>
            <button
              type="button"
              onclick="downloadMp3()"
              class="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/25 transition-all"
            >
              <span>📥</span>
              <span>MP3 ဒေါင်းလုဒ်ဆွဲမည် (Download Audio)</span>
            </button>
          </div>
        </section>

      </div>
    </div>

  </main>

  <audio id="previewAudio" class="hidden"></audio>

  <script>
    // Tab Switching Logic
    function switchMainTab(tab) {
      const ttsSec = document.getElementById("sectionTts");
      const transSec = document.getElementById("sectionTranscript");
      const ttsBtn = document.getElementById("tabTtsBtn");
      const transBtn = document.getElementById("tabTranscriptBtn");

      if (tab === "transcript") {
        ttsSec.classList.add("hidden");
        transSec.classList.remove("hidden");
        transBtn.className = "px-3 py-1.5 rounded-lg bg-amber-500 text-slate-950 font-bold transition-all flex items-center gap-1.5";
        ttsBtn.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
      } else {
        transSec.classList.add("hidden");
        ttsSec.classList.remove("hidden");
        ttsBtn.className = "px-3 py-1.5 rounded-lg bg-amber-500 text-slate-950 font-bold transition-all flex items-center gap-1.5";
        transBtn.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
      }
    }

    // Toast Notification System
    function showToast(msg, type = "info") {
      const container = document.getElementById("toastContainer");
      const toast = document.createElement("div");
      toast.className = `px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold flex items-center gap-2 transition-all transform duration-300 translate-y-2 opacity-0 pointer-events-auto border ${
        type === 'error' ? 'bg-rose-950 border-rose-800 text-rose-200' :
        type === 'success' ? 'bg-emerald-950 border-emerald-800 text-emerald-200' :
        'bg-slate-900 border-slate-700 text-slate-200'
      }`;
      toast.innerHTML = `<span>${type === 'error' ? '⚠' : type === 'success' ? '✓' : 'ℹ️'}</span><span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => toast.classList.remove('translate-y-2', 'opacity-0'), 20);
      setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    // ==========================================
    // GROQ TRANSCRIPT LOGIC
    // ==========================================
    let currentVideoFile = null;
    let videoDurationSeconds = 0;

    // Load saved Groq Key from local storage
    const savedGroqKey = localStorage.getItem("groq_api_key") || "";
    if (savedGroqKey) {
      document.getElementById("groqApiKeyInput").value = savedGroqKey;
    }

    document.getElementById("groqApiKeyInput").addEventListener("input", (e) => {
      localStorage.setItem("groq_api_key", e.target.value.trim());
    });

    function handleVideoSelected(e) {
      const file = e.target.files[0];
      if (!file) return;

      currentVideoFile = file;
      document.getElementById("uploadPromptText").innerText = file.name;

      const videoEl = document.getElementById("previewVideoEl");
      videoEl.src = URL.createObjectURL(file);
      document.getElementById("videoPreviewBox").classList.remove("hidden");

      videoEl.onloadedmetadata = () => {
        videoDurationSeconds = Math.round(videoEl.duration);
        const mins = Math.floor(videoDurationSeconds / 60);
        const secs = videoDurationSeconds % 60;
        document.getElementById("videoDurationLabel").innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        const targetSecs = videoDurationSeconds + 30;
        const tMins = Math.floor(targetSecs / 60);
        const tSecs = targetSecs % 60;
        document.getElementById("targetDurationLabel").innerText = `${tMins.toString().padStart(2, '0')}:${tSecs.toString().padStart(2, '0')} (+30s ထပ်ဆောင်း)`;
        showToast("Video အလျားကို အောင်မြင်စွာ စစ်ဆေးပြီးပါပြီ", "success");
      };
    }

    async function generateGroqTranscript() {
      if (!currentVideoFile) {
        showToast("ကျေးဇူးပြု၍ Video ဖိုင် အရင်ရွေးချယ်ပေးပါ", "error");
        return;
      }

      const apiKey = document.getElementById("groqApiKeyInput").value.trim();
      if (!apiKey || !apiKey.startsWith("gsk_")) {
        showToast("Groq API Key (gsk_...) ကို မှန်ကန်စွာ ထည့်ပေးပါ (console.groq.com/keys)", "error");
        return;
      }

      const btn = document.getElementById("startTranscriptBtn");
      const spinner = document.getElementById("transSpinner");
      const btnText = document.getElementById("transBtnText");
      const outputText = document.getElementById("transcriptOutputText");
      const includeTimestamps = document.getElementById("timestampSwitch").checked;

      btn.disabled = true;
      spinner.classList.remove("hidden");
      btnText.innerText = "၁/၂: Groq Whisper ဖြင့် အသံဖတ်နေပါသည်...";
      outputText.value = "အဆင့် ၁: Groq Whisper Large-V3 စနစ်ဖြင့် Video ထဲမှ စကားပြောသံများကို အလွန်လျင်မြန်စွာ ဖတ်ရှုနေပါသည်...";

      try {
        // Step 1: Transcribe Audio using Groq Whisper API
        const formData = new FormData();
        formData.append("file", currentVideoFile);
        formData.append("model", "whisper-large-v3");
        formData.append("response_format", includeTimestamps ? "verbose_json" : "json");

        const whisperRes = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${apiKey}`
          },
          body: formData
        });

        if (!whisperRes.ok) {
          const errData = await whisperRes.json().catch(() => ({}));
          throw new Error(errData.error?.message || "Groq Whisper ချိတ်ဆက်မှု မအောင်မြင်ပါ (ဖိုင်အရွယ်အစား 25MB ထက် မကျော်လွန်စေရန် ဂရုပြုပါ)");
        }

        const whisperData = await whisperRes.json();
        let originalText = whisperData.text || "";

        if (includeTimestamps && whisperData.segments) {
          originalText = whisperData.segments.map(s => {
            const startM = Math.floor(s.start / 60).toString().padStart(2, '0');
            const startS = Math.floor(s.start % 60).toString().padStart(2, '0');
            return `[${startM}:${startS}] ${s.text}`;
          }).join("\n");
        }

        btnText.innerText = "၂/၂: Groq Llama ဖြင့် မြန်မာဘာသာပြန်နေပါသည် (+30s)...";
        outputText.value = "အဆင့် ၂: အပိုစာသားနှင့် အင်္ဂလိပ်စာလုံး လုံးဝမပါဘဲ ဗီဒီယိုအလျားထက် စက္ကန့် ၃၀ ပိုရှည်အောင် မြန်မာစကားပြေအဖြစ် ပြန်ဆိုနေပါသည်...";

        // Step 2: Translate and expand by +30 seconds using Groq LLaMA 3.3 70B
        const targetSecs = videoDurationSeconds + 30;
        const targetWords = Math.max(120, Math.round(targetSecs * 2.8));

        const systemPrompt = `
သင်သည် အဆင့်မြင့် ရုပ်ရှင်ဇာတ်ညွှန်းနှင့် ဗီဒီယို ဘာသာပြန် ကျွမ်းကျင်သူ ဖြစ်သည်။
ပေးထားသော Video ဇာတ်ကြောင်း စကားများကို အောက်ပါ တိကျသော စည်းမျဉ်း (၄) ချက်အတိုင်း မြန်မာလို ပြန်ဆိုပေးပါ:

၁။ အပိုစာသားနှင့် English စာသား လုံးဝ (လုံးဝ) မထည့်ပါနှင့်။ (ဥပမာ "Here is the Burmese translation:", "Title:", "Summary:" စသည့် စကားလုံးများ၊ နိဒါန်းစာများနှင့် အင်္ဂလိပ်စာလုံးများ လုံးဝမပါရ)။
၂။ မူရင်းဗီဒီယို ကြာချိန်ထက် စက္ကန့် ၃၀ စာခန့် ပိုရှည်စေရန်အတွက် အကြောင်းအရာကို ပြည့်စုံသန့်ရှင်းစွာ အသေးစိတ် ချဲ့ထွင်၍ မြန်မာစကားလုံး ခန့်မှန်းခြေ ${targetWords} စကားလုံး ဝန်းကျင်အထိ ပါဝင်အောင် ဇာတ်ကြောင်းပြန် စာသားအဖြစ် ရေးပေးရမည်။
၃။ လူတိုင်း နားလည်လွယ်သော သဘာဝကျသည့် မြန်မာစကားပြော ပြေပြေပြစ်ပြစ် ဖြစ်ရမည်။
၄။ ${includeTimestamps ? "အချိန်မှတ် (Time Stamp) များကို ဥပမာ [00:00], [00:30] ပုံစံဖြင့် ဝါကျများရှေ့တွင် ဆက်လက် ထည့်သွင်းပေးပါ။" : "အချိန်မှတ် (Time Stamp) များကို လုံးဝ မထည့်ပါနှင့်၊ သဘာဝကျသော စာပိုဒ်များဖြင့်သာ ရေးပေးပါ။"}

အထက်ပါ စည်းမျဉ်းအတိုင်း မြန်မာစာသား စစ်စစ်ကိုသာ တိုက်ရိုက် ထုတ်ပေးပါ:
        `.trim();

        const llmRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "llama-3.3-70b-versatile",
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: `မူရင်း ဗီဒီယို စာသားများ:\n${originalText}` }
            ],
            temperature: 0.6
          })
        });

        if (!llmRes.ok) {
          const errData = await llmRes.json().catch(() => ({}));
          throw new Error(errData.error?.message || "Groq Translation မအောင်မြင်ပါ");
        }

        const llmData = await llmRes.json();
        const finalScript = llmData.choices?.[0]?.message?.content || "";

        if (finalScript) {
          outputText.value = finalScript.trim();
          const words = finalScript.trim().split(/\s+/).length;
          document.getElementById("scriptWordCount").innerText = `${words} စကားလုံး`;
          showToast("Groq ဖြင့် မြန်မာဇာတ်ညွှန်း အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ", "success");
        } else {
          throw new Error("စာသား ရယူ၍ မရပါ");
        }

      } catch (err) {
        outputText.value = `ချို့ယွင်းချက် ဖြစ်ပေါ်သွားပါသည်: ${err.message}`;
        showToast(err.message, "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        btnText.innerText = "⚡ Groq ဖြင့် စာညွှန်းထုတ်ယူမည် (+30s)";
      }
    }

    function copyTranscriptScript() {
      const text = document.getElementById("transcriptOutputText").value.trim();
      if (!text) {
        showToast("ကူးယူရန် စာသား မရှိသေးပါ", "error");
        return;
      }
      navigator.clipboard.writeText(text).then(() => {
        showToast("ဇာတ်ညွှန်းစာသား အားလုံးကို ကူးယူပြီးပါပြီ (Copied)", "success");
        const btnText = document.getElementById("copyBtnText");
        btnText.innerText = "✓ ကူးယူပြီးပါပြီ!";
        setTimeout(() => btnText.innerText = "Script အားလုံး ကူးယူမည် (One-Click Copy)", 2000);
      });
    }

    function sendScriptToTts() {
      const text = document.getElementById("transcriptOutputText").value.trim();
      if (!text) {
        showToast("TTS သို့ ပို့ရန် စာသား မရှိသေးပါ", "error");
        return;
      }
      const cleanTextForTts = text.replace(/\[\d{2}:\d{2}\]/g, '').trim();
      document.getElementById("textInput").value = cleanTextForTts;
      document.getElementById("charCount").innerText = `${cleanTextForTts.length} အက္ခရာ`;
      switchMainTab("tts");
      showToast("စာသားများကို TTS အသံထုတ်ခန်းသို့ ထည့်သွင်းပြီးပါပြီ", "success");
    }

    // ==========================================
    // TTS STUDIO LOGIC
    // ==========================================
    const PERSONAS = [
      { id: "nay-toe", name: "နေတိုး", category: "boy", icon: "👦", badge: "လူငယ်အမျိုးသား", role: "တက်ကြွ လန်းဆန်းသော လူငယ်သံ (Movie Recap အကောင်းဆုံး)", sample: "မင်္ဂလာပါ၊ ကျွန်တော် နေတိုး ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "tha-zin", name: "သဇင်", category: "girl", icon: "👧", badge: "မိန်းကလေးငယ်", role: "သွက်လက် ချိုသာသော အပျိုမလေးသံ (TikTok / Shorts အထူးကောင်း)", sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ သဇင် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။" },
      { id: "tay-za", name: "တေဇ", category: "boy", icon: "🧑", badge: "လူငယ်အမျိုးသား", role: "သဘာဝကျပြီး ရှင်းလင်းပြတ်သားသော ဇာတ်ကြောင်းပြောဟန်", sample: "မင်္ဂလာပါ၊ ကျွန်တော် တေဇ ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "may-hnin", name: "မေနှင်း", category: "girl", icon: "🌸", badge: "မိန်းကလေးငယ်", role: "ကြည်လင် အေးချမ်းသော ကောင်မလေးသံ (ဝတ္ထုဖတ်/စာအုပ်)", sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ မေနှင်း ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။" },
      { id: "u-han", name: "ဦးဟန်", category: "men", icon: "👨", badge: "လူကြီးအမျိုးသား", role: "တည်ကြည် ခန့်ညားသော လူကြီးသံ (သတင်း/အသိပညာပေး)", sample: "မင်္ဂလာပါ၊ ကျွန်တော် ဦးဟန် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "u-kyi", name: "ဦးကြည်", category: "men", icon: "👴", badge: "အဖိုး/လူကြီးသံ", role: "အသံဩဇာပြည့်ဝပြီး လေးနက်သော အဖိုးကြီးသံ (သမိုင်း/ဒဏ္ဍာရီ)", sample: "မင်္ဂလာပါ၊ ကျွန်တော် ဦးကြည် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "daw-yin", name: "ဒေါ်ရင်", category: "women", icon: "👩", badge: "အမျိုးသမီးကြီး", role: "နွေးထွေး ကြင်နာတတ်သော မိခင်သံ (တရားတော်/ဘဝအတွေ့အကြုံ)", sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်ရင် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "daw-soe", name: "ဒေါ်စိုး", category: "women", icon: "🧕", badge: "အမျိုးသမီးကြီး", role: "တည်ငြိမ် ရင့်ကျက်သော အိမ်ထောင်ရှင်အမျိုးသမီးသံ", sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်စိုး ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "zaw-zaw", name: "ဇော်ဇော်", category: "boy", icon: "🧒", badge: "ဆယ်ကျော်သက်", role: "သွက်လက် ပေါ့ပါးသော လူငယ်စကားပြောဟန် (Vlog/ဟာသ)", sample: "မင်္ဂလာပါ၊ ကျွန်တော် ဇော်ဇော် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။" },
      { id: "nu-nu", name: "နုနု", category: "girl", icon: "🎀", badge: "ကလေးမလေးသံ", role: "နူးညံ့ ချစ်စဖွယ် ကလေးမလေးသံ (ညအိပ်ရာဝင် ပုံပြင်)", sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ နုနု ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်ရှင်။" }
    ];

    let selectedId = "nay-toe";
    let playingPreviewId = null;
    let generatedBlob = null;

    const previewAudioEl = document.getElementById("previewAudio");
    const mainAudioEl = document.getElementById("mainAudio");
    const textInputEl = document.getElementById("textInput");

    function renderVoiceCards(category = "all") {
      const listContainer = document.getElementById("voiceCardsList");
      listContainer.innerHTML = "";
      const filtered = category === "all" ? PERSONAS : PERSONAS.filter(p => p.category === category);

      filtered.forEach(p => {
        const isSelected = p.id === selectedId;
        const isPreviewing = p.id === playingPreviewId;

        const card = document.createElement("div");
        card.className = `p-3 rounded-xl border transition-all flex items-center justify-between gap-2.5 cursor-pointer ${
          isSelected 
            ? "bg-amber-500/10 border-amber-500 ring-1 ring-amber-500/50 shadow-lg shadow-amber-500/10" 
            : "bg-slate-950/50 border-slate-800 hover:border-slate-700 hover:bg-slate-900/40"
        }`;
        card.onclick = () => selectVoice(p.id);

        card.innerHTML = `
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <div class="w-10 h-10 rounded-xl bg-slate-800/80 flex items-center justify-center text-xl shrink-0 border border-slate-700/50">
              ${p.icon}
            </div>
            <div class="truncate">
              <div class="flex items-center gap-1.5">
                <span class="font-bold text-xs sm:text-sm text-slate-100">${p.name}</span>
                <span class="text-[9px] px-1.5 py-0.5 rounded-full font-medium ${
                  p.category === 'men' ? 'bg-blue-950 text-blue-300 border border-blue-800/80' :
                  p.category === 'boy' ? 'bg-cyan-950 text-cyan-300 border border-cyan-800/80' :
                  p.category === 'women' ? 'bg-purple-950 text-purple-300 border border-purple-800/80' :
                  'bg-pink-950 text-pink-300 border border-pink-800/80'
                }">
                  ${p.badge}
                </span>
                ${isSelected ? '<span class="text-[9px] text-amber-400 font-bold ml-1">✓ ရွေးထားသည်</span>' : ''}
              </div>
              <p class="text-[11px] text-slate-400 truncate mt-0.5">${p.role}</p>
            </div>
          </div>

          <button
            type="button"
            onclick="togglePreview('${p.id}', event)"
            class="px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 flex items-center gap-1 transition-all ${
              isPreviewing ? 'bg-amber-500 text-slate-950 animate-pulse' : 'bg-slate-800/90 hover:bg-amber-950/60 text-amber-300 border border-amber-500/30'
            }"
          >
            <span>${isPreviewing ? '⏹' : '🔈'}</span>
            <span class="hidden sm:inline">${isPreviewing ? 'ရပ်မည်' : 'စမ်းနားထောင်'}</span>
          </button>
        `;
        listContainer.appendChild(card);
      });
    }

    function selectVoice(id) {
      selectedId = id;
      const p = PERSONAS.find(x => x.id === id);
      document.getElementById("activeVoicePill").innerText = `ရွေးထားသည်: ${p.name}`;
      const activeCat = document.querySelector(".cat-pill.bg-amber-500")?.dataset.cat || "all";
      renderVoiceCards(activeCat);
    }

    function filterVoices(cat) {
      document.querySelectorAll(".cat-pill").forEach(btn => {
        if (btn.dataset.cat === cat) {
          btn.className = "cat-pill px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-bold transition-all";
        } else {
          btn.className = "cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all";
        }
      });
      renderVoiceCards(cat);
    }

    async function togglePreview(id, event) {
      event.stopPropagation();
      if (playingPreviewId === id) {
        previewAudioEl.pause();
        playingPreviewId = null;
        renderVoiceCards(document.querySelector(".cat-pill.bg-amber-500")?.dataset.cat || "all");
        return;
      }

      playingPreviewId = id;
      renderVoiceCards(document.querySelector(".cat-pill.bg-amber-500")?.dataset.cat || "all");

      try {
        let res = await fetch(`/api/preview/${id}`);
        if (!res.ok) res = await fetch(`/preview/${id}`);
        if (res.ok) {
          const blob = await res.blob();
          previewAudioEl.src = URL.createObjectURL(blob);
          await previewAudioEl.play();
          return;
        }
      } catch (err) {}

      playingPreviewId = null;
      renderVoiceCards(document.querySelector(".cat-pill.bg-amber-500")?.dataset.cat || "all");
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ", "error");
    }

    previewAudioEl.onended = () => {
      playingPreviewId = null;
      renderVoiceCards(document.querySelector(".cat-pill.bg-amber-500")?.dataset.cat || "all");
    };

    function updateTuningLabels() {
      const s = parseInt(document.getElementById("speedRange").value);
      const p = parseInt(document.getElementById("pitchRange").value);
      document.getElementById("speedVal").innerText = s === 0 ? "မူရင်း" : `${s > 0 ? '+' : ''}${s}%`;
      document.getElementById("pitchVal").innerText = p === 0 ? "မူရင်း" : `${p > 0 ? '+' : ''}${p}Hz`;
    }

    textInputEl.addEventListener("input", () => {
      document.getElementById("charCount").innerText = `${textInputEl.value.length} အက္ခရာ`;
    });

    function clearText() {
      textInputEl.value = "";
      document.getElementById("charCount").innerText = "၀ အက္ခရာ";
      textInputEl.focus();
    }

    async function handleGenerateVoice() {
      const text = textInputEl.value.trim();
      if (!text) {
        showToast("စာသား အရင်ရိုက်ထည့်ပေးပါ", "error");
        return;
      }

      const btn = document.getElementById("generateBtn");
      const spinner = document.getElementById("genSpinner");
      const btnText = document.getElementById("genText");

      btn.disabled = true;
      spinner.classList.remove("hidden");
      btnText.innerText = "Cloud ပေါ်တွင် အသံဖန်တီးနေပါသည်...";

      const persona = PERSONAS.find(p => p.id === selectedId);

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
          generatedBlob = await res.blob();
          mainAudioEl.src = URL.createObjectURL(generatedBlob);
          document.getElementById("playerVoiceTitle").innerText = `${persona.name} (${persona.badge}) ၏ အသံဖိုင်`;
          document.getElementById("playerSection").classList.remove("hidden");
          await mainAudioEl.play();
          showToast(`${persona.name} ၏ အသံဖိုင်ကို ဖန်တီးပြီးပါပြီ`, "success");
        } else {
          showToast("အသံဖန်တီးရာတွင် အဆင်မပြေဖြစ်သွားပါသည်", "error");
        }
      } catch (err) {
        showToast("ချိတ်ဆက်မှု မအောင်မြင်ပါ", "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        btnText.innerText = "🎙️ အသံဖန်တီးမည် (Generate Speech)";
      }
    }

    function downloadMp3() {
      if (!generatedBlob) return;
      const persona = PERSONAS.find(p => p.id === selectedId);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(generatedBlob);
      a.download = `TTS_Pro_${persona.name}_${Date.now()}.mp3`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("MP3 ဒေါင်းလုဒ် ဆွဲပြီးပါပြီ", "success");
    }

    // Initialize View
    renderVoiceCards("all");
    updateTuningLabels();
    document.getElementById("charCount").innerText = `${textInputEl.value.length} အက္ခရာ`;
  </script>
</body>
</html>
"""

PERSONA_VOICES = [
    {"id": "nay-toe", "base_voice": "my-MM-ThihaNeural", "base_rate": "+4%", "base_pitch": "+4Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် နေတိုး ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "tha-zin", "base_voice": "my-MM-NilarNeural", "base_rate": "+3%", "base_pitch": "+6Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ သဇင် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"},
    {"id": "tay-za", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် တေဇ ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "may-hnin", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ မေနှင်း ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"},
    {"id": "u-han", "base_voice": "my-MM-ThihaNeural", "base_rate": "-4%", "base_pitch": "-12Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဦးဟန် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "u-kyi", "base_voice": "my-MM-ThihaNeural", "base_rate": "-6%", "base_pitch": "-18Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဦးကြည် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "daw-yin", "base_voice": "my-MM-NilarNeural", "base_rate": "-4%", "base_pitch": "-8Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်ရင် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "daw-soe", "base_voice": "my-MM-NilarNeural", "base_rate": "-6%", "base_pitch": "-14Hz", "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်စိုး ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
    {"id": "zaw-zaw", "base_voice": "my-MM-ThihaNeural", "base_rate": "+7%", "base_pitch": "+12Hz", "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဇော်ဇော် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"},
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
def health():
    return {"status": "ok"}

@app.get("/api/preview/{persona_id}")
@app.get("/preview/{persona_id}")
async def get_persona_preview(persona_id: str):
    persona = PERSONA_DICT.get(persona_id, PERSONA_VOICES[0])
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
    
    persona = PERSONA_DICT.get(req.persona_id, PERSONA_VOICES[0])
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
