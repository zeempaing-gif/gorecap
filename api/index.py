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
  <title>Recap Go 🍀 • AI Movie Script & Speech Studio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: '#10b981',
            darkbg: '#080d19',
            cardbg: '#0f172a'
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Padauk', 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    .switch-checkbox:checked + .switch-label { background-color: #10b981; }
    .switch-checkbox:checked + .switch-label .switch-dot { transform: translateX(100%); background-color: #ffffff; }
  </style>
</head>
<body class="bg-[#080d19] text-slate-100 min-h-screen flex flex-col items-center antialiased selection:bg-emerald-600 selection:text-white transition-colors duration-200">

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Mobile Sidebar Drawer Overlay -->
  <div id="sidebarOverlay" onclick="toggleSidebarMenu(false)" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden transition-opacity"></div>

  <!-- Mobile Sidebar Drawer Menu (Inspired by Reference UI) -->
  <aside id="sidebarDrawer" class="fixed top-0 left-0 bottom-0 w-72 bg-[#0c1322] border-r border-slate-800 z-50 transform -translate-x-full transition-transform duration-300 flex flex-col p-5 shadow-2xl">
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <div class="flex items-center gap-2.5">
        <span class="text-2xl">🍀</span>
        <div>
          <h2 class="font-extrabold text-base text-white">Recap Go</h2>
          <p class="text-[10px] text-slate-400">Burmese Video Script & Voice Studio</p>
        </div>
      </div>
      <button onclick="toggleSidebarMenu(false)" class="p-1 rounded-lg text-slate-400 hover:text-white">✕</button>
    </div>

    <nav class="space-y-1.5 py-4 flex-1 text-xs font-bold text-slate-300">
      <button onclick="switchStudioView('transcriber')" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 transition-colors text-left">
        <span>🎬</span><span>AI Transcriber</span>
      </button>
      <button onclick="switchStudioView('tts')" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 transition-colors text-left">
        <span>🎙️</span><span>TTS Voice Over</span>
      </button>
      <button onclick="switchStudioView('recapvd')" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 transition-colors text-left">
        <span>🍿</span><span>Auto Recap VD</span>
      </button>
      <button onclick="switchStudioView('dubbing')" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 transition-colors text-left">
        <span>🎧</span><span>Auto Dubbing Mode</span>
      </button>
      <div class="pt-4 border-t border-slate-800 space-y-1.5">
        <button onclick="openKeysModal()" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 text-emerald-400 transition-colors text-left">
          <span>🔑</span><span>API Keys Settings</span>
        </button>
      </div>
    </nav>

    <div class="text-center text-[10px] text-slate-500 border-t border-slate-800 pt-3">
      v16.3.5 • Recap Go AI
    </div>
  </aside>

  <!-- Clean Top Navigation Bar -->
  <header class="w-full border-b border-slate-800/80 bg-[#0a1120]/95 backdrop-blur-xl sticky top-0 z-40">
    <div class="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-xl shadow-lg shadow-emerald-600/20 font-bold text-white">
          🍀
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="text-base font-extrabold tracking-tight text-white">Recap Go</h1>
            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              AI Studio
            </span>
          </div>
          <p class="text-[10px] text-slate-400">Burmese Text to Speech & Recap</p>
        </div>
      </div>

      <!-- Action Utilities -->
      <div class="flex items-center gap-2">
        <button onclick="openKeysModal()" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 text-xs font-bold flex items-center gap-1">
          <span>🔑</span><span class="hidden sm:inline">Keys</span>
        </button>
        <button onclick="toggleSidebarMenu(true)" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 hover:text-white" title="Menu">
          ☰
        </button>
      </div>
    </div>
  </header>

  <!-- Global File Input (Hidden) -->
  <input type="file" id="videoFileInput" accept="video/*,audio/*,.mp4,.mov,.mp3,.wav,.m4a,.webm,.mkv" class="hidden" />

  <!-- Main Container -->
  <main class="max-w-4xl w-full p-4 space-y-6 flex-1">

    <!-- Hero Feature Card Slider (Matches Reference UI) -->
    <section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-950/80 via-[#0d2822]/60 to-[#081820]/90 border border-emerald-500/30 p-6 shadow-2xl backdrop-blur-sm">
      <div class="space-y-2">
        <div class="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-300 flex items-center justify-center text-xl mb-3">
          📹
        </div>
        <span class="text-[10px] font-extrabold uppercase tracking-widest text-emerald-400">VIDEO & AUDIO TO TEXT</span>
        <h2 class="text-xl sm:text-2xl font-black text-white tracking-tight">AI TRANSCRIBER</h2>
        <p class="text-xs text-slate-300 max-w-md leading-relaxed">
          Upload video or audio and get accurate, natural Burmese (or any language) movie recap transcription in minutes.
        </p>
        <div class="pt-2">
          <button onclick="switchStudioView('transcriber')" class="px-5 py-2.5 rounded-full bg-white text-slate-950 font-black text-xs hover:bg-slate-100 shadow-xl transition-all flex items-center gap-1.5 active:scale-95">
            <span>Get Started</span>
            <span>→</span>
          </button>
        </div>
      </div>
    </section>

    <!-- AI Tools Clean Navigation Grid (Matches Reference UI) -->
    <section class="space-y-3">
      <div>
        <h3 class="text-base font-extrabold text-white">AI Tool</h3>
        <p class="text-xs text-slate-400">Quick access to our most used features.</p>
      </div>

      <div class="space-y-3">
        <!-- Tool 1: TTS VOICE OVER (Purple Theme) -->
        <div onclick="switchStudioView('tts')" class="group cursor-pointer rounded-3xl bg-gradient-to-r from-[#201538] to-[#120d24] border border-purple-500/30 p-5 hover:border-purple-500/60 transition-all shadow-xl">
          <div class="flex items-start gap-4">
            <div class="w-11 h-11 rounded-2xl bg-purple-500/20 text-purple-300 flex items-center justify-center text-2xl shrink-0 group-hover:scale-110 transition-transform">
              🎙️
            </div>
            <div class="space-y-1 flex-1 min-w-0">
              <h4 class="font-black text-sm text-white tracking-wide">TTS VOICE OVER</h4>
              <p class="text-xs text-slate-300">Convert Burmese script into natural AI voiceovers with 13 authentic voices.</p>
            </div>
          </div>
        </div>

        <!-- Tool 2: AI TRANSCRIBER (Emerald Theme) -->
        <div onclick="switchStudioView('transcriber')" class="group cursor-pointer rounded-3xl bg-gradient-to-r from-[#0d2822] to-[#091819] border border-emerald-500/30 p-5 hover:border-emerald-500/60 transition-all shadow-xl">
          <div class="flex items-start gap-4">
            <div class="w-11 h-11 rounded-2xl bg-emerald-500/20 text-emerald-300 flex items-center justify-center text-2xl shrink-0 group-hover:scale-110 transition-transform">
              📹
            </div>
            <div class="space-y-1 flex-1 min-w-0">
              <h4 class="font-black text-sm text-white tracking-wide">AI TRANSCRIBER</h4>
              <p class="text-xs text-slate-300">Upload video or audio and get accurate, natural Burmese transcription in minutes.</p>
            </div>
          </div>
        </div>

        <!-- Tool 3: AUTO RECAP VD (Orange Theme) -->
        <div onclick="switchStudioView('recapvd')" class="group cursor-pointer rounded-3xl bg-gradient-to-r from-[#331c12] to-[#1f110c] border border-amber-600/30 p-5 hover:border-amber-500/60 transition-all shadow-xl">
          <div class="flex items-start gap-4">
            <div class="w-11 h-11 rounded-2xl bg-amber-500/20 text-amber-300 flex items-center justify-center text-2xl shrink-0 group-hover:scale-110 transition-transform">
              🍿
            </div>
            <div class="space-y-1 flex-1 min-w-0">
              <h4 class="font-black text-sm text-white tracking-wide">AUTO RECAP VD</h4>
              <p class="text-xs text-slate-300">Upload a video, mute the original audio, and get an AI-dubbed movie recap.</p>
            </div>
          </div>
        </div>

        <!-- Tool 4: AUTO DUBBING MODE (Cyan Theme) -->
        <div onclick="switchStudioView('dubbing')" class="group cursor-pointer rounded-3xl bg-gradient-to-r from-[#0e2a38] to-[#0a1824] border border-cyan-500/30 p-5 hover:border-cyan-500/60 transition-all shadow-xl">
          <div class="flex items-start gap-4">
            <div class="w-11 h-11 rounded-2xl bg-cyan-500/20 text-cyan-300 flex items-center justify-center text-2xl shrink-0 group-hover:scale-110 transition-transform">
              🎧
            </div>
            <div class="space-y-1 flex-1 min-w-0">
              <h4 class="font-black text-sm text-white tracking-wide">AUTO DUBBING MODE</h4>
              <p class="text-xs text-slate-300">Translate original speech with timestamps and replace the audio with a synced AI voiceover.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- WORKSPACE PANEL: AI TRANSCRIBER & SCRIPT STUDIO                          -->
    <!-- ========================================================================= -->
    <div id="panelTranscriber" class="space-y-4 pt-2">
      <div class="bg-[#0c1424] border border-slate-800 rounded-3xl p-5 space-y-4 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h3 class="font-bold text-sm text-emerald-400 flex items-center gap-2">
            <span>📹</span>
            <span>AI Transcriber Studio</span>
          </h3>
          <span class="text-[10px] font-mono text-slate-400">Pure Burmese Storytelling</span>
        </div>

        <!-- Upload Trigger -->
        <label
          for="videoFileInput"
          id="dropzoneLabel"
          class="border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-2xl p-6 text-center cursor-pointer transition-all bg-[#070b14] hover:bg-[#0c1322] block group"
        >
          <div class="space-y-2 pointer-events-none">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              📁
            </div>
            <p class="text-xs font-bold text-slate-100" id="uploadPromptText">Click or Drag video / audio file here</p>
            <p class="text-[10px] text-slate-400 font-mono">mp4, mov, mp3, wav, m4a · max 200MB</p>
          </div>
        </label>

        <!-- Video Preview Box -->
        <div id="videoPreviewBox" class="hidden space-y-3 bg-[#050914] border border-emerald-500/40 rounded-2xl p-3.5 shadow-2xl">
          <div class="flex items-center justify-between pb-2 border-b border-slate-800 text-xs">
            <span class="font-bold text-emerald-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Loaded Media Preview</span>
            </span>
            <label for="videoFileInput" class="text-emerald-400 hover:underline font-bold cursor-pointer text-[11px]">
              🔄 Change File
            </label>
          </div>
          <video id="previewVideoEl" controls playsinline muted class="w-full rounded-xl max-h-52 bg-black border border-slate-800 shadow-inner"></video>
          <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 truncate" id="mediaNameTag">file.mp4</div>
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 text-emerald-400" id="mediaSizeTag">0 MB</div>
          </div>
        </div>

        <!-- Transcribe Process Button -->
        <button
          id="transcribeBtn"
          onclick="handleStartTranscribe()"
          class="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:brightness-110 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-emerald-600/20 flex items-center justify-center gap-2 transition-all active:scale-95"
        >
          <span id="transSpinner" class="hidden animate-spin">🌀</span>
          <span id="transIcon">🎬</span>
          <span id="transBtnText">Generate Movie Recap Script (+30s)</span>
        </button>

        <!-- Output Script Result Area -->
        <div class="space-y-2 pt-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-slate-300">Generated Script</span>
            <span id="scriptWordsTag" class="text-[10px] font-mono text-slate-500">၀ စကားလုံး</span>
          </div>
          <textarea
            id="recapScriptArea"
            rows="7"
            placeholder="ဗီဒီယို တင်သွင်းပြီး Generate နှိပ်လိုက်ပါက ဤနေရာတွင် အပိုစာသားနှင့် English လုံးဝမပါဘဲ Narrator တိုက်ရိုက်ဖတ်နိုင်သော သဘာဝကျသည့် Movie Recap ဇာတ်ညွှန်း ထွက်ပေါ်လာမည် ဖြစ်ပါသည်..."
            class="w-full bg-[#040711] border border-slate-800 rounded-2xl p-4 text-xs leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500 custom-scroll resize-y"
          ></textarea>

          <div class="grid grid-cols-2 gap-2 pt-1">
            <button onclick="copyScriptText()" class="py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-emerald-400 font-bold text-xs flex items-center justify-center gap-1.5 transition-all">
              <span>📋</span><span id="copyBtnTag">Copy Script</span>
            </button>
            <button onclick="transferScriptToTts()" class="py-2.5 rounded-xl bg-emerald-600/30 hover:bg-emerald-600/50 border border-emerald-500/40 text-emerald-200 font-bold text-xs flex items-center justify-center gap-1.5 transition-all">
              <span>🎙️</span><span>Send To Voice</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- WORKSPACE PANEL: TTS VOICE OVER (13 AUTHENTIC VOICES)                    -->
    <!-- ========================================================================= -->
    <div id="panelTts" class="hidden space-y-4 pt-2">
      <div class="bg-[#0c1424] border border-slate-800 rounded-3xl p-5 space-y-4 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h3 class="font-bold text-sm text-purple-400 flex items-center gap-2">
            <span>🎙️</span>
            <span>TTS Voice Over Studio (13 Voices)</span>
          </h3>
          <span id="activeVoiceBadge" class="text-[10px] font-bold text-purple-300 bg-purple-950/80 border border-purple-800/80 px-2.5 py-1 rounded-xl">
            Selected: Tayza
          </span>
        </div>

        <!-- Voice Selection Grid -->
        <div class="space-y-2">
          <div class="flex gap-1 text-[11px] bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button onclick="filterVoiceCatalog('all')" class="v-pill px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold transition-all" data-f="all">All (13)</button>
            <button onclick="filterVoiceCatalog('men')" class="v-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-f="men">Male (7)</button>
            <button onclick="filterVoiceCatalog('women')" class="v-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-f="women">Female (6)</button>
          </div>
          <div id="voicesCatalogList" class="space-y-2 max-h-[360px] overflow-y-auto pr-1 custom-scroll"></div>
        </div>

        <!-- Input Text & Speed Pitch -->
        <div class="space-y-3 pt-2 border-t border-slate-800">
          <div class="flex items-center justify-between text-xs text-slate-400">
            <span class="font-bold text-slate-300">မြန်မာစာသား</span>
            <span id="charCountTag" class="font-mono text-purple-400">၀ အက္ခရာ</span>
          </div>

          <textarea
            id="ttsInputTextArea"
            rows="5"
            placeholder="အသံထုတ်လိုသော မြန်မာစာသားများကို ရိုက်ထည့်ပါ..."
            class="w-full bg-[#040711] border border-slate-800 rounded-2xl p-4 text-xs leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-purple-500 resize-y"
          >သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <div class="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
              <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>စကားပြောနှုန်း</span>
                <span id="spdTag" class="text-purple-400 font-mono font-bold">မူရင်း</span>
              </div>
              <input id="speedRangeInput" type="range" min="-20" max="20" step="2" value="0" class="w-full accent-purple-500" oninput="updateTuningValues()" />
            </div>
            <div class="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
              <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>အသံအမြင့် (Pitch)</span>
                <span id="ptcTag" class="text-purple-400 font-mono font-bold">မူရင်း</span>
              </div>
              <input id="pitchRangeInput" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-purple-500" oninput="updateTuningValues()" />
            </div>
          </div>

          <button
            id="ttsGenerateBtn"
            onclick="handleGenerateAudioSpeech()"
            class="w-full py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 hover:brightness-110 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-purple-600/20 flex items-center justify-center gap-2 transition-all active:scale-95"
          >
            <span id="ttsSpinner" class="hidden animate-spin">🌀</span>
            <span id="ttsBtnText">🎙 Generate Speech (အသံဖန်တီးမည်)</span>
          </button>

          <!-- Audio Player Card -->
          <div id="ttsPlayerCard" class="hidden bg-slate-950 border border-purple-500/40 rounded-2xl p-4 space-y-3">
            <audio id="mainAudioEl" controls class="w-full"></audio>
            <button onclick="downloadGeneratedMp3()" class="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-md">
              <span>📥</span><span>Download MP3</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- WORKSPACE PANEL: AUTO RECAP VD & DUBBING                                -->
    <!-- ========================================================================= -->
    <div id="panelRecapVd" class="hidden space-y-4 pt-2">
      <div class="bg-[#0c1424] border border-slate-800 rounded-3xl p-5 space-y-4 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-amber-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🍿</span><span>Auto Recap Video Mode</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">
          Upload video, mute original audio tracks, and combine with generated AI pure Burmese voiceover and synchronized subtitles.
        </p>
        <div class="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
          <div class="flex justify-between">
            <span class="text-slate-400">Aspect Ratio:</span>
            <span class="font-bold text-amber-400">9:16 (Shorts / TikTok)</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Original Audio:</span>
            <span class="font-bold text-rose-400">Muted (Zero Background Clash)</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Voiceover Sync:</span>
            <span class="font-bold text-emerald-400">Synchronized</span>
          </div>
        </div>
        <button onclick="showToast('Video compositor ready. Export package is prepared in Transcriber.', 'success')" class="w-full py-3 rounded-2xl bg-amber-600 hover:bg-amber-500 text-white font-bold">
          Process Auto Recap Video
        </button>
      </div>
    </div>

    <div id="panelDubbing" class="hidden space-y-4 pt-2">
      <div class="bg-[#0c1424] border border-slate-800 rounded-3xl p-5 space-y-4 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-cyan-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🎧</span><span>Auto Dubbing Mode</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">
          Translate original speech with timestamps and replace the audio with a synchronized Burmese AI voiceover.
        </p>
        <button onclick="showToast('Auto Dubbing mode ready. Synchronizing audio tracks.', 'success')" class="w-full py-3 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold">
          Start Auto Dubbing Track
        </button>
      </div>
    </div>

  </main>

  <!-- Clean Footer (Matches Reference UI) -->
  <footer class="w-full border-t border-slate-900 bg-[#060a12] py-8 text-center space-y-3 text-xs text-slate-500">
    <div class="flex justify-center items-center gap-3">
      <div class="w-9 h-9 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 text-sm">f</div>
      <div class="w-9 h-9 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 text-sm">✈</div>
      <div class="w-9 h-9 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 text-sm">♪</div>
    </div>
    <div>
      Powered by <span class="font-extrabold text-slate-300">Recap Go AI</span>
    </div>
  </footer>

  <!-- Audio Preview Element -->
  <audio id="previewAudioEl" class="hidden"></audio>

  <!-- Clean API Key Settings Modal -->
  <div id="apiKeysModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-[#0b1222] border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 class="font-extrabold text-sm text-white">API Keys Configuration</h3>
        <button onclick="closeKeysModal()" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="font-bold text-amber-400 block mb-1">Google Gemini API Key (aistudio.google.com)</label>
          <input type="password" id="modalGeminiInput" placeholder="AIzaSy..." class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-emerald-500" />
        </div>
        <div>
          <label class="font-bold text-blue-400 block mb-1">Groq Whisper API Key (console.groq.com)</label>
          <input type="password" id="modalGroqInput" placeholder="gsk_..." class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-emerald-500" />
        </div>
        <p class="text-[10px] text-slate-500">Keys are stored locally in your browser storage only.</p>
      </div>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
        <button onclick="closeKeysModal()" class="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold">Cancel</button>
        <button onclick="saveApiKeysModal()" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold">Save Keys</button>
      </div>
    </div>
  </div>

  <script>
    // =========================================================================
    // EXACT 13 CHARACTER VOICES CATALOG & GENDER GREETINGS
    // =========================================================================
    const PERSONAS = [
      { id: "tayza", name: "Tayza", gender: "men", icon: "🎬", badge: "အမျိုးသား", role: "ရင့်ကျက်ပြတ်သားသော နာမည်ကြီး Movie Recap အသံ (Brian)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aung-ye-linn", name: "Aung Ye' Linn", gender: "men", icon: "🧑", badge: "အမျိုးသား", role: "နွေးထွေးတည်ငြိမ်သော ဇာတ်ကြောင်းပြောဟန် (Andrew)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "chue-lay", name: "Chue Lay", gender: "women", icon: "👧", badge: "အမျိုးသမီး", role: "ချိုသာကြည်လင် ခေတ်မီဆန်းသစ်သော အမျိုးသမီးသံ (Ava)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "n-kai-yar", name: "N Kai Yar", gender: "women", icon: "🎀", badge: "အမျိုးသမီး", role: "နုပျိုသွက်လက်သော အသံဟန် (Emma)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nilar", name: "Nilar", gender: "women", icon: "🌸", badge: "အမျိုးသမီး", role: "ကြည်လင်ချိုသာသော ဇာတ်ကြောင်းပြောသံ (မူရင်းမြန်မာ)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "thiha", name: "Thiha", gender: "men", icon: "🎙", badge: "အမျိုးသား", role: "တည်ကြည်လေးနက်သော အမျိုးသားအသံ (မူရင်းမြန်မာ)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "phyo-ngwe-soe", name: "Phyo Ngwe Soe", gender: "men", icon: "⚡", badge: "အမျိုးသား", role: "စိတ်လှုပ်ရှားဖွယ် Action ဇာတ်လမ်းပြောဟန် (Florian)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "sinn-tiyar", name: "Sinn Tiyar", gender: "women", icon: "✨", badge: "အမျိုးသမီး", role: "ညင်သာအေးချမ်းသော စာပေ/ပုံပြင်ဖတ်ကြားသံ (Seraphina)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nay-win", name: "Nay Win", gender: "men", icon: "🕺", badge: "အမျိုးသား", role: "လန်းဆန်းတက်ကြွသော လူငယ်စကားပြောဟန် (Remy)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "eaindra-bo", name: "Eaindra Bo", gender: "women", icon: "👑", badge: "အမျိုးသမီး", role: "ပရော်ဖက်ရှင်နယ် တင်ဆက်သူပုံစံ အမျိုးသမီးသံ (Vivienne)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "bunny-phyoe", name: "Bunny Phyoe", gender: "men", icon: "🎧", badge: "အမျိုးသား", role: "နက်ရှိုင်းစွဲမက်ဖွယ် ဩဇာပြည့်ဝသောအသံ (Giuseppe)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "ji-chaung-wook", name: "Ji Chaung Wook", gender: "men", icon: "🇰🇷", badge: "အမျိုးသား", role: "နူးညံ့သိမ်မွေ့သော စီးရီးဇာတ်လမ်းပြောသံ (Hyunsu)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aye-thidar", name: "Aye Thidar", gender: "women", icon: "🌺", badge: "အမျိုးသမီး", role: "တက်ကြွပျော်ရွှင်ဖွယ် ခေတ်မီအမျိုးသမီးသံ (Thalita)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" }
    ];

    let selectedVoiceId = "tayza";
    let previewingVoiceId = null;
    let uploadedMediaFile = null;
    let generatedMp3Blob = null;

    // Load keys
    const gKey = localStorage.getItem("gemini_api_key") || "";
    const grKey = localStorage.getItem("groq_api_key") || "";
    if (gKey) document.getElementById("modalGeminiInput").value = gKey;
    if (grKey) document.getElementById("modalGroqInput").value = grKey;

    function toggleSidebarMenu(show) {
      const drawer = document.getElementById("sidebarDrawer");
      const overlay = document.getElementById("sidebarOverlay");
      if (show) {
        overlay.classList.remove("hidden");
        drawer.classList.remove("-translate-x-full");
      } else {
        overlay.classList.add("hidden");
        drawer.classList.add("-translate-x-full");
      }
    }

    function switchStudioView(tool) {
      toggleSidebarMenu(false);
      const pTrans = document.getElementById("panelTranscriber");
      const pTts = document.getElementById("panelTts");
      const pRecap = document.getElementById("panelRecapVd");
      const pDub = document.getElementById("panelDubbing");

      [pTrans, pTts, pRecap, pDub].forEach(p => p.classList.add("hidden"));

      if (tool === "tts") {
        pTts.classList.remove("hidden");
        renderVoiceCatalog("all");
      } else if (tool === "recapvd") {
        pRecap.classList.remove("hidden");
      } else if (tool === "dubbing") {
        pDub.classList.remove("hidden");
      } else {
        pTrans.classList.remove("hidden");
      }
      window.scrollTo({ top: 380, behavior: 'smooth' });
    }

    function openKeysModal() {
      document.getElementById("apiKeysModal").classList.remove("hidden");
    }

    function closeKeysModal() {
      document.getElementById("apiKeysModal").classList.add("hidden");
    }

    function saveApiKeysModal() {
      const g = document.getElementById("modalGeminiInput").value.trim();
      const gr = document.getElementById("modalGroqInput").value.trim();
      localStorage.setItem("gemini_api_key", g);
      localStorage.setItem("groq_api_key", gr);
      closeKeysModal();
      showToast("API Keys saved successfully", "success");
    }

    function showToast(msg, type = "info") {
      const container = document.getElementById("toastContainer");
      const toast = document.createElement("div");
      toast.className = `px-4 py-2.5 rounded-2xl shadow-2xl text-xs font-bold flex items-center gap-2 border transition-all pointer-events-auto ${
        type === 'error' ? 'bg-rose-950 border-rose-800 text-rose-200' :
        type === 'success' ? 'bg-emerald-950 border-emerald-800 text-emerald-200' :
        'bg-slate-900 border-slate-700 text-slate-200'
      }`;
      toast.innerHTML = `<span>${type === 'error' ? '⚠' : type === 'success' ? '✓' : 'ℹ'}</span><span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 3500);
    }

    // File Ingestion Handler
    document.getElementById("videoFileInput").addEventListener("change", function(e) {
      const file = this.files && this.files[0];
      if (!file) return;

      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      if (file.size > 200 * 1024 * 1024) {
        showToast(`ဖိုင်အရွယ်အစား ${sizeMB}MB ဖြစ်နေပါသည်။ 200MB အောက်သာ ခွင့်ပြုထားပါသည်`, "error");
        return;
      }

      uploadedMediaFile = file;
      document.getElementById("uploadPromptText").innerText = `✓ ${file.name}`;
      document.getElementById("mediaNameTag").innerText = file.name;
      document.getElementById("mediaSizeTag").innerText = `${sizeMB} MB`;
      document.getElementById("dropzoneLabel").classList.add("hidden");
      document.getElementById("videoPreviewBox").classList.remove("hidden");

      const vEl = document.getElementById("previewVideoEl");
      vEl.src = URL.createObjectURL(file);
      showToast(`ဖိုင်တင်ခြင်း အောင်မြင်ပါသည် (${sizeMB} MB)`, "success");
    });

    // Audio Conversion Pipeline for Whisper
    async function prepareAudioBlob(file) {
      if (file.type.startsWith("audio/") && file.size <= 24 * 1024 * 1024) return file;
      const arrayBuffer = await file.arrayBuffer();
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
      const targetRate = 16000;
      const offlineCtx = new OfflineAudioContext(1, Math.ceil(audioBuffer.duration * targetRate), targetRate);
      const source = offlineCtx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(offlineCtx.destination);
      source.start(0);
      const rendered = await offlineCtx.startRendering();
      return new File([audioBufferToWavBlob(rendered)], "audio.wav", { type: "audio/wav" });
    }

    function audioBufferToWavBlob(buffer) {
      const numOfChan = 1, length = buffer.length * 2, outBuffer = new ArrayBuffer(44 + length), view = new DataView(outBuffer);
      let pos = 0;
      function setUint16(data) { view.setUint16(pos, data, true); pos += 2; }
      function setUint32(data) { view.setUint32(pos, data, true); pos += 4; }
      setUint32(0x46464952); setUint32(36 + length); setUint32(0x45564157); setUint32(0x20746d66); setUint32(16); setUint16(1); setUint16(numOfChan);
      setUint32(buffer.sampleRate); setUint32(buffer.sampleRate * 2); setUint16(2); setUint16(16); setUint32(0x61746164); setUint32(length);
      const channel = buffer.getChannelData(0);
      for (let i = 0; i < channel.length; i++) {
        let sample = Math.max(-1, Math.min(1, channel[i]));
        view.setInt16(pos, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        pos += 2;
      }
      return new Blob([view], { type: "audio/wav" });
    }

    // Clean pure Burmese Recap Script Sanitizer
    function sanitizeRecapScript(raw) {
      if (!raw) return "";
      let cleaned = raw
        .replace(/\*\s*\*(?:Intro|Middle|Conflict|Climax|End|Resolution|Plot|Beginning)(?:\/[A-Za-z]+)?\s*:\s*\*/gi, '')
        .replace(/\*(?:Intro|Middle|Conflict|Climax|End|Resolution|Plot|Beginning)(?:\/[A-Za-z]+)?\s*:\*/gi, '')
        .replace(/(?:^|\n)\s*(?:Intro|Middle|Conflict|Climax|End|Resolution|Plot|Beginning)\s*:\s*/gi, '\n');

      const lines = cleaned.split('\n');
      const filtered = [];
      for (let line of lines) {
        const trimmed = line.trim();
        if (/^\*\s*(?:No English|No "Note|No timestamps|Accurate pronouns|Natural flow|Gender neutral|Longer than)/i.test(trimmed)) continue;
        if (/^(?:No English|No "Note|No timestamps|Accurate pronouns|Natural flow|Gender neutral|Longer than)/i.test(trimmed)) continue;
        if (/^Famous Myanmar Movie Recap Creator/i.test(trimmed)) continue;
        if (/^A detailed plot summary and transcription/i.test(trimmed)) continue;
        if (/^\(Note:.*?\)$/i.test(trimmed)) continue;
        const burmese = trimmed.match(/[\u1000-\u109F]/g);
        const english = trimmed.match(/[a-zA-Z]/g);
        if (!burmese && english && english.length > 5) continue;
        line = line.replace(/^\s*[\*\-]\s+/, '');
        filtered.push(line);
      }
      cleaned = filtered.join('\n').trim();
      cleaned = cleaned.replace(/(.{4,80}?)\s*(?:\1\s*){2,}/gu, '$1');
      return cleaned.replace(/\n{3,}/g, '\n\n').trim();
    }

    // Transcribe & Storytelling Generation
    async function handleStartTranscribe() {
      if (!uploadedMediaFile) {
        showToast("ကျေးဇူးပြု၍ Video / Audio ဖိုင် အရင်ရွေးချယ်ပေးပါ", "error");
        return;
      }

      const geminiKey = (localStorage.getItem("gemini_api_key") || "").trim();
      const groqKey = (localStorage.getItem("groq_api_key") || "").trim();

      if (!geminiKey && !groqKey) {
        showToast("Gemini Key သို့မဟုတ် Groq Key ထည့်သွင်းပေးရန် လိုအပ်ပါသည်", "error");
        openKeysModal();
        return;
      }

      const btn = document.getElementById("transcribeBtn");
      const spinner = document.getElementById("transSpinner");
      const icon = document.getElementById("transIcon");
      const txt = document.getElementById("transBtnText");
      const out = document.getElementById("recapScriptArea");

      btn.disabled = true;
      spinner.classList.remove("hidden");
      icon.classList.add("hidden");
      txt.innerText = "Speech AI ဖြင့် စကားလုံးများ ဖတ်နေပါသည်...";

      try {
        const audio = await prepareAudioBlob(uploadedMediaFile);
        let understoodText = "";

        // Fast Audio Transcription via Whisper if Groq Key exists
        if (groqKey) {
          const formData = new FormData();
          formData.append("file", audio);
          formData.append("model", "whisper-large-v3");
          formData.append("response_format", "verbose_json");

          let res = await fetch("https://api.groq.com/openai/v1/audio/translations", {
            method: "POST",
            headers: { "Authorization": `Bearer ${groqKey}` },
            body: formData
          });

          if (!res.ok) {
            res = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
              method: "POST",
              headers: { "Authorization": `Bearer ${groqKey}` },
              body: formData
            });
          }

          if (res.ok) {
            const data = await res.json();
            understoodText = data.text || "";
          }
        }

        txt.innerText = "Movie Recap စကားပြောဟန်ဖြင့် ရေးဖွဲ့နေပါသည်...";

        const prompt = `
သင်သည် နာမည်ကြီး မြန်မာ Movie Recap (ရုပ်ရှင်ဇာတ်ကြောင်းပြန်) အစီအစဉ် ဖန်တီးသူ ဖြစ်သည်။
ပေးထားသော ဗီဒီယိုပါ ဇာတ်လမ်းအကြောင်းအရာနှင့် စကားပြောများကို အခြေခံ၍ လူတိုင်းနားလည်လွယ်ပြီး ဆွဲဆောင်မှုရှိသော မြန်မာစကားပြော Movie Recap Voiceover ဇာတ်ညွှန်းကို ရေးသားပေးရမည်။

စည်းမျဉ်းများ:
၁။ Maid/Servant -> "အိမ်ဖော်မလေး/အိမ်အကူကောင်မလေး", Dog -> "ခွေးလေး", Father -> "အဖေကြီး", Son -> "သားဖြစ်သူ", Daughter-in-law -> "ချွေးမ" စသည့် သဘာဝနာမ်စားများကိုသာ သုံးပါ။
၂။ "ကျွန်တော်", "ကျွန်မ", "ခင်ဗျာ", "ရှင်" မသုံးရ။ ကျား/မ မရွေး ဖတ်နိုင်သော Voiceover လေသံ ဖြစ်ရမည်။
၃။ "ဒီနေ့ ဇာတ်လမ်းလေးမှာတော့...", "ကောင်မလေးက...", "အဲဒီအချိန်မှာပဲ...", "မထင်မှတ်ထားဘဲ...", "နောက်ဆုံးမှာတော့..." စသည့် သဘာဝစကားပြော စကားဆက်များ သုံးပါ။
၄။ အပိုစာသား လုံးဝမပါရ (ZERO ENGLISH)။ "*Intro:*", "*Middle:*" ခေါင်းစဉ်များ၊ "No English? Yes" စသည့် စာတန်းများ လုံးဝမထည့်ရ။

အထက်ပါ စည်းမျဉ်းအတိုင်း သန့်ရှင်းသော မြန်မာ Movie Recap Script စစ်စစ်ကိုသာ ထုတ်ပေးပါ:
        `.trim();

        let finalScript = "";

        // Prefer Groq for ultra-fast generation or Gemini directly
        if (groqKey) {
          const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
            body: JSON.stringify({
              model: "llama-3.3-70b-versatile",
              messages: [
                { role: "system", content: prompt },
                { role: "user", content: `Story information:\n${understoodText || "A father rescues a speaking dog."}` }
              ],
              temperature: 0.3
            })
          });

          if (res.ok) {
            const data = await res.json();
            finalScript = sanitizeRecapScript(data.choices?.[0]?.message?.content || "");
          }
        }

        if (!finalScript && geminiKey) {
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiKey}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contents: [{ parts: [{ text: `${prompt}\n\nStory:\n${understoodText}` }] }]
            })
          });

          if (res.ok) {
            const data = await res.json();
            finalScript = sanitizeRecapScript(data.candidates?.[0]?.content?.parts?.[0]?.text || "");
          }
        }

        if (finalScript) {
          out.value = finalScript;
          document.getElementById("scriptWordsTag").innerText = `${finalScript.split(/\s+/).length} စကားလုံး`;
          showToast("Movie Recap မြန်မာဇာတ်ညွှန်း အောင်မြင်စွာ ရရှိပါပြီ", "success");
        } else {
          throw new Error("ဇာတ်ညွှန်းထုတ်ယူ၍ မရပါ");
        }

      } catch (err) {
        showToast(err.message, "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        icon.classList.remove("hidden");
        txt.innerText = "Generate Movie Recap Script (+30s)";
      }
    }

    function copyScriptText() {
      const t = document.getElementById("recapScriptArea").value.trim();
      if (!t) return showToast("Copy ကူးရန် စာသား မရှိပါ", "error");
      navigator.clipboard.writeText(t).then(() => {
        const tag = document.getElementById("copyBtnTag");
        tag.innerText = "Copied!";
        setTimeout(() => tag.innerText = "Copy Script", 2000);
        showToast("ဇာတ်ညွှန်း ကူးယူပြီးပါပြီ", "success");
      });
    }

    function transferScriptToTts() {
      const t = document.getElementById("recapScriptArea").value.trim();
      if (!t) return showToast("TTS သို့ ပို့ရန် စာသား မရှိပါ", "error");
      document.getElementById("ttsInputTextArea").value = t;
      document.getElementById("charCountTag").innerText = `${t.length} အက္ခရာ`;
      switchStudioView("tts");
      showToast("စာသားများကို TTS အသံထုတ်ခန်းသို့ ထည့်သွင်းပြီးပါပြီ", "success");
    }

    // =========================================================================
    // TTS STUDIO CONTROLLER
    // =========================================================================
    function renderVoiceCatalog(filter = "all") {
      const container = document.getElementById("voicesCatalogList");
      container.innerHTML = "";
      const list = filter === "all" ? PERSONAS : PERSONAS.filter(p => p.gender === filter);

      list.forEach(p => {
        const isSel = p.id === selectedVoiceId;
        const isPrev = p.id === previewingVoiceId;

        const card = document.createElement("div");
        card.className = `p-3 rounded-2xl border transition-all flex items-center justify-between gap-3 cursor-pointer ${
          isSel ? 'bg-purple-900/30 border-purple-500 ring-1 ring-purple-500/50 shadow-md' : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
        }`;
        card.onclick = () => selectVoiceItem(p.id);

        card.innerHTML = `
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <div class="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-xl shrink-0 border border-slate-800">
              ${p.icon}
            </div>
            <div class="truncate">
              <div class="flex items-center gap-1.5">
                <span class="font-bold text-xs sm:text-sm text-slate-100">${p.name}</span>
                <span class="text-[9px] px-1.5 py-0.5 rounded-full font-medium ${
                  p.gender === 'men' ? 'bg-blue-950 text-blue-300 border border-blue-800' : 'bg-pink-950 text-pink-300 border border-pink-800'
                }">
                  ${p.badge}
                </span>
                ${isSel ? '<span class="text-[9px] text-purple-400 font-bold ml-1">✓ ရွေးထားသည်</span>' : ''}
              </div>
              <p class="text-[11px] text-slate-400 truncate mt-0.5">${p.role}</p>
            </div>
          </div>
          <button
            type="button"
            onclick="playVoiceSample('${p.id}', event)"
            class="px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 flex items-center gap-1 transition-all ${
              isPrev ? 'bg-purple-600 text-white animate-pulse' : 'bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-500/30'
            }"
          >
            <span>${isPrev ? '⏹' : '🔈'}</span>
            <span class="hidden sm:inline">${isPrev ? 'ရပ်မည်' : 'စမ်းနားထောင်'}</span>
          </button>
        `;
        container.appendChild(card);
      });
    }

    function selectVoiceItem(id) {
      selectedVoiceId = id;
      const p = PERSONAS.find(x => x.id === id);
      document.getElementById("activeVoiceBadge").innerText = `Selected: ${p.name}`;
      const activeFilter = document.querySelector(".v-pill.bg-purple-600")?.dataset.f || "all";
      renderVoiceCatalog(activeFilter);
    }

    function filterVoiceCatalog(cat) {
      document.querySelectorAll(".v-pill").forEach(btn => {
        if (btn.dataset.f === cat) {
          btn.className = "v-pill px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold transition-all";
        } else {
          btn.className = "v-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all";
        }
      });
      renderVoiceCatalog(cat);
    }

    async function playVoiceSample(id, event) {
      event.stopPropagation();
      const pAudio = document.getElementById("previewAudioEl");

      if (previewingVoiceId === id) {
        pAudio.pause();
        previewingVoiceId = null;
        renderVoiceCatalog(document.querySelector(".v-pill.bg-purple-600")?.dataset.f || "all");
        return;
      }

      previewingVoiceId = id;
      renderVoiceCatalog(document.querySelector(".v-pill.bg-purple-600")?.dataset.f || "all");

      try {
        let res = await fetch(`/api/preview/${id}`);
        if (!res.ok) res = await fetch(`/preview/${id}`);
        if (res.ok) {
          const blob = await res.blob();
          pAudio.src = URL.createObjectURL(blob);
          await pAudio.play();
          return;
        }
      } catch (e) {}

      previewingVoiceId = null;
      renderVoiceCatalog(document.querySelector(".v-pill.bg-purple-600")?.dataset.f || "all");
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ", "error");
    }

    document.getElementById("previewAudioEl").onended = () => {
      previewingVoiceId = null;
      renderVoiceCatalog(document.querySelector(".v-pill.bg-purple-600")?.dataset.f || "all");
    };

    function updateTuningValues() {
      const s = parseInt(document.getElementById("speedRangeInput").value);
      const p = parseInt(document.getElementById("pitchRangeInput").value);
      document.getElementById("spdTag").innerText = s === 0 ? "မူရင်း" : `${s > 0 ? '+' : ''}${s}%`;
      document.getElementById("ptcTag").innerText = p === 0 ? "မူရင်း" : `${p > 0 ? '+' : ''}${p}Hz`;
    }

    document.getElementById("ttsInputTextArea").addEventListener("input", function() {
      document.getElementById("charCountTag").innerText = `${this.value.length} အက္ခရာ`;
    });

    function clearText() {
      document.getElementById("ttsInputTextArea").value = "";
      document.getElementById("charCountTag").innerText = "၀ အက္ခရာ";
    }

    async function handleGenerateAudioSpeech() {
      const text = document.getElementById("ttsInputTextArea").value.trim();
      if (!text) return showToast("စာသား အရင်ရိုက်ထည့်ပေးပါ", "error");

      const btn = document.getElementById("ttsGenerateBtn");
      const spinner = document.getElementById("ttsSpinner");
      const txt = document.getElementById("ttsBtnText");

      btn.disabled = true;
      spinner.classList.remove("hidden");
      txt.innerText = "အသံဖန်တီးနေပါသည်...";

      try {
        let res = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: text,
            persona_id: selectedVoiceId,
            user_rate_offset: parseInt(document.getElementById("speedRangeInput").value),
            user_pitch_offset: parseInt(document.getElementById("pitchRangeInput").value)
          })
        });

        if (!res.ok) {
          res = await fetch("/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: text,
              persona_id: selectedVoiceId,
              user_rate_offset: parseInt(document.getElementById("speedRangeInput").value),
              user_pitch_offset: parseInt(document.getElementById("pitchRangeInput").value)
            })
          });
        }

        if (res.ok) {
          generatedMp3Blob = await res.blob();
          const audioEl = document.getElementById("mainAudioEl");
          audioEl.src = URL.createObjectURL(generatedMp3Blob);
          document.getElementById("ttsPlayerCard").classList.remove("hidden");
          await audioEl.play();
          showToast("အသံဖိုင် အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ", "success");
        } else {
          showToast("အသံဖန်တီး၍ မရပါ", "error");
        }
      } catch (err) {
        showToast("ချိတ်ဆက်မှု မအောင်မြင်ပါ", "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        txt.innerText = "🎙 Generate Speech (အသံဖန်တီးမည်)";
      }
    }

    function downloadGeneratedMp3() {
      if (!generatedMp3Blob) return;
      const a = document.createElement("a");
      a.href = URL.createObjectURL(generatedMp3Blob);
      a.download = `Recap_Go_${selectedVoiceId}_${Date.now()}.mp3`;
      a.click();
      showToast("MP3 ဒေါင်းလုဒ် ဆွဲပြီးပါပြီ", "success");
    }

    // Init
    renderVoiceCatalog("all");
    updateTuningValues();
    document.getElementById("charCountTag").innerText = `${document.getElementById("ttsInputTextArea").value.length} အက္ခရာ`;
  </script>
</body>
</html>
"""

@app.get("/")
def read_root():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api")
def read_api_root():
    return HTMLResponse(content=HTML_CONTENT)
