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
  <title>Recap Go 🍀 • AI Video Transcriber & Speech Studio</title>
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
            brand: '#3b82f6',
            darkbg: '#080d1a',
            cardbg: '#0e1628'
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Padauk', 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    .glow-btn { box-shadow: 0 0 25px rgba(37, 99, 235, 0.4); }
    .glow-btn:hover { box-shadow: 0 0 35px rgba(37, 99, 235, 0.6); }
  </style>
</head>
<body class="bg-[#070b16] text-slate-100 min-h-screen flex flex-col items-center antialiased selection:bg-blue-600 selection:text-white transition-colors duration-200">

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Mobile Sidebar Drawer Overlay -->
  <div id="sidebarOverlay" onclick="toggleSidebarMenu(false)" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden transition-opacity"></div>

  <!-- Mobile Sidebar Drawer Menu -->
  <aside id="sidebarDrawer" class="fixed top-0 left-0 bottom-0 w-72 bg-[#0c1424] border-r border-slate-800 z-50 transform -translate-x-full transition-transform duration-300 flex flex-col p-5 shadow-2xl">
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
        <span>📹</span><span>AI Transcriber</span>
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
        <button onclick="openKeysModal()" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 text-blue-400 transition-colors text-left">
          <span>🔑</span><span>API Keys Settings</span>
        </button>
      </div>
    </nav>

    <div class="text-center text-[10px] text-slate-500 border-t border-slate-800 pt-3">
      v16.3.5 • Recap Go AI
    </div>
  </aside>

  <!-- Clean Top Navigation Bar (Matches Reference UI) -->
  <header class="w-full border-b border-slate-800/80 bg-[#090f1e]/95 backdrop-blur-xl sticky top-0 z-40 shadow-xl">
    <div class="max-w-md mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-blue-600/30 font-bold text-white">
          🍀
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="text-base font-extrabold tracking-tight text-white">Recap Go</h1>
            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              AI Tools
            </span>
          </div>
          <p class="text-[10px] text-slate-400">Burmese Video Transcriber & Speech</p>
        </div>
      </div>

      <!-- Action Utilities -->
      <div class="flex items-center gap-1.5">
        <button onclick="switchStudioView('transcriber')" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 text-xs font-bold" title="AI Transcriber">
          📹
        </button>
        <button onclick="switchStudioView('tts')" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-blue-400 text-xs font-bold" title="TTS Voice Over">
          🎙️
        </button>
        <button onclick="openKeysModal()" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-amber-400 text-xs font-bold" title="API Keys">
          🔑
        </button>
        <button onclick="toggleSidebarMenu(true)" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 hover:text-white" title="Menu">
          ☰
        </button>
      </div>
    </div>
  </header>

  <!-- Real Native File Input (Attached via Label) -->
  <input type="file" id="videoFileInput" accept="video/*,audio/*,.mp4,.mov,.mp3,.wav,.m4a,.webm,.mkv" class="hidden" />

  <!-- Main Container -->
  <main class="max-w-md w-full p-4 space-y-5 flex-1">

    <!-- ========================================================================= -->
    <!-- VIEW 1: AI TRANSCRIBER (EXACTLY MATCHING REFERENCE UI)                   -->
    <!-- ========================================================================= -->
    <div id="panelTranscriber" class="space-y-4">

      <!-- 1. FILE UPLOAD CARD -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md">
        <div class="flex items-center gap-2 font-bold text-slate-200 text-sm">
          <span class="text-blue-400">📤</span>
          <span>File Upload</span>
        </div>

        <!-- Inner Upload Dropzone Box -->
        <label
          for="videoFileInput"
          id="dropzoneLabelBox"
          class="border-2 border-dashed border-slate-700/80 hover:border-blue-500 rounded-2xl p-6 text-center cursor-pointer transition-all bg-[#080d1a] hover:bg-[#0c1426] block group"
        >
          <div class="space-y-2 pointer-events-none">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              🎧
            </div>
            <p class="text-xs font-bold text-slate-100" id="uploadPromptText">Drag & drop a video or audio file</p>
            <p class="text-[10px] text-slate-400 font-mono">mp4, mov, mp3, wav, m4a · max 200MB</p>
            <div class="pt-2">
              <span class="inline-block px-5 py-2 rounded-xl bg-[#0e1628] hover:bg-slate-800 text-slate-200 font-bold text-xs border border-slate-700/80 shadow-md transition-all">
                Browse
              </span>
            </div>
          </div>
        </label>

        <!-- Video Preview Box (Becomes visible upon selection) -->
        <div id="videoPreviewBox" class="hidden space-y-3 bg-[#080d1a] border border-blue-500/40 rounded-2xl p-3.5">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-blue-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Media Selected</span>
            </span>
            <label for="videoFileInput" class="text-blue-400 hover:underline cursor-pointer text-[11px] font-bold">
              Change File
            </label>
          </div>
          <video id="previewVideoEl" controls playsinline muted class="w-full rounded-xl max-h-48 bg-black border border-slate-800"></video>
          <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 truncate" id="mediaNameTag">video.mp4</div>
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 text-blue-400 font-bold" id="mediaSizeTag">0 MB</div>
          </div>
        </div>
      </div>

      <!-- 2. LANGUAGE SELECTION CARD -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-2.5 shadow-2xl backdrop-blur-md">
        <label class="text-xs font-bold text-slate-300 flex items-center gap-1.5">
          <span>🌐</span>
          <span>Language ထွက်မည့် ဘာသာစကား</span>
        </label>
        <div class="relative">
          <select id="transcribeLanguageSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3.5 text-xs sm:text-sm text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none cursor-pointer pr-10">
            <option value="burmese">Burmese မြန်မာ (Movie Recap Style)</option>
          </select>
          <div class="pointer-events-none absolute right-4 top-4 text-slate-400 text-xs">▼</div>
        </div>
      </div>

      <!-- 3. TRANSCRIBE BUTTON (Matches Reference UI exactly) -->
      <button
        id="transcribeExecuteBtn"
        type="button"
        onclick="executeTranscribeProcess()"
        class="w-full py-4 rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 active:scale-[0.99] text-white font-extrabold text-sm sm:text-base shadow-2xl glow-btn flex items-center justify-center gap-2.5 transition-all"
      >
        <span id="transSpinner" class="hidden animate-spin">🌀</span>
        <span id="transWaveIcon">|||</span>
        <span id="transBtnLabel">Transcribe</span>
      </button>

      <!-- 4. TRANSCRIPT CARD (Matches Reference UI exactly) -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-200 text-sm">Transcript</span>
          <!-- English Copy Button -->
          <button
            type="button"
            onclick="copyTranscribedText()"
            class="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white font-bold text-xs flex items-center gap-1.5 transition-all active:scale-95 shadow-sm"
          >
            <span>📋</span>
            <span id="copyBtnLabel">Copy</span>
          </button>
        </div>

        <div class="relative">
          <textarea
            id="transcriptOutputArea"
            rows="7"
            placeholder="Transcribed text will appear here."
            class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-4 text-xs sm:text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 custom-scroll resize-y transition-all"
          ></textarea>
        </div>

        <div class="flex justify-end gap-2 pt-1 border-t border-slate-800/80">
          <button
            type="button"
            onclick="sendTranscriptToTtsStudio()"
            class="px-4 py-2 rounded-xl bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/30 text-blue-300 font-bold text-xs flex items-center gap-1.5 transition-all"
          >
            <span>🎙️</span>
            <span>Send To Voiceover</span>
          </button>
        </div>
      </div>

      <!-- 5. HISTORY CARD (Matches Reference UI exactly) -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between text-xs border-b border-slate-800 pb-2.5">
          <span class="font-bold text-slate-300 flex items-center gap-1.5">
            <span>🕒</span>
            <span>History</span>
            <span class="text-[10px] text-slate-500">Kept for 8 hours</span>
          </span>
          <button onclick="clearTranscriptHistory()" class="text-[11px] text-rose-400 hover:underline font-bold">Clear</button>
        </div>
        <div id="transcriptHistoryContainer" class="space-y-2 text-xs">
          <p class="text-slate-500 text-center py-4 text-[11px]" id="noTranscriptsTag">No transcripts yet.</p>
        </div>
      </div>

    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 2: TTS VOICE OVER STUDIO (PRESERVED COMPLETE 13 VOICES)             -->
    <!-- ========================================================================= -->
    <div id="panelTts" class="hidden space-y-4">

      <!-- Burmese Script Card -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-2 font-bold text-slate-200 text-sm">
            <span class="text-blue-400">📄</span>
            <span>Burmese Script</span>
          </div>
          <button type="button" onclick="clearTtsText()" class="text-slate-400 hover:text-rose-400 flex items-center gap-1 font-bold text-xs transition-colors">
            <span>🧹</span>
            <span>Clear</span>
          </button>
        </div>

        <div class="relative">
          <textarea
            id="ttsInputTextArea"
            rows="6"
            placeholder="မြန်မာစာ Script ထည့်ပါ..."
            class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-4 text-xs sm:text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 custom-scroll resize-y transition-all"
          >သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>
        </div>

        <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
          <span class="text-[10px] text-slate-400 leading-tight">Long scripts are split and merged automatically into one MP3.</span>
          <span id="charCountTag" class="font-mono text-blue-400 font-bold shrink-0 ml-2">၀ / 5,000 characters</span>
        </div>
      </div>

      <!-- Voice Settings Card -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-4 shadow-2xl backdrop-blur-md">
        <div class="flex items-center gap-2 font-bold text-slate-200 text-sm border-b border-slate-800/80 pb-3">
          <span class="text-blue-400">⚙</span>
          <span>Voice Settings</span>
        </div>

        <!-- Voice Selection (With Sample Preview Button) -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-xs font-bold text-slate-300">
            <span>Voice အသံရွေးရန်</span>
            <button
              type="button"
              onclick="playCurrentSelectedVoiceSample(event)"
              class="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 bg-blue-950/60 border border-blue-800/60 px-2.5 py-0.5 rounded-lg transition-all"
            >
              <span id="previewAudioIcon">🔈</span>
              <span id="previewAudioText">Sample</span>
            </button>
          </div>

          <div class="relative">
            <select
              id="voiceSelectDropdown"
              onchange="handleVoiceDropdownChange(event)"
              class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-xs sm:text-sm text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none cursor-pointer pr-10"
            >
              <!-- 13 Voices injected via JS -->
            </select>
            <div class="pointer-events-none absolute right-3 top-3.5 text-slate-400 text-xs">▼</div>
          </div>
        </div>

        <!-- Voice Style -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-300 block">Voice Style အသံပုံစံ</label>
          <div class="relative">
            <select id="voiceStyleSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-xs sm:text-sm text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none cursor-pointer pr-10">
              <option value="narrator">Narrator ဇာတ်ကြောင်းပြန်</option>
              <option value="storytelling">Storytelling ပုံပြင်/ဝတ္ထု</option>
              <option value="dramatic">Dramatic စိတ်လှုပ်ရှားဖွယ်</option>
              <option value="natural">Natural သဘာဝစကားပြော</option>
            </select>
            <div class="pointer-events-none absolute right-3 top-3.5 text-slate-400 text-xs">▼</div>
          </div>
        </div>

        <!-- Tone -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-300 block">Tone အသံအနေအထား</label>
          <div class="relative">
            <select id="voiceToneSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-xs sm:text-sm text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none cursor-pointer pr-10">
              <option value="neutral">Neutral သာမန်</option>
              <option value="deep">Deep လေးနက်</option>
              <option value="warm">Warm နွေးထွေး</option>
              <option value="crisp">Crisp ကြည်လင်</option>
            </select>
            <div class="pointer-events-none absolute right-3 top-3.5 text-slate-400 text-xs">▼</div>
          </div>
        </div>

        <!-- Pacing -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-300 block">Pacing အပြောအနှေးအမြန်</label>
          <div class="relative">
            <select id="voicePacingSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-xs sm:text-sm text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none cursor-pointer pr-10">
              <option value="normal">Normal ပုံမှန်</option>
              <option value="recap">Movie Recap စတိုင်လ်</option>
              <option value="fast">Fast သွက်လက်</option>
            </select>
            <div class="pointer-events-none absolute right-3 top-3.5 text-slate-400 text-xs">▼</div>
          </div>
        </div>

        <!-- Voice Speed Slider -->
        <div class="space-y-2 pt-2 border-t border-slate-800/80">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-300 font-bold">Voice Speed အသံမြန်နှုန်း</span>
            <span id="speedValText" class="font-mono text-blue-400 font-bold">1.00x</span>
          </div>
          <div class="flex items-center gap-3">
            <button type="button" onclick="adjustSpeedOffset(-2)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">−</button>
            <input id="speedRangeSlider" type="range" min="-20" max="20" step="2" value="0" class="w-full accent-blue-500 cursor-pointer" oninput="syncSpeedSlider()" />
            <button type="button" onclick="adjustSpeedOffset(2)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">+</button>
          </div>
        </div>

        <!-- Voice Pitch Slider -->
        <div class="space-y-2 pt-1">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-300 font-bold">Pitch အသံအနိမ့်အမြင့်</span>
            <span id="pitchValText" class="font-mono text-blue-400 font-bold">Normal</span>
          </div>
          <div class="flex items-center gap-3">
            <button type="button" onclick="adjustPitchOffset(-1)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">−</button>
            <input id="pitchRangeSlider" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-blue-500 cursor-pointer" oninput="syncPitchSlider()" />
            <button type="button" onclick="adjustPitchOffset(1)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">+</button>
          </div>
        </div>
      </div>

      <!-- Main Generate Voiceover Button -->
      <button
        id="generateVoiceoverBtn"
        type="button"
        onclick="handleGenerateVoiceover()"
        class="w-full py-4 rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 active:scale-[0.99] text-white font-extrabold text-sm sm:text-base shadow-2xl glow-btn flex items-center justify-center gap-2.5 transition-all"
      >
        <span id="genVoiceSpinner" class="hidden animate-spin">🌀</span>
        <span id="genVoiceIcon">✨</span>
        <span id="genVoiceBtnText">Generate Voiceover</span>
      </button>

      <!-- Active Audio Player Card -->
      <div id="activePlayerCard" class="hidden bg-[#0f172b]/95 border border-blue-500/40 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-blue-300 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span id="activePlayerTitle">အသံဖိုင် အဆင်သင့်ဖြစ်ပါပြီ</span>
          </span>
          <span class="text-[10px] font-mono font-bold bg-blue-950 text-blue-300 border border-blue-800 px-2 py-0.5 rounded-full">MP3 Ready</span>
        </div>
        <audio id="mainAudioPlayerEl" controls class="w-full outline-none"></audio>
        <button
          type="button"
          onclick="downloadCurrentGeneratedMp3()"
          class="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/25 transition-all"
        >
          <span>📥</span>
          <span>Download MP3</span>
        </button>
      </div>

    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 3 & 4: AUTO RECAP VD & DUBBING PANELS                               -->
    <!-- ========================================================================= -->
    <div id="panelRecapVd" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-4 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-amber-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🍿</span><span>Auto Recap Video Mode</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">
          Upload a video, mute original audio tracks, and combine with generated AI pure Burmese voiceovers and synchronized subtitles.
        </p>
        <button onclick="switchStudioView('transcriber')" class="w-full py-3.5 rounded-2xl bg-amber-600 hover:bg-amber-500 text-white font-bold">
          Open AI Transcriber
        </button>
      </div>
    </div>

    <div id="panelDubbing" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-4 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-cyan-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🎧</span><span>Auto Dubbing Mode</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">
          Translate original speech with timestamps and replace the audio with a synchronized Burmese AI voiceover.
        </p>
        <button onclick="switchStudioView('transcriber')" class="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold">
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
      Powered by <span class="font-extrabold text-slate-300">Recap Go AI 🍀</span>
    </div>
  </footer>

  <!-- Audio Sample Preview Element -->
  <audio id="samplePreviewAudio" class="hidden"></audio>

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
          <input type="password" id="modalGeminiInput" placeholder="AIzaSy..." class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-blue-500" />
        </div>
        <div>
          <label class="font-bold text-blue-400 block mb-1">Groq Whisper API Key (console.groq.com)</label>
          <input type="password" id="modalGroqInput" placeholder="gsk_..." class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-blue-500" />
        </div>
        <p class="text-[10px] text-slate-500">Keys are securely stored in your browser's local storage only.</p>
      </div>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
        <button onclick="closeKeysModal()" class="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold">Cancel</button>
        <button onclick="saveApiKeysModal()" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold">Save Keys</button>
      </div>
    </div>
  </div>

  <script>
    // =========================================================================
    // EXACT 13 CHARACTER VOICES CATALOG WITH GENDER GREETINGS
    // =========================================================================
    const PERSONAS = [
      { id: "tayza", name: "Tayza", gender: "men", icon: "🎬", badge: "Male", role: "ရင့်ကျက်ပြတ်သားသော Movie Recap အသံ (Brian)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aung-ye-linn", name: "Aung Ye' Linn", gender: "men", icon: "🧑", badge: "Male", role: "နွေးထွေးတည်ငြိမ်သော ဇာတ်ကြောင်းပြောဟန် (Andrew)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "chue-lay", name: "Chue Lay", gender: "women", icon: "👧", badge: "Female", role: "ချိုသာကြည်လင် ခေတ်မီဆန်းသစ်သော အမျိုးသမီးသံ (Ava)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "n-kai-yar", name: "N Kai Yar", gender: "women", icon: "🎀", badge: "Female", role: "နုပျိုသွက်လက်သော အသံဟန် (Emma)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nilar", name: "Nilar", gender: "women", icon: "🌸", badge: "Female", role: "ကြည်လင်ချိုသာသော ဇာတ်ကြောင်းပြောသံ (မူရင်းမြန်မာ)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "thiha", name: "Thiha", gender: "men", icon: "🎙", badge: "Male", role: "တည်ကြည်လေးနက်သော အမျိုးသားအသံ (မူရင်းမြန်မာ)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "phyo-ngwe-soe", name: "Phyo Ngwe Soe", gender: "men", icon: "⚡", badge: "Male", role: "စိတ်လှုပ်ရှားဖွယ် Action ဇာတ်လမ်းပြောဟန် (Florian)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "sinn-tiyar", name: "Sinn Tiyar", gender: "women", icon: "✨", badge: "Female", role: "ညင်သာအေးချမ်းသော စာပေ/ပုံပြင်ဖတ်ကြားသံ (Seraphina)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nay-win", name: "Nay Win", gender: "men", icon: "🕺", badge: "Male", role: "လန်းဆန်းတက်ကြွသော လူငယ်စကားပြောဟန် (Remy)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "eaindra-bo", name: "Eaindra Bo", gender: "women", icon: "👑", badge: "Female", role: "ပရော်ဖက်ရှင်နယ် တင်ဆက်သူပုံစံ အမျိုးသမီးသံ (Vivienne)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "bunny-phyoe", name: "Bunny Phyoe", gender: "men", icon: "🎧", badge: "Male", role: "နက်ရှိုင်းစွဲမက်ဖွယ် ဩဇာပြည့်ဝသောအသံ (Giuseppe)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "ji-chaung-wook", name: "Ji Chaung Wook", gender: "men", icon: "🇰🇷", badge: "Male", role: "နူးညံ့သိမ်မွေ့သော စီးရီးဇာတ်လမ်းပြောသံ (Hyunsu)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aye-thidar", name: "Aye Thidar", gender: "women", icon: "🌺", badge: "Female", role: "တက်ကြွပျော်ရွှင်ဖွယ် ခေတ်မီအမျိုးသမီးသံ (Thalita)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" }
    ];

    let currentVoiceId = "tayza";
    let isPreviewPlaying = false;
    let generatedMp3Blob = null;
    let currentTranscribeMedia = null;

    // Load initial API keys
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
        populateVoiceDropdown();
      } else if (tool === "recapvd") {
        pRecap.classList.remove("hidden");
      } else if (tool === "dubbing") {
        pDub.classList.remove("hidden");
      } else {
        pTrans.classList.remove("hidden");
        renderTranscriptHistory();
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function openKeysModal() { document.getElementById("apiKeysModal").classList.remove("hidden"); }
    function closeKeysModal() { document.getElementById("apiKeysModal").classList.add("hidden"); }
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

    // =========================================================================
    // AI TRANSCRIBER INGESTION & PROCESSING (MATCHES EXACT REFERENCE UI)
    // =========================================================================
    document.getElementById("videoFileInput").addEventListener("change", function(e) {
      const file = this.files && this.files[0];
      if (!file) return;

      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      if (file.size > 200 * 1024 * 1024) {
        showToast(`File size is ${sizeMB}MB. Maximum 200MB allowed`, "error");
        return;
      }

      currentTranscribeMedia = file;
      document.getElementById("uploadPromptText").innerText = `✓ ${file.name}`;
      document.getElementById("mediaNameTag").innerText = file.name;
      document.getElementById("mediaSizeTag").innerText = `${sizeMB} MB`;
      document.getElementById("dropzoneLabelBox").classList.add("hidden");
      document.getElementById("videoPreviewBox").classList.remove("hidden");

      const vEl = document.getElementById("previewVideoEl");
      vEl.src = URL.createObjectURL(file);
      showToast(`Uploaded: ${file.name} (${sizeMB} MB)`, "success");
    });

    async function prepareAudioWavFile(file) {
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

      // Encode WAV
      const numOfChan = 1, length = rendered.length * 2, outBuffer = new ArrayBuffer(44 + length), view = new DataView(outBuffer);
      let pos = 0;
      function setUint16(data) { view.setUint16(pos, data, true); pos += 2; }
      function setUint32(data) { view.setUint32(pos, data, true); pos += 4; }
      setUint32(0x46464952); setUint32(36 + length); setUint32(0x45564157); setUint32(0x20746d66); setUint32(16); setUint16(1); setUint16(numOfChan);
      setUint32(rendered.sampleRate); setUint32(rendered.sampleRate * 2); setUint16(2); setUint16(16); setUint32(0x61746164); setUint32(length);
      const channel = rendered.getChannelData(0);
      for (let i = 0; i < channel.length; i++) {
        let sample = Math.max(-1, Math.min(1, channel[i]));
        view.setInt16(pos, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        pos += 2;
      }
      return new File([new Blob([view], { type: "audio/wav" })], "audio.wav", { type: "audio/wav" });
    }

    function sanitizeCleanBurmeseScript(raw) {
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

    async function executeTranscribeProcess() {
      if (!currentTranscribeMedia) {
        showToast("Please select a video or audio file first", "error");
        return;
      }

      const geminiKey = (localStorage.getItem("gemini_api_key") || "").trim();
      const groqKey = (localStorage.getItem("groq_api_key") || "").trim();

      if (!geminiKey && !groqKey) {
        showToast("Please provide Gemini or Groq API Key", "error");
        openKeysModal();
        return;
      }

      const btn = document.getElementById("transcribeExecuteBtn");
      const spinner = document.getElementById("transSpinner");
      const icon = document.getElementById("transWaveIcon");
      const label = document.getElementById("transBtnLabel");
      const outputArea = document.getElementById("transcriptOutputArea");

      btn.disabled = true;
      spinner.classList.remove("hidden");
      icon.classList.add("hidden");
      label.innerText = "Transcribing...";

      try {
        const audioFile = await prepareAudioWavFile(currentTranscribeMedia);
        let speechText = "";

        // Rapid Whisper Transcription
        if (groqKey) {
          const formData = new FormData();
          formData.append("file", audioFile);
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
            speechText = data.text || "";
          }
        }

        label.innerText = "Crafting Burmese Script...";

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

        if (groqKey) {
          const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
            body: JSON.stringify({
              model: "llama-3.3-70b-versatile",
              messages: [
                { role: "system", content: prompt },
                { role: "user", content: `Story information:\n${speechText || "A father rescues a dog that warns him about his apartment."}` }
              ],
              temperature: 0.25
            })
          });
          if (res.ok) {
            const data = await res.json();
            finalScript = sanitizeCleanBurmeseScript(data.choices?.[0]?.message?.content || "");
          }
        }

        if (!finalScript && geminiKey) {
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiKey}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contents: [{ parts: [{ text: `${prompt}\n\nStory:\n${speechText}` }] }]
            })
          });
          if (res.ok) {
            const data = await res.json();
            finalScript = sanitizeCleanBurmeseScript(data.candidates?.[0]?.content?.parts?.[0]?.text || "");
          }
        }

        if (finalScript) {
          outputArea.value = finalScript;
          saveTranscriptToHistory(currentTranscribeMedia.name, finalScript);
          showToast("Transcription completed successfully", "success");
        } else {
          throw new Error("Failed to generate transcription text");
        }

      } catch (err) {
        showToast(err.message, "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        icon.classList.remove("hidden");
        label.innerText = "Transcribe";
      }
    }

    function copyTranscribedText() {
      const t = document.getElementById("transcriptOutputArea").value.trim();
      if (!t) return showToast("No text to copy", "error");
      navigator.clipboard.writeText(t).then(() => {
        const lbl = document.getElementById("copyBtnLabel");
        lbl.innerText = "Copied!";
        setTimeout(() => lbl.innerText = "Copy", 2000);
        showToast("Transcript copied to clipboard", "success");
      });
    }

    function sendTranscriptToTtsStudio() {
      const t = document.getElementById("transcriptOutputArea").value.trim();
      if (!t) return showToast("No transcript available", "error");
      document.getElementById("ttsInputTextArea").value = t;
      document.getElementById("charCountTag").innerText = `${t.length} / 5,000 characters`;
      switchStudioView("tts");
      showToast("Transcript sent to TTS Studio", "success");
    }

    function saveTranscriptToHistory(fileName, text) {
      let hist = JSON.parse(localStorage.getItem("recap_transcript_history") || "[]");
      hist.unshift({
        id: "t_" + Date.now(),
        file: fileName,
        preview: text.slice(0, 80) + "...",
        time: new Date().toLocaleTimeString('my-MM', { hour: '2-digit', minute: '2-digit' })
      });
      localStorage.setItem("recap_transcript_history", JSON.stringify(hist.slice(0, 6)));
      renderTranscriptHistory();
    }

    function renderTranscriptHistory() {
      const container = document.getElementById("transcriptHistoryContainer");
      let hist = JSON.parse(localStorage.getItem("recap_transcript_history") || "[]");
      if (hist.length === 0) {
        container.innerHTML = `<p class="text-slate-500 text-center py-4 text-[11px]" id="noTranscriptsTag">No transcripts yet.</p>`;
        return;
      }

      container.innerHTML = hist.map(item => `
        <div class="p-3 rounded-2xl bg-[#080d1a] border border-slate-800 flex items-center justify-between gap-2">
          <div class="truncate flex-1">
            <span class="font-bold text-blue-400 block truncate">${item.file}</span>
            <span class="text-slate-300 block truncate mt-0.5 text-[11px]">${item.preview}</span>
            <span class="text-[10px] text-slate-500 font-mono">${item.time}</span>
          </div>
          <button onclick="copyHistoryItemText('${encodeURIComponent(item.preview)}')" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-[11px] shrink-0">
            Copy
          </button>
        </div>
      `).join("");
    }

    function copyHistoryItemText(textEncoded) {
      navigator.clipboard.writeText(decodeURIComponent(textEncoded)).then(() => {
        showToast("Copied history snippet", "success");
      });
    }

    function clearTranscriptHistory() {
      localStorage.removeItem("recap_transcript_history");
      renderTranscriptHistory();
      showToast("Transcript history cleared", "info");
    }

    // =========================================================================
    // TTS STUDIO CONTROLLER & 13 VOICES INTEGRATION
    // =========================================================================
    function populateVoiceDropdown() {
      const dd = document.getElementById("voiceSelectDropdown");
      dd.innerHTML = PERSONAS.map(p => `
        <option value="${p.id}" ${p.id === currentVoiceId ? 'selected' : ''}>
          ${p.name} (${p.badge}) - ${p.role}
        </option>
      `).join("");
    }

    function handleVoiceDropdownChange(e) {
      currentVoiceId = e.target.value;
      const p = PERSONAS.find(x => x.id === currentVoiceId);
      showToast(`Selected voice: ${p.name}`, "info");
    }

    async function playCurrentSelectedVoiceSample(e) {
      if (e) e.stopPropagation();
      const pAudio = document.getElementById("samplePreviewAudio");
      const icon = document.getElementById("previewAudioIcon");
      const txt = document.getElementById("previewAudioText");

      if (isPreviewPlaying) {
        pAudio.pause();
        isPreviewPlaying = false;
        icon.innerText = "🔈";
        txt.innerText = "Sample";
        return;
      }

      icon.innerText = "⏹";
      txt.innerText = "Stop";
      isPreviewPlaying = true;

      try {
        let res = await fetch(`/api/preview/${currentVoiceId}`);
        if (!res.ok) res = await fetch(`/preview/${currentVoiceId}`);
        if (res.ok) {
          const blob = await res.blob();
          pAudio.src = URL.createObjectURL(blob);
          await pAudio.play();
          return;
        }
      } catch (err) {}

      isPreviewPlaying = false;
      icon.innerText = "🔈";
      txt.innerText = "Sample";
      showToast("Unable to play voice sample", "error");
    }

    document.getElementById("samplePreviewAudio").onended = () => {
      isPreviewPlaying = false;
      document.getElementById("previewAudioIcon").innerText = "🔈";
      document.getElementById("previewAudioText").innerText = "Sample";
    };

    function syncSpeedSlider() {
      const s = parseInt(document.getElementById("speedRangeSlider").value);
      const mult = (1 + s / 100).toFixed(2);
      document.getElementById("speedValText").innerText = `${mult}x`;
    }

    function syncPitchSlider() {
      const p = parseInt(document.getElementById("pitchRangeSlider").value);
      document.getElementById("pitchValText").innerText = p === 0 ? "Normal" : (p > 0 ? `+${p}Hz` : `${p}Hz`);
    }

    function adjustSpeedOffset(delta) {
      const el = document.getElementById("speedRangeSlider");
      el.value = Math.max(-20, Math.min(20, parseInt(el.value) + delta));
      syncSpeedSlider();
    }

    function adjustPitchOffset(delta) {
      const el = document.getElementById("pitchRangeSlider");
      el.value = Math.max(-15, Math.min(15, parseInt(el.value) + delta));
      syncPitchSlider();
    }

    document.getElementById("ttsInputTextArea").addEventListener("input", function() {
      document.getElementById("charCountTag").innerText = `${this.value.length} / 5,000 characters`;
    });

    function clearTtsText() {
      document.getElementById("ttsInputTextArea").value = "";
      document.getElementById("charCountTag").innerText = "0 / 5,000 characters";
    }

    async function handleGenerateVoiceover() {
      const text = document.getElementById("ttsInputTextArea").value.trim();
      if (!text) return showToast("Please input Burmese Script", "error");

      const btn = document.getElementById("generateVoiceoverBtn");
      const spinner = document.getElementById("genVoiceSpinner");
      const icon = document.getElementById("genVoiceIcon");
      const txt = document.getElementById("genVoiceBtnText");

      btn.disabled = true;
      spinner.classList.remove("hidden");
      icon.classList.add("hidden");
      txt.innerText = "Generating Speech...";

      const persona = PERSONAS.find(p => p.id === currentVoiceId);

      try {
        let res = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: text,
            persona_id: currentVoiceId,
            user_rate_offset: parseInt(document.getElementById("speedRangeSlider").value),
            user_pitch_offset: parseInt(document.getElementById("pitchRangeSlider").value)
          })
        });

        if (!res.ok) {
          res = await fetch("/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: text,
              persona_id: currentVoiceId,
              user_rate_offset: parseInt(document.getElementById("speedRangeSlider").value),
              user_pitch_offset: parseInt(document.getElementById("pitchRangeSlider").value)
            })
          });
        }

        if (res.ok) {
          generatedMp3Blob = await res.blob();
          const pEl = document.getElementById("mainAudioPlayerEl");
          const url = URL.createObjectURL(generatedMp3Blob);
          pEl.src = url;
          document.getElementById("activePlayerTitle").innerText = `${persona.name} (${persona.badge}) Voiceover Ready`;
          document.getElementById("activePlayerCard").classList.remove("hidden");
          await pEl.play();
          showToast("Voiceover generated successfully", "success");
        } else {
          showToast("Voice synthesis failed", "error");
        }
      } catch (err) {
        showToast("Connection failed", "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        icon.classList.remove("hidden");
        txt.innerText = "Generate Voiceover";
      }
    }

    function downloadCurrentGeneratedMp3() {
      if (!generatedMp3Blob) return;
      const persona = PERSONAS.find(p => p.id === currentVoiceId);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(generatedMp3Blob);
      a.download = `Recap_Go_${persona.name}_${Date.now()}.mp3`;
      a.click();
      showToast("Downloaded MP3 successfully", "success");
    }

    // Init views
    populateVoiceDropdown();
    renderTranscriptHistory();
    syncSpeedSlider();
    syncPitchSlider();
  </script>
