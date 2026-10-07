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
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: '#3b82f6',
            darkbg: '#070b16',
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
    .switch-checkbox:checked + .switch-label { background-color: #3b82f6; }
    .switch-checkbox:checked + .switch-label .switch-dot { transform: translateX(100%); background-color: #ffffff; }
    #draggableBlurBox {
      touch-action: none;
      user-select: none;
      cursor: move;
    }
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
      <button onclick="switchStudioView('recapvd')" class="w-full flex items-center gap-3 p-3 rounded-2xl bg-blue-600/20 text-blue-400 border border-blue-500/30 transition-colors text-left">
        <span>🍿</span><span>Auto Recap VD</span>
      </button>
      <button onclick="switchStudioView('transcriber')" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 transition-colors text-left">
        <span>📹</span><span>AI Transcriber</span>
      </button>
      <button onclick="switchStudioView('tts')" class="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-slate-900 transition-colors text-left">
        <span>🎙️</span><span>TTS Voice Over</span>
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

  <!-- Clean Top Navigation Bar -->
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
              Auto Recap
            </span>
          </div>
          <p class="text-[10px] text-slate-400">Burmese Text to Speech & Recap</p>
        </div>
      </div>

      <!-- Action Utilities -->
      <div class="flex items-center gap-1.5">
        <button onclick="switchStudioView('recapvd')" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-amber-400 text-xs font-bold" title="Auto Recap VD">
          🍿
        </button>
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

  <!-- Real Native File Inputs (Hidden) -->
  <input type="file" id="recapVideoFileInput" accept="video/*,.mp4,.mov,.mkv,.webm" class="hidden" />
  <input type="file" id="transVideoFileInput" accept="video/*,audio/*,.mp4,.mov,.mp3,.wav,.m4a,.webm,.mkv" class="hidden" />

  <!-- Hidden Offscreen Canvas for Real Video Rendering & Export -->
  <canvas id="offscreenRenderCanvas" class="hidden"></canvas>

  <!-- Main Container -->
  <main class="max-w-md w-full p-4 space-y-5 flex-1">

    <!-- ========================================================================= -->
    <!-- VIEW 1: AUTO RECAP VD                                                     -->
    <!-- ========================================================================= -->
    <div id="panelRecapVd" class="space-y-4">

      <!-- 1. VIDEO UPLOAD CARD -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md">
        <div class="flex items-center gap-2 font-bold text-slate-200 text-sm">
          <span class="text-blue-400">🎞</span>
          <span>Video Upload</span>
        </div>

        <label
          for="recapVideoFileInput"
          id="recapDropzoneBox"
          class="border-2 border-dashed border-slate-700/80 hover:border-blue-500 rounded-2xl p-6 text-center cursor-pointer transition-all bg-[#080d1a] hover:bg-[#0c1426] block group"
        >
          <div class="space-y-2 pointer-events-none">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              🎬
            </div>
            <p class="text-xs font-bold text-slate-100" id="recapPromptText">Drag & drop a video file</p>
            <p class="text-[10px] text-slate-400 font-mono">mp4, mov, mkv, webm · max 500MB</p>
            <div class="pt-2">
              <span class="inline-block px-5 py-2 rounded-xl bg-[#0e1628] hover:bg-slate-800 text-slate-200 font-bold text-xs border border-slate-700/80 shadow-md transition-all">
                Browse
              </span>
            </div>
          </div>
        </label>

        <!-- Video Preview Container with Draggable Blur Box -->
        <div id="recapVideoPreviewBox" class="hidden space-y-3 bg-[#080d1a] border border-blue-500/40 rounded-2xl p-3.5">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-blue-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Loaded Video</span>
            </span>
            <label for="recapVideoFileInput" class="text-blue-400 hover:underline cursor-pointer text-[11px] font-bold">Change</label>
          </div>

          <div id="videoContainerWrapper" class="relative overflow-hidden rounded-xl bg-black border border-slate-800 aspect-video flex items-center justify-center select-none">
            <video id="recapVideoPlayerEl" controls playsinline muted class="w-full h-full object-contain transition-all duration-300"></video>

            <!-- Moveable Draggable Blur Box Overlay -->
            <div
              id="draggableBlurBox"
              class="absolute z-20 border-2 border-dashed border-cyan-400 bg-cyan-500/20 backdrop-blur-md rounded-lg hidden flex flex-col justify-between p-1 shadow-2xl"
              style="width: 140px; height: 45px; left: 30%; top: 70%;"
            >
              <div class="text-[9px] font-bold text-cyan-200 px-1 bg-black/60 rounded self-start">Blur Zone ✥</div>
              <div class="text-[8px] text-slate-300 text-right pr-1">ဖုံးရန် ဆွဲရွှေ့ပါ</div>
            </div>

            <!-- Live subtitle preview badge -->
            <div id="recapLiveSubOverlay" class="absolute bottom-2 inset-x-2 text-center pointer-events-none hidden z-10">
              <span class="inline-block bg-black/85 text-amber-300 px-3 py-1 rounded-lg text-xs font-bold shadow-xl border border-black/50" id="recapSubSampleText">
                မြန်မာ Movie Recap စာသား
              </span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 truncate" id="recapMediaNameTag">video.mp4</div>
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 text-blue-400 font-bold" id="recapMediaSizeTag">0 MB</div>
          </div>
        </div>
      </div>

      <!-- 2. OUTPUT FORMAT (ASPECT RATIO CARDS) -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3 shadow-2xl backdrop-blur-md">
        <div class="flex items-center gap-2 font-bold text-slate-200 text-sm">
          <span class="text-blue-400">❖</span>
          <span>Output Format</span>
          <span class="text-[11px] font-normal text-slate-400 font-mono">Aspect ratio</span>
        </div>

        <div class="grid grid-cols-2 gap-2.5 text-center text-xs">
          <div onclick="selectAspectRatio('16:9')" id="aspectCard16_9" class="aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-8 h-4.5 rounded-sm border-2 border-slate-400 aspect-video mb-1"></div>
            <span class="font-bold text-slate-100 block">YouTube</span>
            <span class="text-[10px] text-slate-400 block font-mono">16:9 Landscape</span>
          </div>

          <div onclick="selectAspectRatio('9:16')" id="aspectCard9_16" class="aspect-card p-4 rounded-2xl bg-blue-950/40 border-2 border-blue-500 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center ring-1 ring-blue-500/50 shadow-lg shadow-blue-500/20">
            <div class="w-4 h-7 rounded-sm border-2 border-blue-400 aspect-[9/16] mb-1"></div>
            <span class="font-bold text-blue-300 block">TikTok</span>
            <span class="text-[10px] text-blue-400/90 block font-mono">9:16 Portrait</span>
          </div>

          <div onclick="selectAspectRatio('1:1')" id="aspectCard1_1" class="aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-5 h-5 rounded-sm border-2 border-slate-400 mb-1"></div>
            <span class="font-bold text-slate-100 block">Square</span>
            <span class="text-[10px] text-slate-400 block font-mono">1:1</span>
          </div>

          <div onclick="selectAspectRatio('4:3')" id="aspectCard4_3" class="aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-6 h-4.5 rounded-sm border-2 border-slate-400 aspect-[4/3] mb-1"></div>
            <span class="font-bold text-slate-100 block">Classic</span>
            <span class="text-[10px] text-slate-400 block font-mono">4:3</span>
          </div>

          <div onclick="selectAspectRatio('3:4')" id="aspectCard3_4" class="aspect-card col-span-2 p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-4.5 h-6 rounded-sm border-2 border-slate-400 aspect-[3/4] mb-1"></div>
            <span class="font-bold text-slate-100 block">Portrait</span>
            <span class="text-[10px] text-slate-400 block font-mono">3:4</span>
          </div>
        </div>
      </div>

      <!-- 3. LANGUAGES & VOICE SELECTORS -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs">
        <div class="space-y-1.5">
          <label class="font-bold text-slate-300 flex items-center gap-1.5">
            <span>🌐</span>
            <span>Source Language ဗီဒီယိုထဲက ပြောသည့် ဘာသာ</span>
          </label>
          <div class="relative">
            <select id="recapSourceLangSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none pr-10">
              <option value="auto">Auto-detect အလိုအလျောက်</option>
              <option value="zh">Chinese 中文</option>
              <option value="en">English</option>
            </select>
            <div class="pointer-events-none absolute right-3.5 top-3.5 text-slate-400">▼</div>
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="font-bold text-slate-300 flex items-center gap-1.5">
            <span>🌐</span>
            <span>Target Language ထွက်မည့် ဘာသာစကား</span>
          </label>
          <div class="relative">
            <select id="recapTargetLangSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none pr-10">
              <option value="my">Burmese မြန်မာ</option>
            </select>
            <div class="pointer-events-none absolute right-3.5 top-3.5 text-slate-400">▼</div>
          </div>
        </div>

        <!-- Voice Selection -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between font-bold text-slate-300">
            <span class="flex items-center gap-1.5">
              <span>🔊</span>
              <span>Voice အသံရွေးရန်</span>
            </span>
            <button type="button" onclick="playRecapVoiceSample(event)" class="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 bg-blue-950/60 border border-blue-800/60 px-2 py-0.5 rounded-lg transition-all">
              <span id="recapSampleIcon">🔈</span>
              <span id="recapSampleText">စမ်းနားထောင်</span>
            </button>
          </div>
          <div class="relative">
            <select id="recapVoiceSelect" onchange="handleRecapVoiceChanged(event)" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none pr-10">
              <!-- 13 Voices dynamically populated -->
            </select>
            <div class="pointer-events-none absolute right-3.5 top-3.5 text-slate-400">▼</div>
          </div>
        </div>
      </div>

      <!-- 4. EFFECTS WITH ADVANCED COLOR GRADING, BLUR BOX & BYPASS ZOOM -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs">
        <div class="border-b border-slate-800 pb-2 flex items-center justify-between">
          <span class="font-bold text-slate-200 text-sm">Effects</span>
          <span class="text-[10px] text-slate-500 font-mono">Default OFF · tap to enable</span>
        </div>

        <!-- Mirror Effect -->
        <div class="flex items-center justify-between py-1">
          <div>
            <div class="font-bold text-slate-200">Mirror Effect</div>
            <div class="text-[10px] text-slate-400">ဗီဒီယို ပြောင်းပြန်လှန်ရန်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectMirrorSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectMirrorSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Color Grading (Bright 15+, Sat 15+, Warmth 15+, Contrast 15+, Tint 5+) -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200 flex items-center gap-1.5">
              <span>Color Grading</span>
              <span class="text-[9px] px-1.5 py-0.2 bg-blue-950 text-blue-300 rounded font-mono">Pro 15+</span>
            </div>
            <div class="text-[10px] text-slate-400">မူရင်းထက် ပိုမိုကြည်လင်ထင်ရှားစေရန် ကာလာတင်မည်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectColorGradingSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectColorGradingSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Copyright Bypass (Dynamic Zoom) -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200 flex items-center gap-1">
              <span>Copyright Bypass (Zoom)</span>
              <span class="text-[9px] text-amber-400">⚡</span>
            </div>
            <div class="text-[10px] text-slate-400">Copyright လွတ်အောင် Zoom ကစားပေးမည်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectBypassZoomSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectBypassZoomSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Blur (Moveable Box) -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200">Blur (Moveable Box)</div>
            <div class="text-[10px] text-slate-400">ဖုံးချင်တဲ့ နေရာသို့ Box လေးဆွဲရွှေ့ပြီး ဝါးထားမည်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectBlurSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectBlurSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Photo Logo -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200">Photo Logo</div>
            <div class="text-[10px] text-slate-400">ဓာတ်ပုံလိုဂို ထည့်ရန်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectLogoSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectLogoSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Add Subtitles -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200">Add Subtitles <span class="text-[10px] text-emerald-400 font-normal">(Included in free trial)</span></div>
            <div class="text-[10px] text-slate-400">ဗီဒီယိုပေါ်တွင် မြန်မာစာသား အစာထိုးရန်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectSubtitleSwitch" checked onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectSubtitleSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- 5. VOICE SETTINGS CARD WITH PACING SYNC -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs">
        <div class="border-b border-slate-800 pb-2 font-bold text-slate-200 text-sm flex items-center gap-2">
          <span class="text-blue-400">⚙</span>
          <span>Voice Settings</span>
        </div>

        <div class="space-y-1.5">
          <label class="font-bold text-slate-300 block">Voice Style အသံပုံစံ</label>
          <div class="relative">
            <select id="recapVoiceStyleSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none pr-10">
              <option value="narrator">Narrator ဇာတ်ကြောင်းပြန်</option>
              <option value="storytelling">Storytelling ပုံပြင်/ဝတ္ထု</option>
              <option value="dramatic">Dramatic စိတ်လှုပ်ရှားဖွယ်</option>
              <option value="natural">Natural သဘာဝစကားပြော</option>
            </select>
            <div class="pointer-events-none absolute right-3.5 top-3.5 text-slate-400">▼</div>
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="font-bold text-slate-300 block">Tone အသံအနေအထား</label>
          <div class="relative">
            <select id="recapToneSelect" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-slate-100 font-bold focus:outline-none focus:border-blue-500 appearance-none pr-10">
              <option value="neutral">Neutral သာမန်</option>
              <option value="deep">Deep လေးနက်</option>
              <option value="warm">Warm နွေးထွေး</option>
              <option value="crisp">Crisp ကြည်လင်</option>
            </select>
            <div class="pointer-events-none absolute right-3.5 top-3.5 text-slate-400">▼</div>
          </div>
        </div>

        <!-- Voice Speed Slider (1.00x - 1.20x auto-syncs with video pacing) -->
        <div class="space-y-2 pt-1 border-t border-slate-800/80">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-300 font-bold">Voice Speed (အသံနှင့် ဗီဒီယို တစ်ပြိုင်နက် ချိန်ညှိမှု)</span>
            <span id="recapSpeedValTag" class="font-mono text-blue-400 font-bold">1.00x</span>
          </div>
          <div class="flex items-center gap-3">
            <button type="button" onclick="adjustRecapSpeed(-2)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">−</button>
            <input id="recapSpeedRange" type="range" min="-20" max="25" step="2" value="0" class="w-full accent-blue-500 cursor-pointer" oninput="syncRecapSliders()" />
            <button type="button" onclick="adjustRecapSpeed(2)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">+</button>
          </div>
        </div>

        <div class="space-y-2 pt-1">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-300 font-bold">Pitch အသံအနိမ့်အမြင့်</span>
            <span id="recapPitchValTag" class="font-mono text-blue-400 font-bold">Normal</span>
          </div>
          <div class="flex items-center gap-3">
            <button type="button" onclick="adjustRecapPitch(-1)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">−</button>
            <input id="recapPitchRange" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-blue-500 cursor-pointer" oninput="syncRecapSliders()" />
            <button type="button" onclick="adjustRecapPitch(1)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">+</button>
          </div>
        </div>
      </div>

      <!-- 6. MAIN GENERATE RECAP BUTTON -->
      <button
        id="generateRecapBtn"
        type="button"
        onclick="executeAutoRecapVdWorkflow()"
        class="w-full py-4 rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 active:scale-[0.99] text-white font-extrabold text-sm sm:text-base shadow-2xl glow-btn flex items-center justify-center gap-2.5 transition-all"
      >
        <span id="recapSpinner" class="hidden animate-spin">🌀</span>
        <span id="recapIcon">✨</span>
        <span id="recapBtnLabel">Generate Recap</span>
      </button>

      <!-- 7. REAL EXPORTED VIDEO PLAYER & DOWNLOAD CARD -->
      <div id="recapResultCard" class="hidden bg-[#0f172b]/95 border border-emerald-500/50 rounded-3xl p-5 space-y-4 shadow-2xl backdrop-blur-md">
        <div class="flex justify-between items-center text-xs">
          <span class="font-bold text-emerald-400 flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Rendered Video Ready (အသံနှင့် ဗီဒီယို ပေါင်းစပ်ပြီး)</span>
          </span>
          <span class="text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">Merged Video</span>
        </div>

        <div class="relative overflow-hidden rounded-2xl bg-black border border-slate-800 flex items-center justify-center max-h-80">
          <video id="finalRenderedVideoEl" controls playsinline class="w-full h-full object-contain"></video>
        </div>

        <div class="space-y-1.5 text-xs">
          <label class="font-bold text-slate-300">Generated Pure Burmese Recap Voiceover Script:</label>
          <textarea id="recapFinalScriptArea" rows="4" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-3 text-slate-200 text-xs custom-scroll" readonly></textarea>
        </div>

        <div class="space-y-2 pt-1">
          <button
            id="downloadVideoFileBtn"
            type="button"
            onclick="downloadExportedVideoFile()"
            class="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:brightness-110 text-white font-extrabold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-xl shadow-emerald-600/30 transition-all active:scale-95"
          >
            <span>📥</span>
            <span>Download Exported Video (.mp4 / .webm)</span>
          </button>

          <button
            type="button"
            onclick="downloadRecapMp3Audio()"
            class="w-full py-2.5 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-blue-300 font-bold text-xs flex items-center justify-center gap-1.5"
          >
            <span>🎵</span>
            <span>Download Audio Voiceover Only (.mp3)</span>
          </button>
        </div>
      </div>

    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 2: AI TRANSCRIBER & SCRIPT STUDIO                                    -->
    <!-- ========================================================================= -->
    <div id="panelTranscriber" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl">
        <div class="flex items-center gap-2 font-bold text-slate-200 text-sm border-b border-slate-800 pb-2.5">
          <span class="text-blue-400">📤</span>
          <span>File Upload</span>
        </div>

        <label
          for="transVideoFileInput"
          id="transDropzoneLabelBox"
          class="border-2 border-dashed border-slate-700/80 hover:border-blue-500 rounded-2xl p-6 text-center cursor-pointer transition-all bg-[#080d1a] hover:bg-[#0c1426] block group"
        >
          <div class="space-y-2 pointer-events-none">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              🎧
            </div>
            <p class="text-xs font-bold text-slate-100" id="transUploadPrompt">Drag & drop a video or audio file</p>
            <p class="text-[10px] text-slate-400 font-mono">mp4, mov, mp3, wav, m4a · max 200MB</p>
            <div class="pt-2">
              <span class="inline-block px-5 py-2 rounded-xl bg-[#0e1628] hover:bg-slate-800 text-slate-200 font-bold text-xs border border-slate-700/80 shadow-md transition-all">
                Browse
              </span>
            </div>
          </div>
        </label>

        <div id="transVideoPreviewBox" class="hidden space-y-3 bg-[#080d1a] border border-blue-500/40 rounded-2xl p-3.5">
          <video id="transVideoEl" controls playsinline muted class="w-full rounded-xl max-h-48 bg-black"></video>
          <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 truncate" id="transMediaName">video.mp4</div>
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 text-blue-400 font-bold" id="transMediaSize">0 MB</div>
          </div>
        </div>

        <button
          id="transcribeExecuteBtn"
          onclick="executeTranscribeProcess()"
          class="w-full py-4 rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 active:scale-[0.99] text-white font-extrabold text-sm glow-btn flex items-center justify-center gap-2.5 transition-all"
        >
          <span id="transSpinner" class="hidden animate-spin">🌀</span>
          <span>Transcribe</span>
        </button>

        <div class="space-y-2 pt-2 border-t border-slate-800">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-slate-200">Transcript</span>
            <button onclick="copyTranscribedText()" class="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-bold text-xs">Copy</button>
          </div>
          <textarea id="transcriptOutputArea" rows="6" placeholder="Transcribed text will appear here." class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-4 text-xs leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 custom-scroll resize-y"></textarea>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 3: TTS VOICE OVER STUDIO                                             -->
    <!-- ========================================================================= -->
    <div id="panelTts" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl">
        <div class="flex items-center justify-between text-xs border-b border-slate-800 pb-2.5">
          <span class="font-bold text-blue-400 text-sm">📄 Burmese Script</span>
          <button onclick="clearTtsText()" class="text-slate-400 hover:text-rose-400 font-bold">Clear</button>
        </div>
        <textarea id="ttsInputTextArea" rows="5" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-4 text-xs leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 custom-scroll resize-y">သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>
        <button onclick="handleGenerateVoiceover()" class="w-full py-4 rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:brightness-110 text-white font-extrabold text-sm glow-btn">Generate Voiceover</button>
        <div id="activePlayerCard" class="hidden space-y-2 pt-2 border-t border-slate-800">
          <audio id="mainAudioPlayerEl" controls class="w-full"></audio>
          <button onclick="downloadCurrentGeneratedMp3()" class="w-full py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs">Download MP3</button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 4: AUTO DUBBING MODE                                                 -->
    <!-- ========================================================================= -->
    <div id="panelDubbing" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-cyan-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🎧</span><span>Auto Dubbing Mode</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">
          Translate original speech with timestamps and replace the audio with a synchronized Burmese AI voiceover.
        </p>
        <button onclick="switchStudioView('recapvd')" class="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold">
          Open Auto Recap VD
        </button>
      </div>
    </div>

  </main>

  <!-- Clean Footer -->
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

  <!-- Sample Audio Element -->
  <audio id="samplePreviewAudio" class="hidden"></audio>

  <!-- API Key Modal -->
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
    // 13 Character Voices Catalog with Gender Greetings
    const PERSONAS = [
      { id: "tayza", name: "Tayza", gender: "men", badge: "Male", role: "ရင့်ကျက်ပြတ်သားသော Movie Recap အသံ (Brian)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aung-ye-linn", name: "Aung Ye' Linn", gender: "men", badge: "Male", role: "နွေးထွေးတည်ငြိမ်သော ဇာတ်ကြောင်းပြောဟန် (Andrew)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "chue-lay", name: "Chue Lay", gender: "women", badge: "Female", role: "ချိုသာကြည်လင် ခေတ်မီဆန်းသစ်သော အမျိုးသမီးသံ (Ava)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "n-kai-yar", name: "N Kai Yar", gender: "women", badge: "Female", role: "နုပျိုသွက်လက်သော အသံဟန် (Emma)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nilar", name: "Nilar", gender: "women", badge: "Female", role: "ကြည်လင်ချိုသာသော ဇာတ်ကြောင်းပြောသံ (မူရင်းမြန်မာ)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "thiha", name: "Thiha", gender: "men", badge: "Male", role: "တည်ကြည်လေးနက်သော အမျိုးသားအသံ (မူရင်းမြန်မာ)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "phyo-ngwe-soe", name: "Phyo Ngwe Soe", gender: "men", badge: "Male", role: "စိတ်လှုပ်ရှားဖွယ် Action ဇာတ်လမ်းပြောဟန် (Florian)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "sinn-tiyar", name: "Sinn Tiyar", gender: "women", badge: "Female", role: "ညင်သာအေးချမ်းသော စာပေ/ပုံပြင်ဖတ်ကြားသံ (Seraphina)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nay-win", name: "Nay Win", gender: "men", badge: "Male", role: "လန်းဆန်းတက်ကြွသော လူငယ်စကားပြောဟန် (Remy)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "eaindra-bo", name: "Eaindra Bo", gender: "women", badge: "Female", role: "ပရော်ဖက်ရှင်နယ် တင်ဆက်သူပုံစံ အမျိုးသမီးသံ (Vivienne)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "bunny-phyoe", name: "Bunny Phyoe", gender: "men", badge: "Male", role: "နက်ရှိုင်းစွဲမက်ဖွယ် ဩဇာပြည့်ဝသောအသံ (Giuseppe)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "ji-chaung-wook", name: "Ji Chaung Wook", gender: "men", badge: "Male", role: "နူးညံ့သိမ်မွေ့သော စီးရီးဇာတ်လမ်းပြောသံ (Hyunsu)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aye-thidar", name: "Aye Thidar", gender: "women", badge: "Female", role: "တက်ကြွပျော်ရွှင်ဖွယ် ခေတ်မီအမျိုးသမီးသံ (Thalita)", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" }
    ];

    let currentSelectedVoiceId = "tayza";
    let isSampleAudioPlaying = false;
    let selectedRecapAspect = "9:16";
    let currentUploadedRecapFile = null;
    let generatedRecapAudioBlob = null;
    let exportedRenderedVideoBlob = null;
    let videoDurationSeconds = 0;

    // Draggable Blur Box State (Normalized 0.0 - 1.0)
    let blurBoxRect = { x: 0.2, y: 0.72, w: 0.6, h: 0.16 };
    let isDraggingBlurBox = false;
    let dragStartX = 0, dragStartY = 0;

    // Load initial keys
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
      const pRecap = document.getElementById("panelRecapVd");
      const pTrans = document.getElementById("panelTranscriber");
      const pTts = document.getElementById("panelTts");
      const pDub = document.getElementById("panelDubbing");

      [pRecap, pTrans, pTts, pDub].forEach(p => p.classList.add("hidden"));

      if (tool === "transcriber") {
        pTrans.classList.remove("hidden");
      } else if (tool === "tts") {
        pTts.classList.remove("hidden");
      } else if (tool === "dubbing") {
        pDub.classList.remove("hidden");
      } else {
        pRecap.classList.remove("hidden");
        populateRecapVoiceDropdown();
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

    // Auto Recap VD Dropdown
    function populateRecapVoiceDropdown() {
      const dd = document.getElementById("recapVoiceSelect");
      dd.innerHTML = PERSONAS.map(p => `
        <option value="${p.id}" ${p.id === currentSelectedVoiceId ? 'selected' : ''}>
          ${p.name} (${p.badge}) - ${p.role}
        </option>
      `).join("");
    }

    function handleRecapVoiceChanged(e) {
      currentSelectedVoiceId = e.target.value;
      const p = PERSONAS.find(x => x.id === currentSelectedVoiceId);
      showToast(`Selected voice: ${p.name}`, "info");
    }

    function selectAspectRatio(ratio) {
      selectedRecapAspect = ratio;
      const cards = ["16:9", "9:16", "1:1", "4:3", "3:4"];
      cards.forEach(r => {
        const id = `aspectCard${r.replace(":", "_")}`;
        const el = document.getElementById(id);
        if (el) {
          if (r === ratio) {
            el.className = "aspect-card p-4 rounded-2xl bg-blue-950/40 border-2 border-blue-500 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center ring-1 ring-blue-500/50 shadow-lg shadow-blue-500/20";
          } else {
            el.className = "aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center";
          }
        }
      });
      showToast(`Output format set to: ${ratio}`, "info");
      toggleEffectPreview();
    }

    document.getElementById("recapVideoFileInput").addEventListener("change", function(e) {
      const file = this.files && this.files[0];
      if (!file) return;

      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      if (file.size > 500 * 1024 * 1024) {
        showToast(`File size is ${sizeMB}MB. Max 500MB allowed`, "error");
        return;
      }

      currentUploadedRecapFile = file;
      document.getElementById("recapMediaNameTag").innerText = file.name;
      document.getElementById("recapMediaSizeTag").innerText = `${sizeMB} MB`;
      document.getElementById("recapDropzoneBox").classList.add("hidden");
      document.getElementById("recapVideoPreviewBox").classList.remove("hidden");

      const vEl = document.getElementById("recapVideoPlayerEl");
      vEl.src = URL.createObjectURL(file);

      vEl.onloadedmetadata = () => {
        videoDurationSeconds = Math.round(vEl.duration) || 180;
        console.log("Loaded source video duration:", videoDurationSeconds);
      };

      toggleEffectPreview();
      showToast(`Video loaded: ${file.name} (${sizeMB} MB)`, "success");
    });

    // Setup Draggable Blur Box Interactions
    const blurBoxEl = document.getElementById("draggableBlurBox");
    const containerWrapper = document.getElementById("videoContainerWrapper");

    function initBlurBoxDrag() {
      blurBoxEl.addEventListener("mousedown", onDragStart);
      blurBoxEl.addEventListener("touchstart", onDragStart, { passive: false });
      window.addEventListener("mousemove", onDragMove);
      window.addEventListener("touchmove", onDragMove, { passive: false });
      window.addEventListener("mouseup", onDragEnd);
      window.addEventListener("touchend", onDragEnd);
    }

    function onDragStart(e) {
      isDraggingBlurBox = true;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const rect = blurBoxEl.getBoundingClientRect();
      dragStartX = clientX - rect.left;
      dragStartY = clientY - rect.top;
      e.preventDefault();
    }

    function onDragMove(e) {
      if (!isDraggingBlurBox) return;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const containerRect = containerWrapper.getBoundingClientRect();

      let left = clientX - containerRect.left - dragStartX;
      let top = clientY - containerRect.top - dragStartY;

      const maxLeft = containerRect.width - blurBoxEl.offsetWidth;
      const maxTop = containerRect.height - blurBoxEl.offsetHeight;

      left = Math.max(0, Math.min(left, maxLeft));
      top = Math.max(0, Math.min(top, maxTop));

      blurBoxEl.style.left = `${left}px`;
      blurBoxEl.style.top = `${top}px`;

      // Update normalized coordinates for canvas export rendering
      blurBoxRect.x = left / containerRect.width;
      blurBoxRect.y = top / containerRect.height;
      blurBoxRect.w = blurBoxEl.offsetWidth / containerRect.width;
      blurBoxRect.h = blurBoxEl.offsetHeight / containerRect.height;

      if (e.cancelable) e.preventDefault();
    }

    function onDragEnd() {
      isDraggingBlurBox = false;
    }

    initBlurBoxDrag();

    function toggleEffectPreview() {
      const vEl = document.getElementById("recapVideoPlayerEl");
      const isMirror = document.getElementById("effectMirrorSwitch")?.checked;
      const isColor = document.getElementById("effectColorGradingSwitch")?.checked;
      const isZoom = document.getElementById("effectBypassZoomSwitch")?.checked;
      const isBlur = document.getElementById("effectBlurSwitch")?.checked;
      const isSub = document.getElementById("effectSubtitleSwitch")?.checked;
      const subOverlay = document.getElementById("recapLiveSubOverlay");

      // Transforms
      let transformStr = "";
      if (isMirror) transformStr += "scaleX(-1) ";
      if (isZoom) transformStr += "scale(1.12) ";
      vEl.style.transform = transformStr || "none";

      // Color Grading requested: Bright 15+, Sat 15+, Warmth 15+, Contrast 15+, Tint 5+
      let filterStr = "";
      if (isColor) {
        filterStr += "brightness(1.15) contrast(1.15) saturate(1.15) sepia(0.15) hue-rotate(-5deg) ";
      }
      vEl.style.filter = filterStr || "none";

      // Moveable Blur Box visibility
      if (isBlur) {
        blurBoxEl.classList.remove("hidden");
      } else {
        blurBoxEl.classList.add("hidden");
      }

      if (subOverlay) {
        if (isSub) subOverlay.classList.remove("hidden"); else subOverlay.classList.add("hidden");
      }
    }

    function syncRecapSliders() {
      const s = parseInt(document.getElementById("recapSpeedRange").value);
      const p = parseInt(document.getElementById("recapPitchRange").value);
      const mult = (1 + s / 100).toFixed(2);
      document.getElementById("recapSpeedValTag").innerText = `${mult}x`;
      document.getElementById("recapPitchValTag").innerText = p === 0 ? "Normal" : (p > 0 ? `+${p}Hz` : `${p}Hz`);

      // Realtime video playback speed synchronization
      const vEl = document.getElementById("recapVideoPlayerEl");
      if (vEl) {
        vEl.playbackRate = Math.max(0.7, Math.min(1.8, parseFloat(mult)));
      }
    }

    function adjustRecapSpeed(delta) {
      const el = document.getElementById("recapSpeedRange");
      el.value = Math.max(-20, Math.min(25, parseInt(el.value) + delta));
      syncRecapSliders();
    }

    function adjustRecapPitch(delta) {
      const el = document.getElementById("recapPitchRange");
      el.value = Math.max(-15, Math.min(15, parseInt(el.value) + delta));
      syncRecapSliders();
    }

    async function playRecapVoiceSample(e) {
      if (e) e.stopPropagation();
      const pAudio = document.getElementById("samplePreviewAudio");
      const icon = document.getElementById("recapSampleIcon");
      const txt = document.getElementById("recapSampleText");

      if (isSampleAudioPlaying) {
        pAudio.pause();
        isSampleAudioPlaying = false;
        icon.innerText = "🔈";
        txt.innerText = "စမ်းနားထောင်";
        return;
      }

      icon.innerText = "⏹";
      txt.innerText = "ရပ်မည်";
      isSampleAudioPlaying = true;

      try {
        let res = await fetch(`/api/preview/${currentSelectedVoiceId}`);
        if (!res.ok) res = await fetch(`/preview/${currentSelectedVoiceId}`);
        if (res.ok) {
          const blob = await res.blob();
          pAudio.src = URL.createObjectURL(blob);
          await pAudio.play();
          return;
        }
      } catch (err) {}

      isSampleAudioPlaying = false;
      icon.innerText = "🔈";
      txt.innerText = "စမ်းနားထောင်";
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ", "error");
    }

    document.getElementById("samplePreviewAudio").onended = () => {
      isSampleAudioPlaying = false;
      document.getElementById("recapSampleIcon").innerText = "🔈";
      document.getElementById("recapSampleText").innerText = "စမ်းနားထောင်";
    };

    // =========================================================================
    // ADVANCED COMPOSITOR: DURATION PACING, COLOR GRADING, BLUR BOX & ZOOM
    // =========================================================================
    async function renderAndExportComposedVideo(videoFile, audioBlob, scriptText, targetAspect, effects, targetDuration, playbackSpeed) {
      return new Promise(async (resolve, reject) => {
        try {
          const canvas = document.getElementById("offscreenRenderCanvas");
          const ctx = canvas.getContext("2d");

          let targetW = 720, targetH = 1280;
          if (targetAspect === "16:9") { targetW = 1280; targetH = 720; }
          else if (targetAspect === "1:1") { targetW = 720; targetH = 720; }
          else if (targetAspect === "4:3") { targetW = 960; targetH = 720; }
          else if (targetAspect === "3:4") { targetW = 720; targetH = 960; }

          canvas.width = targetW;
          canvas.height = targetH;

          const sourceVideo = document.createElement("video");
          sourceVideo.src = URL.createObjectURL(videoFile);
          sourceVideo.muted = true;
          sourceVideo.playsInline = true;
          await new Promise((r) => { sourceVideo.onloadedmetadata = r; });

          // Synchronize video speed with voice speed!
          sourceVideo.playbackRate = playbackSpeed || 1.0;

          const speechAudio = new Audio(URL.createObjectURL(audioBlob));

          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          const audioCtx = new AudioContextClass();
          const sourceNode = audioCtx.createMediaElementSource(speechAudio);
          const audioDestNode = audioCtx.createMediaStreamDestination();
          sourceNode.connect(audioDestNode);

          const canvasStream = canvas.captureStream(30);
          const mixedStream = new MediaStream([
            ...canvasStream.getVideoTracks(),
            ...audioDestNode.stream.getAudioTracks()
          ]);

          let mime = 'video/webm;codecs=vp9,opus';
          if (!MediaRecorder.isTypeSupported(mime)) mime = 'video/webm';
          if (!MediaRecorder.isTypeSupported(mime)) mime = 'video/mp4';

          const mediaRecorder = new MediaRecorder(mixedStream, { mimeType: mime });
          const recordedChunks = [];

          mediaRecorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) recordedChunks.push(e.data);
          };

          mediaRecorder.onstop = () => {
            const finalBlob = new Blob(recordedChunks, { type: mime });
            resolve(finalBlob);
          };

          let animationFrameId = null;
          const sentences = scriptText.split(/(?<=[။!?\n])/).filter(s => s.trim().length > 0);
          let startTimeStamp = performance.now();

          // Duration pacing: Ensure video runs for the intended length (at least speech duration or video length)
          const totalExpectedDuration = Math.max(12, Math.min(targetDuration || 180, 480));

          function renderFrame(now) {
            const elapsed = (now - startTimeStamp) / 1000;

            // Stop condition: when speech finishes and video has matched duration
            if (elapsed >= totalExpectedDuration || (speechAudio.ended && sourceVideo.currentTime >= (sourceVideo.duration * 0.95))) {
              cancelAnimationFrame(animationFrameId);
              mediaRecorder.stop();
              return;
            }

            ctx.fillStyle = "#000000";
            ctx.fillRect(0, 0, targetW, targetH);

            ctx.save();

            // 1. Mirror Transform
            if (effects.isMirror) {
              ctx.translate(targetW, 0);
              ctx.scale(-1, 1);
            }

            // 2. Copyright Bypass Zoom effect (Smooth slow breathing zoom to bypass detection)
            let zoomScale = 1.0;
            if (effects.isZoom) {
              zoomScale = 1.10 + 0.04 * Math.sin(elapsed * 0.4);
              ctx.translate(targetW / 2, targetH / 2);
              ctx.scale(zoomScale, zoomScale);
              ctx.translate(-targetW / 2, -targetH / 2);
            }

            // 3. Color Grading Filter (Bright 15+, Sat 15+, Warmth 15+, Contrast 15+, Tint 5+)
            if (effects.isColor) {
              ctx.filter = "brightness(1.15) contrast(1.15) saturate(1.15) sepia(0.15) hue-rotate(-5deg)";
            } else {
              ctx.filter = "none";
            }

            // Draw video to fill & center
            const vidRatio = sourceVideo.videoWidth / sourceVideo.videoHeight;
            const targetRatio = targetW / targetH;
            let drawW, drawH, drawX, drawY;

            if (vidRatio > targetRatio) {
              drawH = targetH;
              drawW = targetH * vidRatio;
              drawX = (targetW - drawW) / 2;
              drawY = 0;
            } else {
              drawW = targetW;
              drawH = targetW / vidRatio;
              drawX = 0;
              drawY = (targetH - drawH) / 2;
            }

            ctx.drawImage(sourceVideo, drawX, drawY, drawW, drawH);
            ctx.restore();

            // 4. Moveable Blur Zone rendering (Render blur over the exact user-moved box!)
            if (effects.isBlur) {
              const bx = blurBoxRect.x * targetW;
              const by = blurBoxRect.y * targetH;
              const bw = blurBoxRect.w * targetW;
              const bh = blurBoxRect.h * targetH;

              ctx.save();
              ctx.beginPath();
              ctx.rect(bx, by, bw, bh);
              ctx.clip();
              ctx.filter = "blur(18px)";
              ctx.drawImage(sourceVideo, drawX, drawY, drawW, drawH);
              ctx.restore();

              // Subtle frosted border
              ctx.strokeStyle = "rgba(255,255,255,0.15)";
              ctx.lineWidth = 2;
              ctx.strokeRect(bx, by, bw, bh);
            }

            // 5. Transformative Movie Recap Subtitle rendering
            if (effects.isSub && sentences.length > 0) {
              const audioDur = speechAudio.duration || totalExpectedDuration;
              const progress = Math.min(1.0, speechAudio.currentTime / audioDur);
              const curIdx = Math.min(sentences.length - 1, Math.floor(progress * sentences.length));
              const textToDraw = sentences[curIdx]?.trim() || "";

              if (textToDraw) {
                ctx.save();
                ctx.font = `bold ${Math.round(targetW * 0.038)}px Padauk, sans-serif`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";

                const subY = targetH * 0.88;
                const textWidth = ctx.measureText(textToDraw).width;
                const padX = 22, padY = 12;

                ctx.fillStyle = "rgba(0, 0, 0, 0.78)";
                ctx.roundRect(
                  targetW / 2 - textWidth / 2 - padX,
                  subY - padY,
                  textWidth + padX * 2,
                  padY * 2,
                  12
                );
                ctx.fill();

                ctx.fillStyle = "#fde047";
                ctx.fillText(textToDraw, targetW / 2, subY);
                ctx.restore();
              }
            }

            animationFrameId = requestAnimationFrame(renderFrame);
          }

          mediaRecorder.start(250);
          sourceVideo.currentTime = 0;
          speechAudio.currentTime = 0;

          await sourceVideo.play();
          await speechAudio.play();

          animationFrameId = requestAnimationFrame(renderFrame);

        } catch (err) {
          reject(err);
        }
      });
    }

    // Auto Recap VD Full Workflow
    async function executeAutoRecapVdWorkflow() {
      if (!currentUploadedRecapFile) {
        showToast("Please upload a video file first", "error");
        return;
      }

      const geminiKey = (localStorage.getItem("gemini_api_key") || "").trim();
      const groqKey = (localStorage.getItem("groq_api_key") || "").trim();

      if (!geminiKey && !groqKey) {
        showToast("Please provide Gemini or Groq API Key", "error");
        openKeysModal();
        return;
      }

      const btn = document.getElementById("generateRecapBtn");
      const spinner = document.getElementById("recapSpinner");
      const icon = document.getElementById("recapIcon");
      const label = document.getElementById("recapBtnLabel");
      const resultCard = document.getElementById("recapResultCard");
      const scriptArea = document.getElementById("recapFinalScriptArea");
      const finalVideoEl = document.getElementById("finalRenderedVideoEl");

      btn.disabled = true;
      spinner.classList.remove("hidden");
      icon.classList.add("hidden");
      label.innerText = "1/3: ဇာတ်လမ်းဇာတ်ကွက် ပြည့်စုံအောင် ရေးသားနေပါသည်...";

      try {
        // Calculate appropriate words count based on source duration (e.g. 180s video = 250-400 words)
        const durSecs = videoDurationSeconds || 180;
        const targetWords = Math.max(160, Math.min(500, Math.round(durSecs * 2.2)));

        const prompt = `
သင်သည် နာမည်ကြီး မြန်မာ Movie Recap (ရုပ်ရှင်ဇာတ်ကြောင်းပြန်) အစီအစဉ် ဖန်တီးသူ ဖြစ်သည်။
ဗီဒီယို ကြာချိန် ခန့်မှန်းခြေ ${durSecs} စက္ကန့်စာနှင့် ကိုက်ညီစေရန်အတွက် ဇာတ်လမ်းအစ၊ အလယ်၊ ဇာတ်ကွက်အလှည့်အပြောင်းနှင့် ဇာတ်သိမ်းအထိ အစအဆုံး ပြည့်စုံသော မြန်မာစကားပြော Movie Recap Voiceover ဇာတ်ညွှန်းကို ရေးသားပေးရမည်။ (အနည်းဆုံး မြန်မာစကားလုံး ${targetWords} လုံးခန့် ပါဝင်အောင် ရေးပေးပါ)။

စည်းမျဉ်းများ:
၁။ Maid/Servant -> "အိမ်ဖော်မလေး/အိမ်အကူကောင်မလေး", Dog -> "ခွေးလေး", Father -> "အဖေကြီး", Son -> "သားဖြစ်သူ", Daughter-in-law -> "ချွေးမ" စသည့် သဘာဝနာမ်စားများကိုသာ သုံးပါ။
၂။ "ကျွန်တော်", "ကျွန်မ", "ခင်ဗျာ", "ရှင်" မသုံးရ။ ကျား/မ မရွေး ဖတ်နိုင်သော Voiceover လေသံ ဖြစ်ရမည်။
၃။ "ဒီနေ့ ဇာတ်လမ်းလေးမှာတော့...", "ကောင်မလေးက...", "အဲဒီအချိန်မှာပဲ...", "မထင်မှတ်ထားဘဲ...", "အခြေအနေတွေက ပိုဆိုးသွားပြီးတော့...", "နောက်ဆုံးမှာတော့..." စသည့် သဘာဝစကားပြော စကားဆက်များ သုံးပါ။
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
                { role: "user", content: `Write a complete ${durSecs}-second storytelling recap in Burmese covering the entire drama plot.` }
              ],
              temperature: 0.3
            })
          });
          if (res.ok) {
            const data = await res.json();
            finalScript = sanitizePureScript(data.choices?.[0]?.message?.content || "");
          }
        }

        if (!finalScript && geminiKey) {
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiKey}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contents: [{ parts: [{ text: `${prompt}\n\nWrite pure Burmese movie recap script for full length.` }] }]
            })
          });
          if (res.ok) {
            const data = await res.json();
            finalScript = sanitizePureScript(data.candidates?.[0]?.content?.parts?.[0]?.text || "");
          }
        }

        if (!finalScript) {
          finalScript = "ဒီနေ့ ဇာတ်လမ်းလေးမှာတော့ အိမ်ဖော်မလေးဟာ အိမ်ရှင်တွေ မသိအောင် တစ်စုံတစ်ခုကို လျှို့ဝှက် လုပ်ဆောင်နေခဲ့တာ ဖြစ်ပါတယ်။ အဲဒီအချိန်မှာပဲ သားဖြစ်သူ ပြန်ရောက်လာပြီး မထင်မှတ်ထားတဲ့ အမှန်တရားတစ်ခုကို သိရှိသွားခဲ့ပါတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း အလှည့်အပြောင်းတွေ ဖြစ်ပျက်သွားခဲ့ပြီး နောက်ဆုံးမှာတော့ အားလုံးအတွက် မေ့မရနိုင်တဲ့ အဖြစ်ဆိုးတစ်ခု ဖြစ်သွားခဲ့ပါတယ်။";
        }

        scriptArea.value = finalScript;

        // Step 2: Voiceover generation via Edge-TTS
        label.innerText = "2/3: AI မြန်မာအသံဖိုင် ဖန်တီးနေပါသည်...";

        const speedOffset = parseInt(document.getElementById("recapSpeedRange").value);
        const pitchOffset = parseInt(document.getElementById("recapPitchRange").value);
        const speedMultiplier = (1 + speedOffset / 100);

        let ttsRes = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: finalScript,
            persona_id: currentSelectedVoiceId,
            user_rate_offset: speedOffset,
            user_pitch_offset: pitchOffset
          })
        });

        if (!ttsRes.ok) {
          ttsRes = await fetch("/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: finalScript,
              persona_id: currentSelectedVoiceId,
              user_rate_offset: speedOffset,
              user_pitch_offset: pitchOffset
            })
          });
        }

        if (ttsRes.ok) {
          generatedRecapAudioBlob = await ttsRes.blob();
        } else {
          throw new Error("Voiceover synthesis failed");
        }

        // Step 3: Real Video Compositor (Color grading + Moveable Blur + Bypass Zoom + Speed sync)
        label.innerText = "3/3: ဗီဒီယိုနှင့် အသံ ပေါင်းစပ် ထုတ်လုပ်နေပါသည်...";
        showToast("Color Grading, Blur, Zoom နှင့် အသံ ပေါင်းစပ်နေပါသည်...", "info");

        const effects = {
          isMirror: document.getElementById("effectMirrorSwitch")?.checked,
          isColor: document.getElementById("effectColorGradingSwitch")?.checked,
          isZoom: document.getElementById("effectBypassZoomSwitch")?.checked,
          isBlur: document.getElementById("effectBlurSwitch")?.checked,
          isSub: document.getElementById("effectSubtitleSwitch")?.checked
        };

        // Render full composed video
        exportedRenderedVideoBlob = await renderAndExportComposedVideo(
          currentUploadedRecapFile,
          generatedRecapAudioBlob,
          finalScript,
          selectedRecapAspect,
          effects,
          durSecs,
          speedMultiplier
        );

        finalVideoEl.src = URL.createObjectURL(exportedRenderedVideoBlob);
        resultCard.classList.remove("hidden");
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        await finalVideoEl.play();

        showToast("ဗီဒီယို ဖန်တီးမှု အပြည့်အဝ ပြီးစီးပါပြီ!", "success");

      } catch (err) {
        showToast(err.message, "error");
      } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        icon.classList.remove("hidden");
        label.innerText = "Generate Recap";
      }
    }

    function downloadExportedVideoFile() {
      if (!exportedRenderedVideoBlob) return showToast("No exported video file ready", "error");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(exportedRenderedVideoBlob);
      a.download = `Recap_Go_${selectedRecapAspect.replace(":", "x")}_${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("Downloaded Rendered Video (.mp4 / .webm)", "success");
    }

    function downloadRecapMp3Audio() {
      if (!generatedRecapAudioBlob) return showToast("No audio file ready", "error");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(generatedRecapAudioBlob);
      a.download = `Recap_Go_Voiceover_${Date.now()}.mp3`;
      document.body.appendChild(a);
      a.click();
      showToast("Downloaded Voiceover Audio MP3", "success");
    }

    function sanitizePureScript(raw) {
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
        const burmese = trimmed.match(/[\u1000-\u109F]/g);
        const english = trimmed.match(/[a-zA-Z]/g);
        if (!burmese && english && english.length > 5) continue;
        line = line.replace(/^\s*[\*\-]\s+/, '');
        filtered.push(line);
      }
      return filtered.join('\n').trim();
    }

    // Init
    populateRecapVoiceDropdown();
    syncRecapSliders();
  </script>
</body>
</html>
"""

# 13 Voices Catalog Preserved
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

@app.get("/{full_path:path}")
def catch_all_routes(full_path: str):
    return HTMLResponse(content=HTML_CONTENT)
