import os
import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Recap Go AI - Burmese Script & TTS Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="my" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Recap Go • AI Script & Voice Studio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Padauk', 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 5px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    .switch-checkbox:checked + .switch-label { background-color: #3b82f6; }
    .switch-checkbox:checked + .switch-label .switch-dot { transform: translateX(100%); background-color: #ffffff; }
  </style>
</head>
<body class="bg-[#080d1a] text-slate-100 min-h-screen flex flex-col items-center antialiased selection:bg-blue-600 selection:text-white">

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Header Navigation -->
  <header class="w-full border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-xl sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-lg shadow-lg shadow-blue-500/20 font-bold text-white">
          ⚡
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-bold tracking-tight text-white">Recap Go</h1>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Max 200MB
            </span>
          </div>
          <p class="text-[11px] text-slate-400 hidden sm:block">Burmese Movie Recap Script & Speech Studio</p>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs font-bold">
        <button id="tabTranscriptBtn" onclick="switchMainTab('transcript')" class="px-3 py-1.5 rounded-lg bg-blue-600 text-white transition-all flex items-center gap-1.5">
          <span>📝</span>
          <span>Transcript (200MB)</span>
        </button>
        <button id="tabTtsBtn" onclick="switchMainTab('tts')" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5">
          <span>🎙️</span>
          <span>TTS Studio</span>
        </button>
      </div>
    </div>
  </header>

  <input
    type="file"
    id="videoFileInput"
    accept="video/*,audio/*"
    class="hidden"
  />

  <!-- Main Body Content -->
  <main class="max-w-5xl w-full p-4 sm:p-6 space-y-6 flex-1">

    <!-- ========================================== -->
    <!-- SECTION 1: TRANSCRIPT (Recap Go 200MB)     -->
    <!-- ========================================== -->
    <div id="sectionTranscript" class="space-y-6">

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left: Upload & Config Controls -->
        <div class="lg:col-span-5 space-y-4">

          <div class="bg-gradient-to-b from-slate-900/95 to-[#0d1527]/95 border border-slate-800/90 rounded-2xl p-5 space-y-4 shadow-2xl backdrop-blur-sm">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <span class="text-blue-400 text-sm">📤</span>
                <span>File Upload</span>
              </span>
              <span id="fileBadgeStatus" class="hidden text-[10px] px-2.5 py-0.5 rounded-full font-bold bg-emerald-950 text-emerald-300 border border-emerald-700 animate-pulse">
                ✓ Video ရောက်ရှိပြီး
              </span>
            </div>

            <!-- Upload Dropzone Label Container -->
            <label
              id="uploadDropzoneLabel"
              for="videoFileInput"
              class="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-2xl p-6 text-center cursor-pointer transition-all bg-[#070b14]/90 hover:bg-[#0c1322] block group"
            >
              <div class="space-y-2 pointer-events-none">
                <div class="w-12 h-12 mx-auto rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                  📁
                </div>
                <p class="text-xs font-bold text-slate-100" id="uploadPromptText">Drag & drop a video or audio file</p>
                <p class="text-[11px] text-slate-400 font-mono">mp4, mov, mp3, wav, m4a · max 200MB</p>
                <div class="pt-2">
                  <span class="inline-block px-4 py-2 rounded-xl bg-blue-600 group-hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition-all">
                    Browse (ဖိုင်ရွေးမည်)
                  </span>
                </div>
              </div>
            </label>

            <!-- Video Preview Card -->
            <div id="videoPreviewBox" class="hidden space-y-3 bg-[#050914] border-2 border-blue-500 rounded-2xl p-3.5 shadow-2xl transition-all">
              <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span class="text-xs font-bold text-emerald-300">တင်ထားသော ဗီဒီယို (Preview)</span>
                </div>
                <label for="videoFileInput" class="text-[11px] text-blue-400 hover:text-blue-300 font-bold underline cursor-pointer">
                  🔄 အသစ်လဲမည်
                </label>
              </div>

              <video
                id="previewVideoEl"
                controls
                playsinline
                webkit-playsinline="true"
                muted
                preload="auto"
                class="w-full rounded-xl max-h-52 bg-black border border-slate-800 shadow-inner"
              ></video>

              <div id="audioPreviewContainer" class="hidden space-y-2 p-3 rounded-xl bg-slate-900 border border-slate-800">
                <div class="flex items-center gap-2 text-xs text-amber-300 font-bold">
                  <span>🎵</span>
                  <span>Audio အသံဖိုင် စမ်းဖွင့်ရန်</span>
                </div>
                <audio id="previewAudioEl" controls class="w-full"></audio>
              </div>

              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                  <span class="text-[10px] text-slate-400 block">ဖိုင်အမည်:</span>
                  <span id="videoFileNameLabel" class="font-bold text-slate-100 truncate block text-[11px]">video.mp4</span>
                </div>
                <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                  <span class="text-[10px] text-slate-400 block">ဖိုင်အရွယ်အစား:</span>
                  <span id="videoFileSizeLabel" class="font-bold text-cyan-400 font-mono text-[11px]">0.0 MB</span>
                </div>
              </div>

              <div class="p-2.5 rounded-xl bg-blue-950/40 border border-blue-800/60 text-xs text-blue-300 flex items-center justify-between">
                <div>
                  <span class="text-[10px] text-slate-400 block">မူရင်းအလျား ➔ Recap စာညွှန်း</span>
                  <span id="videoDurationLabel" class="font-bold font-mono text-slate-200">00:00</span>
                  <span class="text-slate-400 font-mono"> ➔ </span>
                  <span id="targetDurationLabel" class="font-bold font-mono text-emerald-400">00:30 (+30s)</span>
                </div>
                <span class="text-[10px] bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-1 rounded-lg font-bold">
                  သဘာဝဇာတ်ကြောင်းပြန်
                </span>
              </div>
            </div>

            <!-- AI Engine Selector -->
            <div class="space-y-1.5 pt-1">
              <label class="text-xs font-bold text-slate-300 flex items-center justify-between">
                <span class="flex items-center gap-1.5">
                  <span>🤖</span>
                  <span>အသုံးပြုမည့် AI စနစ် ရွေးချယ်ပါ</span>
                </span>
                <span class="text-[10px] text-amber-400 font-semibold" id="activeEngineText">Active: ✨ Gemini 3.8 Flash</span>
              </label>
              <div class="grid grid-cols-2 gap-2 bg-[#070b14] p-1 rounded-xl border border-slate-800">
                <button
                  type="button"
                  id="engineGeminiBtn"
                  onclick="selectAiEngine('gemini')"
                  class="py-2 px-3 rounded-lg text-xs font-bold transition-all bg-amber-500 text-slate-950 flex items-center justify-center gap-1.5 shadow-md"
                >
                  <span>✨ Gemini 3.8 Flash</span>
                </button>
                <button
                  type="button"
                  id="engineGroqBtn"
                  onclick="selectAiEngine('groq')"
                  class="py-2 px-3 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white flex items-center justify-center gap-1.5"
                >
                  <span>⚡ Groq Engine</span>
                </button>
              </div>
            </div>

            <!-- Gemini API Key Input Field -->
            <div id="geminiKeyBox" class="pt-2 border-t border-slate-800/80 space-y-1.5">
              <div class="flex items-center justify-between">
                <label class="text-[11px] font-bold text-amber-400 flex items-center gap-1">
                  <span>✨</span>
                  <span>Gemini API Key (Google AI Studio)</span>
                </label>
                <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-[10px] text-amber-400 hover:underline">Key ရယူရန် (Free) ↗</a>
              </div>
              <input
                type="password"
                id="geminiApiKeyInput"
                placeholder="AIzaSy... (Gemini Key ထည့်ပါ)"
                class="w-full bg-[#070b14] border border-amber-500/70 rounded-xl p-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500 font-mono"
              />
              <p class="text-[10px] text-slate-500">Google AI Studio မှ အခမဲ့ ရယူနိုင်ပါသည်။</p>
            </div>

            <!-- Groq API Key Input Field -->
            <div id="groqKeyBox" class="pt-2 border-t border-slate-800/80 space-y-1.5">
              <div class="flex items-center justify-between">
                <label class="text-[11px] font-bold text-blue-400 flex items-center gap-1">
                  <span>⚡</span>
                  <span>Groq API Key (console.groq.com)</span>
                </label>
                <a href="https://console.groq.com/keys" target="_blank" class="text-[10px] text-blue-400 hover:underline">Key ရယူရန် (Free) ↗</a>
              </div>
              <input
                type="password"
                id="groqApiKeyInput"
                placeholder="gsk_... (Groq Key ထည့်ပါ)"
                class="w-full bg-[#070b14] border border-blue-500/40 rounded-xl p-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono"
              />
              <p class="text-[10px] text-slate-500">Groq Console မှ အခမဲ့ ရယူနိုင်ပါသည်။</p>
            </div>

            <!-- Add Timestamp Toggle Switch -->
            <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <div>
                <div class="text-xs font-bold text-slate-200">Add Time Stamp</div>
                <div class="text-[10px] text-slate-400">မိနစ်အလိုက် အချိန်မှတ် [00:00] ထည့်သွင်းမည်</div>
              </div>
              <div class="relative inline-block w-11 h-6 align-middle select-none">
                <input type="checkbox" id="timestampSwitch" class="switch-checkbox hidden" />
                <label for="timestampSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
                  <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
                </label>
              </div>
            </div>

            <!-- Transcribe Button -->
            <button
              id="startTranscriptBtn"
              onclick="handleTranscribeProcess()"
              class="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 active:scale-[0.99] text-white font-bold text-sm shadow-xl shadow-blue-600/30 flex items-center justify-center gap-2.5 transition-all disabled:opacity-50"
            >
              <span id="transSpinner" class="hidden animate-spin">🌀</span>
              <span id="transIcon" class="text-base">🎬</span>
              <span id="transBtnText">Movie Recap Script ထုတ်ယူမည် (+30s)</span>
            </button>
          </div>

        </div>

        <!-- Right: Output Script Result -->
        <div class="lg:col-span-7 space-y-4">
          <div class="bg-gradient-to-b from-slate-900/90 to-[#0d1527]/90 border border-slate-800/90 rounded-2xl p-5 space-y-3 shadow-2xl backdrop-blur-sm flex flex-col h-full min-h-[490px]">
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-slate-200">Movie Recap Script</span>
                <span class="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-bold">Pure Burmese Narration</span>
              </div>
              <div class="flex items-center gap-2">
                <span id="scriptWordCount" class="text-[11px] text-slate-400 font-mono">၀ စကားလုံး</span>
              </div>
            </div>

            <div class="relative flex-1">
              <textarea
                id="transcriptOutputText"
                placeholder="ဗီဒီယို တင်ပြီးခလုတ်နှိပ်လိုက်ပါက ဤနေရာတွင် အပိုစာသားနှင့် English လုံးဝမပါဘဲ Narrator တိုက်ရိုက်ဖတ်နိုင်သော သဘာဝကျသည့် Movie Recap ဇာတ်ညွှန်း အလွန်လျင်မြန်စွာ ထွက်ပေါ်လာမည် ဖြစ်ပါသည်..."
                class="w-full h-full min-h-[360px] bg-[#070b14] border border-slate-800/80 rounded-xl p-4 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 custom-scroll font-sans"
              ></textarea>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
              <button
                type="button"
                onclick="copyTranscriptScript()"
                class="w-full py-2.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-blue-300 font-bold text-xs border border-blue-500/30 flex items-center justify-center gap-2 transition-all active:scale-95 shadow-sm"
              >
                <span>📋</span>
                <span id="copyBtnText">Copy</span>
              </button>

              <button
                type="button"
                onclick="sendScriptToTts()"
                class="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:brightness-110 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-emerald-600/20"
              >
                <span>🎙</span>
                <span>TTS အသံထုတ်ခန်းသို့ ပို့မည်</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 2: TTS STUDIO (EXACT 13 VOICES)    -->
    <!-- ========================================== -->
    <div id="sectionTts" class="hidden space-y-6">

      <div class="p-4 rounded-2xl bg-gradient-to-r from-blue-500/10 via-indigo-500/5 to-transparent border border-blue-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 class="text-sm font-bold text-blue-300 flex items-center gap-1.5">
            <span>✨</span>
            <span>မြန်မာအသံ ကာရိုက်တာ (၁၃) မျိုးဖြင့် အသံဖန်တီးခန်း</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5 leading-relaxed">
            စာသားများကို ရိုက်ထည့်၍ဖြစ်စေ၊ Transcript မှ ရရှိလာသော ဇာတ်ညွှန်းကိုဖြစ်စေ MP3 အသံဖိုင် တိုက်ရိုက် ထုတ်ယူပါ
          </p>
        </div>
        <div id="activeVoicePill" class="text-xs font-bold text-blue-300 bg-blue-950/80 border border-blue-800/80 px-3 py-1.5 rounded-xl shrink-0">
          ရွေးထားသည်: Tayza
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Voice Selector -->
        <section class="lg:col-span-6 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 space-y-4 backdrop-blur-sm">
          <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider">အသံကဏ္ဍခွဲများ</span>
            <div class="flex gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-[11px]">
              <button onclick="filterVoices('all')" class="cat-pill px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold transition-all" data-cat="all">အားလုံး (13)</button>
              <button onclick="filterVoices('men')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="men">အမျိုးသား (7)</button>
              <button onclick="filterVoices('women')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="women">အမျိုးသမီး (6)</button>
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
                <span id="charCount" class="font-mono text-[11px] text-blue-400 font-semibold">၀ အက္ခရာ</span>
                <span>•</span>
                <button onclick="clearText()" class="text-rose-400 hover:underline">ဖျက်မည်</button>
              </div>
            </div>

            <textarea
              id="textInput"
              rows="6"
              placeholder="အသံဖန်တီးလိုသော မြန်မာစာသားများကို ရိုက်ထည့်ပါ..."
              class="w-full bg-[#030712] border border-slate-800 rounded-xl p-3.5 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-all resize-y"
            >သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>

            <div class="grid grid-cols-2 gap-4 pt-3 border-t border-slate-800/80">
              <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-slate-400">စကားပြောနှုန်း</span>
                  <span id="speedVal" class="text-blue-400 font-mono font-bold">မူရင်း</span>
                </div>
                <input id="speedRange" type="range" min="-20" max="20" step="2" value="0" class="w-full accent-blue-500" oninput="updateTuningLabels()" />
              </div>
              <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-slate-400">အသံအမြင့် (Pitch)</span>
                  <span id="pitchVal" class="text-blue-400 font-mono font-bold">မူရင်း</span>
                </div>
                <input id="pitchRange" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-blue-500" oninput="updateTuningLabels()" />
              </div>
            </div>

            <button
              id="generateBtn"
              type="button"
              onclick="handleGenerateVoice()"
              class="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 active:scale-[0.99] text-white font-bold text-sm shadow-xl shadow-blue-500/20 flex items-center justify-center gap-2.5 transition-all"
            >
              <span id="genSpinner" class="hidden animate-spin">🌀</span>
              <span id="genText">🎙 အသံဖန်တီးမည် (Generate Speech)</span>
            </button>
          </div>

          <!-- Audio Player Section -->
          <div id="playerSection" class="hidden bg-gradient-to-b from-slate-900 to-slate-950 border border-blue-500/40 rounded-2xl p-5 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="playerVoiceTitle" class="text-xs font-bold text-blue-300">အသံဖိုင် အဆင်သင့်ဖြစ်ပါပြီ</span>
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
    function switchMainTab(tab) {
      const ttsSec = document.getElementById("sectionTts");
      const transSec = document.getElementById("sectionTranscript");
      const ttsBtn = document.getElementById("tabTtsBtn");
      const transBtn = document.getElementById("tabTranscriptBtn");

      if (tab === "transcript") {
        ttsSec.classList.add("hidden");
        transSec.classList.remove("hidden");
        transBtn.className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold transition-all flex items-center gap-1.5";
        ttsBtn.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
      } else {
        transSec.classList.add("hidden");
        ttsSec.classList.remove("hidden");
        ttsBtn.className = "px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold transition-all flex items-center gap-1.5";
        transBtn.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
      }
    }

    function showToast(msg, type = "info") {
      const container = document.getElementById("toastContainer");
      const toast = document.createElement("div");
      toast.className = `px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold flex items-center gap-2 transition-all transform duration-300 translate-y-2 opacity-0 pointer-events-auto border ${
        type === 'error' ? 'bg-rose-950 border-rose-800 text-rose-200' :
        type === 'success' ? 'bg-emerald-950 border-emerald-800 text-emerald-200' :
        'bg-slate-900 border-slate-700 text-slate-200'
      }`;
      toast.innerHTML = `<span>${type === 'error' ? '⚠' : type === 'success' ? '✓' : 'ℹ'}</span><span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => toast.classList.remove('translate-y-2', 'opacity-0'), 20);
      setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    // ==========================================
    // AI ENGINE SELECTION & DUAL API KEYS
    // ==========================================
    let currentEngine = localStorage.getItem("active_ai_engine") || "gemini";

    function selectAiEngine(engine) {
      currentEngine = engine;
      localStorage.setItem("active_ai_engine", engine);

      const groqBtn = document.getElementById("engineGroqBtn");
      const geminiBtn = document.getElementById("engineGeminiBtn");
      const text = document.getElementById("activeEngineText");
      const groqInput = document.getElementById("groqApiKeyInput");
      const geminiInput = document.getElementById("geminiApiKeyInput");

      if (engine === "groq") {
        groqBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all bg-blue-600 text-white flex items-center justify-center gap-1.5 shadow-md";
        geminiBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white flex items-center justify-center gap-1.5";
        text.innerText = "Active: ⚡ Groq Engine";
        text.className = "text-[10px] text-blue-400 font-semibold";
        groqInput.classList.add("border-blue-500/70", "ring-1", "ring-blue-500/40");
        geminiInput.classList.remove("border-amber-500/70", "ring-1", "ring-amber-500/40");
      } else {
        geminiBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all bg-amber-500 text-slate-950 flex items-center justify-center gap-1.5 shadow-md";
        groqBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white flex items-center justify-center gap-1.5";
        text.innerText = "Active: ✨ Gemini 3.8 Flash";
        text.className = "text-[10px] text-amber-400 font-semibold";
        geminiInput.classList.add("border-amber-500/70", "ring-1", "ring-amber-500/40");
        groqInput.classList.remove("border-blue-500/70", "ring-1", "ring-blue-500/40");
      }
    }

    const savedGroqKey = localStorage.getItem("groq_api_key") || "";
    if (savedGroqKey) {
      document.getElementById("groqApiKeyInput").value = savedGroqKey;
    }

    const savedGeminiKey = localStorage.getItem("gemini_api_key") || "";
    if (savedGeminiKey) {
      document.getElementById("geminiApiKeyInput").value = savedGeminiKey;
    }

    document.getElementById("groqApiKeyInput").addEventListener("input", (e) => {
      localStorage.setItem("groq_api_key", e.target.value.trim());
    });

    document.getElementById("geminiApiKeyInput").addEventListener("input", (e) => {
      localStorage.setItem("gemini_api_key", e.target.value.trim());
    });

    // ==========================================
    // 200MB AUDIO EXTRACTOR & MEDIA HANDLER
    // ==========================================
    let currentUploadedFile = null;
    let videoDurationSeconds = 0;

    const fileInputEl = document.getElementById("videoFileInput");
    fileInputEl.addEventListener("change", function(e) {
      const file = this.files && this.files[0];
      if (!file) return;

      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      
      if (file.size > 200 * 1024 * 1024) {
        showToast(`ဖိုင်အရွယ်အစား ${sizeMB}MB ဖြစ်နေပါသည်။ အများဆုံး 200MB အထိသာ ခွင့်ပြုထားပါသည်`, "error");
        this.value = "";
        return;
      }

      currentUploadedFile = file;

      document.getElementById("uploadPromptText").innerText = `✓ ${file.name}`;
      document.getElementById("fileBadgeStatus").classList.remove("hidden");
      document.getElementById("videoFileNameLabel").innerText = file.name;
      document.getElementById("videoFileSizeLabel").innerText = `${sizeMB} MB`;

      const previewCard = document.getElementById("videoPreviewBox");
      const dropzoneLabel = document.getElementById("uploadDropzoneLabel");
      const videoEl = document.getElementById("previewVideoEl");
      const audioContainer = document.getElementById("audioPreviewContainer");
      const audioEl = document.getElementById("previewAudioEl");

      previewCard.classList.remove("hidden");
      dropzoneLabel.classList.add("hidden");

      const objectUrl = URL.createObjectURL(file);

      if (file.type.startsWith("audio/")) {
        videoEl.classList.add("hidden");
        audioContainer.classList.remove("hidden");
        audioEl.src = objectUrl;
        audioEl.onloadedmetadata = () => {
          videoDurationSeconds = Math.round(audioEl.duration) || 60;
          updateDurationBadges(videoDurationSeconds);
        };
      } else {
        audioContainer.classList.add("hidden");
        videoEl.classList.remove("hidden");
        videoEl.src = objectUrl;
        videoEl.muted = true;
        videoEl.load();

        videoEl.onloadedmetadata = () => {
          videoDurationSeconds = Math.round(videoEl.duration) || 60;
          updateDurationBadges(videoDurationSeconds);
          try {
            videoEl.currentTime = 0.05;
          } catch(err) {}
        };
      }

      setTimeout(() => {
        if (!videoDurationSeconds) {
          videoDurationSeconds = 60;
          updateDurationBadges(videoDurationSeconds);
        }
      }, 1500);

      showToast(`ဖိုင်တင်ခြင်း အောင်မြင်ပါသည် (${sizeMB} MB)`, "success");
    });

    function updateDurationBadges(durSecs) {
      const mins = Math.floor(durSecs / 60);
      const secs = durSecs % 60;
      document.getElementById("videoDurationLabel").innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

      const targetSecs = durSecs + 30;
      const tMins = Math.floor(targetSecs / 60);
      const tSecs = targetSecs % 60;
      document.getElementById("targetDurationLabel").innerText = `${tMins.toString().padStart(2, '0')}:${tSecs.toString().padStart(2, '0')} (+30s)`;
    }

    async function prepareAudioForGroq(file, statusCallback) {
      if (file.type.startsWith("audio/") && file.size <= 24 * 1024 * 1024) {
        return file;
      }

      statusCallback("အဆင့် ၁/၃: 200MB ဗီဒီယိုဖိုင်မှ အသံဖိုင်ကို စက္ကန့်ပိုင်းအတွင်း သီးသန့် ထုတ်ယူနေပါသည်...");
      
      const arrayBuffer = await file.arrayBuffer();
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
      
      statusCallback("အဆင့် ၂/၃: Speech AI အတွက် အသံအရွယ်အစားကို ချုံ့ပေးနေပါသည်...");
      
      const targetRate = 16000;
      const offlineCtx = new OfflineAudioContext(1, Math.ceil(audioBuffer.duration * targetRate), targetRate);
      
      const source = offlineCtx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(offlineCtx.destination);
      source.start(0);
      
      const renderedBuffer = await offlineCtx.startRendering();
      const wavBlob = audioBufferToWav(renderedBuffer);
      return new File([wavBlob], "audio_extracted.wav", { type: "audio/wav" });
    }

    function audioBufferToWav(buffer) {
      const numOfChan = 1;
      const length = buffer.length * 2;
      const outBuffer = new ArrayBuffer(44 + length);
      const view = new DataView(outBuffer);
      let pos = 0;

      function setUint16(data) { view.setUint16(pos, data, true); pos += 2; }
      function setUint32(data) { view.setUint32(pos, data, true); pos += 4; }

      setUint32(0x46464952);
      setUint32(36 + length);
      setUint32(0x45564157);
      setUint32(0x20746d66);
      setUint16(1);
      setUint16(numOfChan);
      setUint32(buffer.sampleRate);
      setUint32(buffer.sampleRate * 2);
      setUint16(2);
      setUint16(16);
      setUint32(0x61746164);
      setUint32(length);

      const channelData = buffer.getChannelData(0);
      for (let i = 0; i < channelData.length; i++) {
        let sample = Math.max(-1, Math.min(1, channelData[i]));
        view.setInt16(pos, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        pos += 2;
      }

      return new Blob([view], { type: "audio/wav" });
    }

    // ==========================================
    // RIGOROUS SCRIPT SANITIZER (NO ENGLISH, NO HEADERS, NO CHECKLISTS)
    // ==========================================
    function sanitizeMovieRecapScript(raw) {
      if (!raw) return "";

      let cleaned = raw
        .replace(/\*\s*\*(?:Intro|Middle|Conflict|Climax|End|Resolution|Plot|Beginning)(?:\/[A-Za-z]+)?\s*:\s*\*/gi, '')
        .replace(/\*(?:Intro|Middle|Conflict|Climax|End|Resolution|Plot|Beginning)(?:\/[A-Za-z]+)?\s*:\*/gi, '')
        .replace(/(?:^|\n)\s*(?:Intro|Middle|Conflict|Climax|End|Resolution|Plot|Beginning)\s*:\s*/gi, '\n');

      const lines = cleaned.split('\n');
      const filteredLines = [];

      for (let line of lines) {
        const trimmed = line.trim();

        if (/^\*\s*(?:No English|No "Note|No timestamps|Accurate pronouns|Natural flow|Gender neutral|Longer than)/i.test(trimmed)) continue;
        if (/^(?:No English|No "Note|No timestamps|Accurate pronouns|Natural flow|Gender neutral|Longer than)/i.test(trimmed)) continue;
        if (/^Famous Myanmar Movie Recap Creator/i.test(trimmed)) continue;
        if (/^A detailed plot summary and transcription/i.test(trimmed)) continue;
        if (/^\*\s*Accurate pronouns/i.test(trimmed)) continue;
        if (/^\*\s*Gender-neutral/i.test(trimmed)) continue;
        if (/^\*\s*Natural Movie Recap/i.test(trimmed)) continue;
        if (/^\*\s*Complete story/i.test(trimmed)) continue;
        if (/^\*\s*Clean script only/i.test(trimmed)) continue;
        if (/^\(Note:.*?\)$/i.test(trimmed)) continue;
        if (/^\[Note:.*?\]$/i.test(trimmed)) continue;

        const burmeseChars = trimmed.match(/[\u1000-\u109F]/g);
        const englishChars = trimmed.match(/[a-zA-Z]/g);

        if (!burmeseChars && englishChars && englishChars.length > 5) {
          continue;
        }

        line = line.replace(/^\s*[\*\-]\s+/, '');
        filteredLines.push(line);
      }

      cleaned = filteredLines.join('\n').trim();
      cleaned = cleaned.replace(/(.{4,80}?)\s*(?:\1\s*){2,}/gu, '$1');
      cleaned = cleaned.replace(/\n{3,}/g, '\n\n').trim();

      return cleaned;
    }

    // Dynamic Groq Translation
    async function callGroqTranslation(apiKey, systemPrompt, userContent) {
      const priority = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
      ];

      let lastError = null;

      for (const modelName of priority) {
        try {
          const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${apiKey}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: modelName,
              messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userContent }
              ],
              temperature: 0.25,
              max_tokens: 2048
            })
          });

          if (res.ok) {
            const data = await res.json();
            const content = data.choices?.[0]?.message?.content || "";
            if (content) return sanitizeMovieRecapScript(content);
          } else {
            const errJson = await res.json().catch(() => ({}));
            lastError = errJson.error?.message || `Model ${modelName} status ${res.status}`;
          }
        } catch (e) {
          lastError = e.message;
        }
      }

      throw new Error(lastError || "Groq Translation မအောင်မြင်ပါ");
    }

    // Official Google Gemini Interactions & Modern GenerateContent Engine
    async function callGemini38Flash(apiKey, systemPrompt, userContent) {
      let lastErr = null;

      // 1. Try Google Gemini's Modern Interactions API (Official standard for gemini-3.8-flash)
      try {
        const res = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
          method: "POST",
          headers: {
            "x-goog-api-key": apiKey,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "gemini-3.8-flash",
            system_instruction: systemPrompt,
            input: userContent
          })
        });

        if (res.ok) {
          const data = await res.json();
          const text = data.output_text || data.output || (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text);
          if (text) return sanitizeMovieRecapScript(text);
        } else {
          const errJson = await res.json().catch(() => ({}));
          lastErr = errJson.error?.message || `Interactions API Status ${res.status}`;
        }
      } catch (e) {
        lastErr = e.message;
      }

      // 2. Direct Fallback to gemini-3.8-flash generateContent endpoint with x-goog-api-key
      const modernModels = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-pro"];

      for (const m of modernModels) {
        try {
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent`, {
            method: "POST",
            headers: {
              "x-goog-api-key": apiKey,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              contents: [{
                role: "user",
                parts: [
                  { text: `${systemPrompt}\n\n[INPUT STORY TO NARRATE]:\n${userContent}` }
                ]
              }],
              generationConfig: {
                maxOutputTokens: 2500
              }
            })
          });

          if (res.ok) {
            const data = await res.json();
            const text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
            if (text) return sanitizeMovieRecapScript(text);
          } else {
            const errJson = await res.json().catch(() => ({}));
            lastErr = errJson.error?.message || `Model ${m} status ${res.status}`;
          }
        } catch (e) {
          lastErr = e.message;
        }
      }

      throw new Error(lastErr || "Gemini 3.8 Flash ချိတ်ဆက်မှု မအောင်မြင်ပါ");
    }

    async function handleTranscribeProcess() {
      if (!currentUploadedFile) {
        showToast("ကျေးဇူးပြု၍ Video / Audio ဖိုင် အရင်ရွေးချယ်ပေးပါ", "error");
        return;
      }

      const groqKey = document.getElementById("groqApiKeyInput").value.trim().replace(/[\s\r\n\t]/g, '');
      const geminiKey = document.getElementById("geminiApiKeyInput").value.trim().replace(/[\s\r\n\t]/g, '');

      if (currentEngine === "gemini") {
        if (!geminiKey) {
          showToast("Gemini API Key ကို ထည့်သွင်းပေးပါ", "error");
          document.getElementById("geminiApiKeyInput").focus();
          return;
        }
      } else {
        if (!groqKey) {
          showToast("Groq API Key ကို ထည့်သွင်းပေးပါ", "error");
          document.getElementById("groqApiKeyInput").focus();
          return;
        }
      }

      const btn = document.getElementById("startTranscriptBtn");
      const spinner = document.getElementById("transSpinner");
      const transIcon = document.getElementById("transIcon");
      const btnText = document.getElementById("transBtnText");
      const outputText = document.getElementById("transcriptOutputText");
      const includeTimestamps = document.getElementById("timestampSwitch").checked;

      btn.disabled = true;
      spinner.classList.remove("hidden");
      transIcon.classList.add("hidden");
      btnText.innerText = "ဖိုင်မှ အသံဖတ်ယူနေပါသည်...";

      try {
        let audioToSend = currentUploadedFile;
        if (currentUploadedFile.size > 24 * 1024 * 1024 || !currentUploadedFile.type.startsWith("audio/")) {
          audioToSend = await prepareAudioForGroq(currentUploadedFile, (msg) => {
            outputText.value = msg;
          });
        }

        const baseSecs = videoDurationSeconds || 60;
        const targetSecs = baseSecs + 30;

        const systemPrompt = `
သင်သည် နာမည်ကြီး မြန်မာ Movie Recap (ရုပ်ရှင်ဇာတ်ကြောင်းပြန်) အစီအစဉ် ဖန်တီးသူ ဖြစ်သည်။
ပေးထားသော ဗီဒီယိုပါ ဇာတ်လမ်းအကြောင်းအရာနှင့် စကားပြောများကို အခြေခံ၍ လူတိုင်းနားလည်လွယ်ပြီး ဆွဲဆောင်မှုရှိသော မြန်မာစကားပြော Movie Recap Voiceover ဇာတ်ညွှန်းကို ရေးသားပေးရမည်။

အောက်ပါ စည်းမျဉ်းများကို မပျက်မကွက် တိကျစွာ လိုက်နာပါ:

၁။ 【နာမ်စားနှင့် လူပုဂ္ဂိုလ် အသုံးအနှုန်းများ တိကျမှန်ကန်ရမည်】
- နိုင်ငံခြားစကားလုံးများကို အဓိပ္ပာယ်မဲ့ တိုက်ရိုက်ပြန်ဆိုခြင်း (Literal Translation) လုံးဝမပြုလုပ်ရ။
- ဇာတ်လမ်းထဲတွင် တွေ့ရသည့်အတိုင်း သဘာဝကျသော မြန်မာနာမ်စားများကိုသာ သုံးပါ:
  * Maid / Servant / အိမ်အကူဝတ်စုံဝတ်ထားသူ -> "အိမ်ဖော်မလေး" သို့မဟုတ် "အိမ်အကူကောင်မလေး" (★ "နို့တိုက်မ" ဟု လုံးဝမသုံးရ)
  * Dog / Pet -> "ခွေးလေး"
  * Father / Old man -> "အဖေကြီး" / "လူကြီး"
  * Son / Boy -> "သားဖြစ်သူ" / "ကောင်လေး"
  * Daughter-in-law -> "ချွေးမ"
  * Boss / Landlord -> "အိမ်ရှင်" / "သူဌေး"

၂။ 【ကျား/မ မရွေး ဖတ်နိုင်သော Voiceover လေသံ】
- "ကျွန်တော်" (ကျား) သို့မဟုတ် "ကျွန်မ" (မ) ဟူသော စကားလုံးများ မသုံးရ။ "ခင်ဗျာ"၊ "ရှင်" မသုံးရ။
- မည်သည့် Voiceover အနုပညာရှင်မဆို သဘာဝကျကျ အသံထွက်ဖတ်နိုင်သော ဇာတ်ကြောင်းပြောဟန် ဖြစ်ရမည်။

၃။ 【သဘာဝကျသော Movie Recap စကားပြောဟန်】
- စာအုပ်ဖတ်သလို မဟုတ်ဘဲ ဗီဒီယိုကို ကိုယ်တိုင် အစအဆုံး ကြည့်ပြီး မိတ်ဆွေတစ်ယောက်ကို ပြန်ပြောပြနေသလို ဇာတ်လမ်းကို စီးမျောစွာ ရေးသားပါ။
- သဘာဝစကားဆက်များ သုံးပါ: "ဒီနေ့ ဇာတ်လမ်းလေးမှာတော့...", "ကောင်မလေးက...", "အဲဒီအချိန်မှာပဲ...", "မထင်မှတ်ထားဘဲ...", "တကယ်တော့ ဖြစ်ပျက်သွားတာက...", "အခြေအနေတွေက ပိုဆိုးသွားပြီးတော့...", "နောက်ဆုံးမှာတော့...".

၄။ 【အပိုစာသား လုံးဝမပါရ (ZERO ENGLISH)】
- အင်္ဂလိပ်စာလုံး လုံးဝမပါရ။
- "*Intro:*", "*Middle:*", "*Conflict:*", "*Climax/End:*" စသည့် ခေါင်းစဉ်များ၊ "No English? Yes" စသည့် စာတန်းများ လုံးဝမထည့်ရ။
- အစမှ အဆုံးထိ မြန်မာစကားပြော စာပိုဒ်စစ်စစ်ကိုသာ ထုတ်ပေးရမည်။

၅။ 【အချိန်မှတ် စည်းမျဉ်း】
- ${includeTimestamps ? "အချိန်မှတ် များကို [00:00], [00:30] ပုံစံဖြင့် ဝါကျအလိုက် ဆက်လက် ထည့်သွင်းပေးပါ။" : "အချိန်မှတ် များကို လုံးဝ မထည့်ပါနှင့်။ သဘာဝကျသော စာပိုဒ်များဖြင့်သာ ရေးပေးပါ။"}

အထက်ပါ စည်းမျဉ်းအတိုင်း သန့်ရှင်းသော မြန်မာ Movie Recap Script စစ်စစ်ကိုသာ ထုတ်ပေးပါ:
        `.trim();

        let finalScript = "";

        // Fast & Reliable Audio Perception:
        // Use Groq Whisper (if groq key provided) for 2-second crystal-clear transcription
        let understoodText = "";
        if (groqKey) {
          outputText.value = "Whisper AI ဖြင့် မည်သည့်ဘာသာစကားဖြင့် ပြောထားသည်ကို စက္ကန့်ပိုင်းအတွင်း ဖတ်ရှုနေပါသည်...";
          btnText.innerText = "စကားလုံးများ ဖတ်နေပါသည်...";

          const formData = new FormData();
          formData.append("file", audioToSend);
          formData.append("model", "whisper-large-v3");
          formData.append("response_format", "verbose_json");

          let whisperRes = await fetch("https://api.groq.com/openai/v1/audio/translations", {
            method: "POST",
            headers: { "Authorization": `Bearer ${groqKey}` },
            body: formData
          });

          if (!whisperRes.ok) {
            whisperRes = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
              method: "POST",
              headers: { "Authorization": `Bearer ${groqKey}` },
              body: formData
            });
          }

          if (whisperRes.ok) {
            const whisperData = await whisperRes.json();
            understoodText = whisperData.text || "";
            if (includeTimestamps && whisperData.segments) {
              understoodText = whisperData.segments.map(s => {
                const startM = Math.floor(s.start / 60).toString().padStart(2, '0');
                const startS = Math.floor(s.start % 60).toString().padStart(2, '0');
                return `[${startM}:${startS}] ${s.text}`;
              }).join("\n");
            }
          }
        }

        if (currentEngine === "gemini") {
          btnText.innerText = "Gemini 3.8 Flash ဖြင့် ဇာတ်ညွှန်း ရေးနေပါသည်...";
          outputText.value = "Gemini 3.8 Flash AI ဖြင့် Movie Recap အသံထွက် ဇာတ်ညွှန်းကို ရေးသားနေပါသည်...";

          if (!understoodText) {
            // If only Gemini key exists, send audio directly
            const reader = new FileReader();
            const base64Audio = await new Promise((resolve) => {
              reader.onloadend = () => resolve(reader.result.split(',')[1]);
              reader.readAsDataURL(audioToSend);
            });

            const res = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent", {
              method: "POST",
              headers: {
                "x-goog-api-key": geminiKey,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                contents: [{
                  role: "user",
                  parts: [
                    { text: systemPrompt },
                    { inlineData: { mimeType: "audio/wav", data: base64Audio } }
                  ]
                }]
              })
            });

            if (res.ok) {
              const data = await res.json();
              finalScript = sanitizeMovieRecapScript(data.candidates?.[0]?.content?.parts?.[0]?.text || "");
            } else {
              const errData = await res.json().catch(() => ({}));
              throw new Error(errData.error?.message || "Gemini 3.8 Flash ချိတ်ဆက်မှု မအောင်မြင်ပါ");
            }
          } else {
            // Ultra-fast text narration with Gemini 3.8 Flash
            finalScript = await callGemini38Flash(geminiKey, systemPrompt, understoodText);
          }

        } else {
          // Groq LLM
          btnText.innerText = "Groq AI ဖြင့် ဇာတ်ညွှန်း ရေးနေပါသည်...";
          outputText.value = "Groq AI ဖြင့် သန့်ရှင်းသော မြန်မာဇာတ်ညွှန်း အချောသပ် ရေးသားနေပါသည်...";
          finalScript = await callGroqTranslation(groqKey, systemPrompt, understoodText);
        }

        if (finalScript) {
          outputText.value = finalScript;
          const words = finalScript.split(/\s+/).length;
          document.getElementById("scriptWordCount").innerText = `${words} စကားလုံး`;
          showToast("Movie Recap စတိုင်လ် မြန်မာဇာတ်ညွှန်း သန့်သန့် ထွက်ရှိပါပြီ", "success");
        } else {
          throw new Error("စာသား ရယူ၍ မရပါ");
        }

      } catch (err) {
        outputText.value = `ချို့ယွင်းချက် ဖြစ်ပေါ်သွားပါသည်: ${err.message}`;
        showToast(err.message, "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        transIcon.classList.remove("hidden");
        btnText.innerText = "Movie Recap Script ထုတ်ယူမည် (+30s)";
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
        btnText.innerText = "✓ Copied!";
        setTimeout(() => btnText.innerText = "Copy", 2000);
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
    // EXACT 13 CHARACTER VOICES CATALOG
    // ==========================================
    const PERSONAS = [
      {
        id: "nilar",
        name: "Nilar",
        gender: "women",
        icon: "🌸",
        badge: "အမျိုးသမီး",
        role: "ကြည်လင်ချိုသာသော ဇာတ်ကြောင်းပြောသံ (မူရင်းမြန်မာ)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
      },
      {
        id: "thiha",
        name: "Thiha",
        gender: "men",
        icon: "🎙",
        badge: "အမျိုးသား",
        role: "တည်ကြည်လေးနက်သော အမျိုးသားအသံ (မူရင်းမြန်မာ)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "phyo-ngwe-soe",
        name: "Phyo Ngwe Soe",
        gender: "men",
        icon: "⚡",
        badge: "အမျိုးသား",
        role: "စိတ်လှုပ်ရှားဖွယ် Action ဇာတ်လမ်းပြောဟန် (Florian)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "sinn-tiyar",
        name: "Sinn Tiyar",
        gender: "women",
        icon: "✨",
        badge: "အမျိုးသမီး",
        role: "ညင်သာအေးချမ်းသော စာပေ/ပုံပြင်ဖတ်ကြားသံ (Seraphina)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
      },
      {
        id: "chue-lay",
        name: "Chue Lay",
        gender: "women",
        icon: "👧",
        badge: "အမျိုးသမီး",
        role: "ချိုသာကြည်လင် ခေတ်မီဆန်းသစ်သော အမျိုးသမီးသံ (Ava)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
      },
      {
        id: "aung-ye-linn",
        name: "Aung Ye' Linn",
        gender: "men",
        icon: "🧑",
        badge: "အမျိုးသား",
        role: "နွေးထွေးတည်ငြိမ်သော ဇာတ်ကြောင်းပြောဟန် (Andrew)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "n-kai-yar",
        name: "N Kai Yar",
        gender: "women",
        icon: "🎀",
        badge: "အမျိုးသမီး",
        role: "နုပျိုသွက်လက်သော အသံဟန် (Emma)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
      },
      {
        id: "tayza",
        name: "Tayza",
        gender: "men",
        icon: "🎬",
        badge: "အမျိုးသား",
        role: "ရင့်ကျက်ပြတ်သားသော နာမည်ကြီး Movie Recap အသံ (Brian)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "nay-win",
        name: "Nay Win",
        gender: "men",
        icon: "🕺",
        badge: "အမျိုးသား",
        role: "လန်းဆန်းတက်ကြွသော လူငယ်စကားပြောဟန် (Remy)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "eaindra-bo",
        name: "Eaindra Bo",
        gender: "women",
        icon: "👑",
        badge: "အမျိုးသမီး",
        role: "ပရော်ဖက်ရှင်နယ် တင်ဆက်သူပုံစံ အမျိုးသမီးသံ (Vivienne)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
      },
      {
        id: "bunny-phyoe",
        name: "Bunny Phyoe",
        gender: "men",
        icon: "🎧",
        badge: "အမျိုးသား",
        role: "နက်ရှိုင်းစွဲမက်ဖွယ် ဩဇာပြည့်ဝသောအသံ (Giuseppe)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "ji-chaung-wook",
        name: "Ji Chaung Wook",
        gender: "men",
        icon: "🇰🇷",
        badge: "အမျိုးသား",
        role: "နူးညံ့သိမ်မွေ့သော စီးရီးဇာတ်လမ်းပြောသံ (Hyunsu)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
      },
      {
        id: "aye-thidar",
        name: "Aye Thidar",
        gender: "women",
        icon: "🌺",
        badge: "အမျိုးသမီး",
        role: "တက်ကြွပျော်ရွှင်ဖွယ် ခေတ်မီအမျိုးသမီးသံ (Thalita)",
        sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
      }
    ];

    let selectedId = "tayza";
    let playingPreviewId = null;
    let generatedBlob = null;

    const previewAudioEl = document.getElementById("previewAudio");
    const mainAudioEl = document.getElementById("mainAudio");
    const textInputEl = document.getElementById("textInput");

    function renderVoiceCards(category = "all") {
      const listContainer = document.getElementById("voiceCardsList");
      listContainer.innerHTML = "";
      const filtered = category === "all" ? PERSONAS : PERSONAS.filter(p => p.gender === category);

      filtered.forEach(p => {
        const isSelected = p.id === selectedId;
        const isPreviewing = p.id === playingPreviewId;

        const card = document.createElement("div");
        card.className = `p-3 rounded-xl border transition-all flex items-center justify-between gap-2.5 cursor-pointer ${
          isSelected 
            ? "bg-blue-500/10 border-blue-500 ring-1 ring-blue-500/50 shadow-lg shadow-blue-500/10" 
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
                  p.gender === 'men' ? 'bg-blue-950 text-blue-300 border border-blue-800/80' :
                  'bg-pink-950 text-pink-300 border border-pink-800/80'
                }">
                  ${p.badge}
                </span>
                ${isSelected ? '<span class="text-[9px] text-blue-400 font-bold ml-1">✓ ရွေးထားသည်</span>' : ''}
              </div>
              <p class="text-[11px] text-slate-400 truncate mt-0.5">${p.role}</p>
            </div>
          </div>

          <button
            type="button"
            onclick="togglePreview('${p.id}', event)"
            class="px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 flex items-center gap-1 transition-all ${
              isPreviewing ? 'bg-blue-600 text-white animate-pulse' : 'bg-slate-800/90 hover:bg-blue-950/60 text-blue-300 border border-blue-500/30'
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
      const activeCat = document.querySelector(".cat-pill.bg-blue-600")?.dataset.cat || "all";
      renderVoiceCards(activeCat);
    }

    function filterVoices(cat) {
      document.querySelectorAll(".cat-pill").forEach(btn => {
        if (btn.dataset.cat === cat) {
          btn.className = "cat-pill px-2.5 py-1 rounded-lg bg-blue-600 text-white font-bold transition-all";
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
        renderVoiceCards(document.querySelector(".cat-pill.bg-blue-600")?.dataset.cat || "all");
        return;
      }

      playingPreviewId = id;
      renderVoiceCards(document.querySelector(".cat-pill.bg-blue-600")?.dataset.cat || "all");

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
      renderVoiceCards(document.querySelector(".cat-pill.bg-blue-600")?.dataset.cat || "all");
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ", "error");
    }

    previewAudioEl.onended = () => {
      playingPreviewId = null;
      renderVoiceCards(document.querySelector(".cat-pill.bg-blue-600")?.dataset.cat || "all");
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
        btnText.innerText = "🎙 အသံဖန်တီးမည် (Generate Speech)";
      }
    }

    function downloadMp3() {
      if (!generatedBlob) return;
      const persona = PERSONAS.find(p => p.id === selectedId);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(generatedBlob);
      a.download = `Recap_Go_${persona.name}_${Date.now()}.mp3`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("MP3 ဒေါင်းလုဒ် ဆွဲပြီးပါပြီ", "success");
    }

    renderVoiceCards("all");
    updateTuningLabels();
    selectAiEngine(currentEngine);
    document.getElementById("charCount").innerText = `${textInputEl.value.length} အက္ခရာ`;
  </script>
</body>
</html>
"""

# The Exact 13 Voices with Assigned Character Names and Gender Greetings
PERSONA_VOICES = [
    {
        "id": "nilar",
        "name": "Nilar",
        "gender": "women",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "thiha",
        "name": "Thiha",
        "gender": "men",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "phyo-ngwe-soe",
        "name": "Phyo Ngwe Soe",
        "gender": "men",
        "base_voice": "de-DE-FlorianMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "sinn-tiyar",
        "name": "Sinn Tiyar",
        "gender": "women",
        "base_voice": "de-DE-SeraphinaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "chue-lay",
        "name": "Chue Lay",
        "gender": "women",
        "base_voice": "en-US-AvaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "aung-ye-linn",
        "name": "Aung Ye' Linn",
        "gender": "men",
        "base_voice": "en-US-AndrewMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "n-kai-yar",
        "name": "N Kai Yar",
        "gender": "women",
        "base_voice": "en-US-EmmaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "tayza",
        "name": "Tayza",
        "gender": "men",
        "base_voice": "en-US-BrianMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "nay-win",
        "name": "Nay Win",
        "gender": "men",
        "base_voice": "fr-FR-RemyMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "eaindra-bo",
        "name": "Eaindra Bo",
        "gender": "women",
        "base_voice": "fr-FR-VivienneMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "bunny-phyoe",
        "name": "Bunny Phyoe",
        "gender": "men",
        "base_voice": "it-IT-GiuseppeMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "ji-chaung-wook",
        "name": "Ji Chaung Wook",
        "gender": "men",
        "base_voice": "ko-KR-HyunsuMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "aye-thidar",
        "name": "Aye Thidar",
        "gender": "women",
        "base_voice": "pt-BR-ThalitaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    }
]
PERSONA_DICT = {p["id"]: p for p in PERSONA_VOICES}

class GenerateTTSRequest(BaseModel):
    text: str
    persona_id: str = "tayza"
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