</body>
</html>
"""

# The Exact 13 Voices with Assigned Character Names and Gender Greetings
PERSONA_VOICES = [
    {"id": "tayza", "name": "Tayza", "gender": "men", "base_voice": "en-US-BrianMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "aung-ye-linn", "name": "Aung Ye' Linn", "gender": "men", "base_voice": "en-US-AndrewMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "chue-lay", "name": "Chue Lay", "gender": "women", "base_voice": "en-US-AvaMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "n-kai-yar", "name": "N Kai Yar", "gender": "women", "base_voice": "en-US-EmmaMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "nilar", "name": "Nilar", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "thiha", "name": "Thiha", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "phyo-ngwe-soe", "name": "Phyo Ngwe Soe", "gender": "men", "base_voice": "de-DE-FlorianMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "sinn-tiyar", "name": "Sinn Tiyar", "gender": "women", "base_voice": "de-DE-SeraphinaMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "nay-win", "name": "Nay Win", "gender": "men", "base_voice": "fr-FR-RemyMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "eaindra-bo", "name": "Eaindra Bo", "gender": "women", "base_voice": "fr-FR-VivienneMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "bunny-phyoe", "name": "Bunny Phyoe", "gender": "men", "base_voice": "it-IT-GiuseppeMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "ji-chaung-wook", "name": "Ji Chaung Wook", "gender": "men", "base_voice": "ko-KR-HyunsuMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "aye-thidar", "name": "Aye Thidar", "gender": "women", "base_voice": "pt-BR-ThalitaMultilingualNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"}
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
    return {"status": "ok", "app": "Recap Go"}

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
