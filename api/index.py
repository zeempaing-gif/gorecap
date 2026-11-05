import os
import asyncio
import urllib.parse
import urllib.request
import edge_tts
from fastapi import FastAPI, HTTPException, UploadFile, File, Header
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
  <meta name="referrer" content="no-referrer">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>GoRecap Studio • AI Movie Recap</title>
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
    
    #draggableBlurBox { touch-action: none; user-select: none; cursor: move; }
    #draggableSubtitleBox { touch-action: none; user-select: none; cursor: move; }
    .resize-handle { touch-action: none; user-select: none; cursor: nwse-resize; }
    .video-cover-fill { object-fit: cover !important; }

    /* GoRecap Studio theme system */
    :root { color-scheme: dark; --app-bg:#070b16; --surface:#0e1628; --surface-2:#111d32; --line:#24324a; --ink:#e8eef9; --muted:#93a4bd; --accent:#8b5cf6; --accent-2:#6366f1; }
    html[data-theme="light"] { color-scheme:light; --app-bg:#f5f6fb; --surface:#ffffff; --surface-2:#f0f2f9; --line:#e1e5ef; --ink:#20263a; --muted:#69748b; --accent:#7651d5; --accent-2:#5b5bd6; }
    body { background:var(--app-bg) !important; color:var(--ink) !important; font-family:'Padauk','Plus Jakarta Sans',sans-serif; }
    header { background:color-mix(in srgb,var(--app-bg) 88%,transparent) !important; border-color:var(--line) !important; box-shadow:0 8px 32px rgba(0,0,0,.12) !important; }
    header h1, header .text-white { color:var(--ink) !important; }
    header p { color:var(--muted) !important; }
    main { max-width:1100px !important; }
    main [class*="bg-[#0f172b]"] { background:var(--surface) !important; border:1px solid var(--line) !important; border-radius:22px !important; box-shadow:0 12px 34px rgba(0,0,0,.10) !important; }
    main [class*="bg-[#080d1a]"] { background:var(--surface-2) !important; border-color:var(--line) !important; }
    main [class*="border-slate-800"], main [class*="border-slate-700"] { border-color:var(--line) !important; }
    main .text-slate-100, main .text-slate-200, main .text-slate-300 { color:var(--ink) !important; }
    main .text-slate-400, main .text-slate-500 { color:var(--muted) !important; }
    main textarea, main input:not([type="checkbox"]):not([type="file"]), main select { background:var(--surface-2) !important; color:var(--ink) !important; border:1px solid var(--line) !important; border-radius:13px !important; padding:12px !important; outline:none !important; }
    main textarea:focus, main input:focus, main select:focus { border-color:var(--accent) !important; box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 18%,transparent) !important; }
    main button { border-radius:14px; font-weight:700; transition:all .18s ease; }
    main button[class*="bg-blue-600"], main button[class*="bg-cyan-600"], main button[class*="bg-emerald-600"] { background:linear-gradient(135deg,var(--accent),var(--accent-2)) !important; color:#fff !important; border:1px solid transparent !important; box-shadow:0 7px 20px color-mix(in srgb,var(--accent) 22%,transparent); }
    main button[class*="bg-blue-600"]:hover, main button[class*="bg-cyan-600"]:hover, main button[class*="bg-emerald-600"]:hover { filter:brightness(1.08); transform:translateY(-1px); }
    .rg-nav { display:grid; }
    .rg-tab { min-width:0; display:flex; align-items:center; justify-content:center; gap:7px; padding:11px 8px; border:1px solid var(--line); border-radius:14px; background:var(--surface); color:var(--muted); font-size:12px; font-weight:700; box-shadow:0 3px 12px rgba(0,0,0,.06); transition:all .18s ease; }
    .rg-tab:hover { border-color:var(--accent); color:var(--ink); transform:translateY(-1px); }
    .rg-tab.is-active { background:color-mix(in srgb,var(--accent) 15%,var(--surface)); border-color:color-mix(in srgb,var(--accent) 55%,var(--line)); color:var(--ink); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--accent) 12%,transparent); }
    .rg-tab span:first-child { font-size:15px; }
    .aspect-card { background:var(--surface-2) !important; border-color:var(--line) !important; }
    .aspect-card[id*="9_16"] { background:color-mix(in srgb,var(--accent) 16%,var(--surface)) !important; border-color:var(--accent) !important; }
    #toastContainer { color:#fff !important; }
    #themeToggle { border:1px solid var(--line); background:var(--surface); color:var(--ink); }
    @media (max-width:480px) { .rg-tab { flex-direction:column; gap:3px; padding:9px 3px; font-size:10px; } .rg-tab span:first-child { font-size:16px; } main { padding-left:13px !important; padding-right:13px !important; } }
  </style>
</head>
<body class="bg-[#070b16] text-slate-100 min-h-screen flex flex-col items-center antialiased selection:bg-blue-600 selection:text-white transition-colors duration-200">

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed top-4 right-4 z-[99999] flex flex-col gap-2 pointer-events-none"></div>

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
    <div class="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-blue-600/30 font-bold text-white">
          🍀
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="text-base font-extrabold tracking-tight text-white">Recap Go</h1>
            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Pro Studio
            </span>
          </div>
          <p class="text-[10px] text-slate-400">Burmese Video Recap & Dubbing</p>
        </div>
      </div>

      <div class="flex items-center gap-2"><button id="themeToggle" onclick="toggleTheme()" class="px-3 py-2 rounded-xl text-xs font-bold" title="Toggle theme">☀️ Light</button><button onclick="openKeysModal()" class="px-3.5 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-xs font-bold shadow-sm" title="API Keys Settings">⚙️ Settings</button></div>
    </div>
    <nav class="rg-nav max-w-4xl mx-auto px-4 pb-3 grid grid-cols-4 gap-2">
      <button id="navRecap" onclick="switchStudioView('recapvd')" class="rg-tab is-active"><span>🍿</span><span>Movie Recap</span></button>
      <button id="navTranscriber" onclick="switchStudioView('transcriber')" class="rg-tab"><span>📝</span><span>Transcribe</span></button>
      <button id="navTts" onclick="switchStudioView('tts')" class="rg-tab"><span>🎙️</span><span>Voice Over</span></button>
      <button id="navDubbing" onclick="switchStudioView('dubbing')" class="rg-tab"><span>🎧</span><span>Dubbing</span></button>
    </nav>
    </div>
  </header>

  <!-- File Inputs -->
  <input type="file" id="recapVideoFileInput" accept="video/*,.mp4,.mov,.mkv,.webm" class="hidden" />
  <input type="file" id="transVideoFileInput" accept="video/*,audio/*,.mp4,.mov,.mp3,.wav,.m4a,.webm,.mkv" class="hidden" />

  <!-- Hidden Offscreen Canvas for Real Video Rendering & Export -->
  <canvas id="offscreenRenderCanvas" class="hidden"></canvas>

  <!-- Audio Player Element for Preview -->
  <audio id="globalPreviewAudio" preload="auto" playsinline class="hidden"></audio>

  <!-- Main Container -->
  <main class="max-w-3xl w-full px-4 py-6 space-y-5 flex-1">

    <!-- VIEW 1: AUTO RECAP VD -->
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
            <p class="text-[10px] text-slate-400 font-mono">mp4, mov, mkv, webm · 200MB+ Video ကို Audio ခွဲထုတ်ပြီး လုပ်ဆောင်မည်</p>
            <div class="pt-2">
              <span class="inline-block px-5 py-2 rounded-xl bg-[#0e1628] hover:bg-slate-800 text-slate-200 font-bold text-xs border border-slate-700/80 shadow-md transition-all">
                Browse
              </span>
            </div>
          </div>
        </label>

        <!-- Live Video Preview Box -->
        <div id="recapVideoPreviewBox" class="hidden space-y-3 bg-[#080d1a] border border-blue-500/40 rounded-2xl p-3.5">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-blue-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span id="aspectRatioLabelTag">Aspect: 9:16 (Zoom Fill)</span>
            </span>
            <label for="recapVideoFileInput" class="text-blue-400 hover:underline cursor-pointer text-[11px] font-bold">Change</label>
          </div>

          <div
            id="videoContainerWrapper"
            class="relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-[9/16] w-full max-w-[310px] mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300"
          >
            <video id="recapBlurredBackdropEl" class="absolute inset-0 w-full h-full object-cover filter blur-lg opacity-40 scale-110 pointer-events-none" muted playsinline></video>
            <video id="recapVideoPlayerEl" controls playsinline muted class="relative z-10 w-full h-full video-cover-fill transition-all duration-300"></video>

            <!-- Moveable Blur Box -->
            <div
              id="draggableBlurBox"
              class="absolute z-20 border-2 border-dashed border-cyan-400 bg-cyan-500/20 backdrop-blur-md rounded-xl hidden flex flex-col justify-between p-1.5 shadow-2xl"
              style="width: 160px; height: 50px; left: 24%; top: 72%;"
            >
              <div class="flex items-center justify-between text-[8px] font-bold text-cyan-200 px-1 bg-black/60 rounded">
                <span>Blur Zone ✥</span>
                <span class="text-slate-300">ဆွဲရွှေ့ပါ</span>
              </div>
              <div class="text-[7px] text-cyan-300 text-center font-mono">အောက်ထောင့်မှ အကြီးသေးဆွဲပါ ↘</div>
              <div id="blurResizeHandle" class="resize-handle w-4 h-4 bg-cyan-400 rounded-br-lg rounded-tl-md self-end cursor-nwse-resize shadow-md"></div>
            </div>

            <!-- Moveable Subtitles -->
            <div
              id="draggableSubtitleBox"
              class="absolute z-30 px-3 py-1.5 rounded-xl cursor-move shadow-2xl text-center transition-transform select-none hidden"
              style="left: 10%; top: 82%; width: 80%;"
            >
              <div class="text-[7px] text-amber-300/80 font-mono mb-0.5 pointer-events-none select-none">✥ စာတန်းထားမည့်နေရာ ရွှေ့ပါ</div>
              <span id="subPreviewSpanText" class="inline-block font-extrabold leading-relaxed drop-shadow-md">
                မြန်မာ Movie Recap စာသားနမူနာ
              </span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 truncate" id="recapMediaNameTag">video.mp4</div>
            <div class="p-2 bg-slate-900 rounded-xl border border-slate-800 text-blue-400 font-bold" id="recapMediaSizeTag">0 MB</div>
          </div>
        </div>
      </div>

      <!-- Transcript is generated automatically inside the one-click workflow -->
      <textarea id="recapSourceTranscript" class="hidden" aria-hidden="true"></textarea>

      <!-- 2. OUTPUT FORMAT -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-2 font-bold text-slate-200">
            <span class="text-blue-400">❖</span>
            <span>Output Format</span>
            <span class="text-[11px] font-normal text-slate-400 font-mono">Aspect ratio</span>
          </div>
          <span class="text-[10px] text-emerald-400 font-bold">No Black Bars</span>
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

      <!-- 3. CLEAN VOICE SELECTION DROPDOWN -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3 shadow-2xl backdrop-blur-md text-xs">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
          <span class="font-bold text-slate-200 text-sm flex items-center gap-2">
            <span class="text-blue-400">🔊</span>
            <span>Voice အသံရွေးရန်</span>
          </span>
          <span class="text-[10px] text-blue-400 font-mono">13 Voices Available</span>
        </div>

        <div>
          <button
            type="button"
            onclick="openVoiceSelectorModal(event)"
            class="w-full bg-[#080d1a] border border-slate-700/80 hover:border-blue-500 rounded-2xl p-4 flex items-center justify-between text-slate-100 font-bold transition-all shadow-lg active:scale-[0.99]"
          >
            <div class="flex items-center gap-3 truncate">
              <span class="text-blue-400 font-mono text-base tracking-tighter">||||</span>
              <span id="selectedVoiceTitleTag" class="text-sm font-bold text-white truncate">ဘန်နီဖြိုး (Male)</span>
            </div>
            <span class="text-slate-400 text-xs ml-2">▼</span>
          </button>
        </div>
      </div>

      <!-- 4. EFFECTS & BYPASS -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs">
        <div class="border-b border-slate-800 pb-2 flex items-center justify-between">
          <span class="font-bold text-slate-200 text-sm">Effects & Bypass</span>
          <span class="text-[10px] text-slate-500 font-mono">Custom Settings</span>
        </div>

        <!-- Subtitles Toggle -->
        <div class="flex items-center justify-between py-1">
          <div>
            <div class="font-bold text-slate-100 flex items-center gap-1.5">
              <span>💬 Add Subtitles (စာတန်းထိုးစနစ်)</span>
              <span class="text-[9px] px-1.5 py-0.2 bg-amber-950 text-amber-300 border border-amber-800 rounded font-mono">Interactive</span>
            </div>
            <div class="text-[10px] text-slate-400">ဖွင့်ထားပါက ဗီဒီယိုပေါ်တွင် နေရာရွှေ့နိုင်ပြီး အရောင်/အရွယ်အစား ရွေးချယ်နိုင်မည်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectSubtitleSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectSubtitleSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Color Grading -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200 flex items-center gap-1.5">
              <span>Color Grading</span>
              <span class="text-[9px] px-1.5 py-0.2 bg-emerald-950 text-emerald-300 border border-emerald-800 rounded font-mono">Pro 15+</span>
            </div>
            <div class="text-[10px] text-slate-400">Bright +15, Sat +15, Warmth +15, Contrast +15, Tint +5</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectColorGradingSwitch" checked onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectColorGradingSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Copyright Bypass (Zoom) -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
          <div>
            <div class="font-bold text-slate-200 flex items-center gap-1">
              <span>Copyright Bypass (Zoom)</span>
              <span class="text-[9px] text-amber-400">⚡</span>
            </div>
            <div class="text-[10px] text-slate-400">Copyright ကင်းလွတ်အောင် Zoom ကစားပေးမည်</div>
          </div>
          <div class="relative inline-block w-11 h-6 align-middle select-none">
            <input type="checkbox" id="effectBypassZoomSwitch" checked onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
            <label for="effectBypassZoomSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
              <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
            </label>
          </div>
        </div>

        <!-- Blur -->
        <div class="space-y-2 py-1 border-t border-slate-800/60">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-bold text-slate-200">Blur (Shape / Box)</div>
              <div class="text-[10px] text-slate-400">လိုသလို အကြီးသေးဆွဲဆန့်ပြီး စာတန်း/ရေစာ ဖုံးကွယ်မည်</div>
            </div>
            <div class="relative inline-block w-11 h-6 align-middle select-none">
              <input type="checkbox" id="effectBlurSwitch" onchange="toggleEffectPreview()" class="switch-checkbox hidden" />
              <label for="effectBlurSwitch" class="switch-label block overflow-hidden h-6 rounded-full bg-slate-800 cursor-pointer transition-colors border border-slate-700">
                <span class="switch-dot block h-6 w-6 rounded-full bg-white shadow transform transition-transform"></span>
              </label>
            </div>
          </div>

          <div id="blurDimensionControls" class="hidden p-3 rounded-2xl bg-[#080d1a] border border-slate-800 grid grid-cols-2 gap-3 text-[11px]">
            <div>
              <div class="flex justify-between text-slate-400 mb-1">
                <span>Box အကျယ် (Width)</span>
                <span id="blurWTag" class="text-cyan-400 font-mono font-bold">160px</span>
              </div>
              <input type="range" id="blurWidthSlider" min="50" max="300" step="5" value="160" oninput="adjustBlurDimensionsFromSlider()" class="w-full accent-cyan-400" />
            </div>
            <div>
              <div class="flex justify-between text-slate-400 mb-1">
                <span>Box အမြင့် (Height)</span>
                <span id="blurHTag" class="text-cyan-400 font-mono font-bold">50px</span>
              </div>
              <input type="range" id="blurHeightSlider" min="25" max="150" step="5" value="50" oninput="adjustBlurDimensionsFromSlider()" class="w-full accent-cyan-400" />
            </div>
          </div>
        </div>

        <!-- Mirror Effect -->
        <div class="flex items-center justify-between py-1 border-t border-slate-800/60">
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
      </div>

      <!-- 5. SUBTITLES FULL STYLING CARD -->
      <div id="subtitleStylingCard" class="hidden bg-[#0f172b]/95 border border-amber-500/40 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs transition-all">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
          <div class="flex items-center gap-2 font-bold text-amber-300 text-sm">
            <span>✨</span>
            <span>Subtitle Customizer</span>
          </div>
          <span class="text-[10px] text-emerald-400 font-bold">Active</span>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="p-2.5 rounded-2xl bg-[#080d1a] border border-slate-800 space-y-1.5">
            <label class="text-[11px] font-bold text-slate-300 block">စာသားအရောင် (Text Color)</label>
            <div class="flex items-center gap-2">
              <input type="color" id="subTextColorInput" value="#fde047" onchange="updateSubtitleStyles()" class="w-8 h-8 rounded-lg cursor-pointer bg-transparent border-0" />
              <span id="subTextColorCode" class="font-mono text-[10px] text-slate-400">#fde047</span>
            </div>
          </div>

          <div class="p-2.5 rounded-2xl bg-[#080d1a] border border-slate-800 space-y-1.5">
            <label class="text-[11px] font-bold text-slate-300 block">ဘောင်အရောင် (Border / Stroke)</label>
            <div class="flex items-center gap-2">
              <input type="color" id="subBorderColorInput" value="#000000" onchange="updateSubtitleStyles()" class="w-8 h-8 rounded-lg cursor-pointer bg-transparent border-0" />
              <span id="subBorderColorCode" class="font-mono text-[10px] text-slate-400">#000000</span>
            </div>
          </div>
        </div>

        <div class="space-y-1.5 p-2.5 rounded-2xl bg-[#080d1a] border border-slate-800">
          <div class="flex justify-between items-center">
            <span class="font-bold text-slate-300">စာသားအရွယ်အစား (Font Size)</span>
            <span id="subSizeLabel" class="font-mono text-amber-400 font-bold">18px</span>
          </div>
          <input type="range" id="subSizeRange" min="12" max="32" step="1" value="18" oninput="updateSubtitleStyles()" class="w-full accent-amber-500 cursor-pointer" />
        </div>
      </div>

      <!-- 6. VOICE SETTINGS CARD -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs">
        <div class="border-b border-slate-800 pb-2 font-bold text-slate-200 text-sm flex items-center justify-between">
          <span class="flex items-center gap-2">
            <span class="text-blue-400">🔊</span>
            <span>Voice & Dubbing Sync</span>
          </span>
          <span class="text-[10px] font-mono text-blue-400">Auto Pacing</span>
        </div>

        <!-- Voice Speed Slider -->
        <div class="space-y-2 pt-1">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-300 font-bold">Dubbing Speed (အသံနှင့် ဗီဒီယို တစ်ပြိုင်နက် Pacing)</span>
            <span id="recapSpeedValTag" class="font-mono text-blue-400 font-bold">1.20x</span>
          </div>
          <div class="flex items-center gap-3">
            <button type="button" onclick="adjustRecapSpeed(-2)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">−</button>
            <input id="recapSpeedRange" type="range" min="-20" max="30" step="2" value="20" class="w-full accent-blue-500 cursor-pointer" oninput="syncRecapSliders()" />
            <button type="button" onclick="adjustRecapSpeed(2)" class="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold text-sm flex items-center justify-center transition-all">+</button>
          </div>
        </div>

        <div class="space-y-2 pt-1 border-t border-slate-800/80">
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

      <!-- One-click pipeline: transcribe → Burmese recap → voice → final edit/export -->
      <button
        id="generateRecapBtn"
        type="button"
        onclick="executeAutoRecapVdWorkflow()"
        class="w-full py-4 rounded-3xl bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 hover:brightness-110 active:scale-[0.99] text-white font-extrabold text-sm sm:text-base shadow-2xl glow-btn flex items-center justify-center gap-2.5 transition-all"
      >
        <span id="recapSpinner" class="hidden animate-spin">🌀</span>
        <span id="recapIcon">✨</span>
        <span id="recapBtnLabel">One-Click Generate Recap</span>
      </button>
      <div id="recapWorkflowStatus" class="hidden rounded-2xl border border-violet-200 bg-violet-50 px-4 py-3 text-xs text-violet-800 space-y-1" role="status" aria-live="polite">
        <div id="recapWorkflowStep" class="font-bold">Preparing...</div>
        <div id="recapWorkflowHint" class="text-violet-600">AI က အဆင့်ဆင့် အလိုအလျောက် လုပ်ဆောင်နေပါတယ်။ Tab ကို မပိတ်ပါနဲ့။</div>
      </div>

      <!-- 8. REAL EXPORTED VIDEO PLAYER & DOWNLOAD CARD -->
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

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-2">
            <label class="font-bold text-slate-300 text-xs">TikTok Titles (၃ ခု)</label>
            <textarea id="recapTitlesOutput" rows="3" readonly class="w-full bg-[#080d1a] border border-slate-800 rounded-xl p-3 text-xs"></textarea>
            <button type="button" onclick="copyRecapField('recapTitlesOutput')" class="w-full py-2 bg-slate-800 text-slate-200 text-xs">📋 ခေါင်းစဉ် ၃ ခု Copy</button>
          </div>
          <div class="space-y-2">
            <label class="font-bold text-slate-300 text-xs">TikTok Hashtags (၅ ခု)</label>
            <textarea id="recapHashtagsOutput" rows="3" readonly class="w-full bg-[#080d1a] border border-slate-800 rounded-xl p-3 text-xs"></textarea>
            <button type="button" onclick="copyRecapField('recapHashtagsOutput')" class="w-full py-2 bg-slate-800 text-slate-200 text-xs">📋 Hashtags ၅ ခု Copy</button>
          </div>
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

    <!-- VIEW 2: AI TRANSCRIBER -->
    <div id="panelTranscriber" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl">
        <div class="flex items-center gap-2 font-bold text-slate-200 text-sm border-b border-slate-800 pb-2.5">
          <span class="text-blue-400">📤</span><span>AI Transcriber • Groq Whisper</span>
        </div>
        <p class="text-xs text-slate-300 leading-relaxed">ဗီဒီယို/အသံဖိုင်ထဲက စကားပြောသံကို စာသားအဖြစ် ပြောင်းပေးမယ်။ Groq API Key လိုအပ်ပါတယ်။ Audio ကို Browser မှာ အလိုအလျောက် ခွဲထုတ်ပြီး Whisper Server ဆီ ပို့ပေးမယ်။</p>
        <input id="transcriberFileInput" type="file" accept="audio/*,video/mp4,video/webm,.mp4,.webm,.mpeg,.mpga,.m4a,.wav,.mp3,.flac" class="w-full text-xs text-slate-300 file:mr-3 file:rounded-xl file:border-0 file:bg-blue-600 file:px-3 file:py-2 file:font-bold file:text-white"/>
        <button id="transcribeSourceBtn" onclick="transcribeSourceMedia()" class="w-full py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs">🎙️ စာသားထုတ်ယူမည် (Transcribe)</button>
        <textarea id="transcriberResultText" rows="9" placeholder="Transcription ရလဒ် ဒီမှာ ပေါ်လာပါမယ်..." class="w-full bg-[#080d1a] border border-slate-700 rounded-2xl p-3 text-xs leading-relaxed text-slate-100 custom-scroll"></textarea>
        <button onclick="sendTranscriptToRecap()" class="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs">စာသားကို Auto Recap ထဲသို့ ပို့မည် →</button>
      </div>
    </div>

    <!-- VIEW 3: TTS VOICE OVER STUDIO -->
    <div id="panelTts" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl">
        <div class="font-bold text-blue-400 text-sm border-b border-slate-800 pb-2.5">📄 Burmese Script → MP3 Voice Over</div>
        <textarea id="ttsInputTextArea" rows="7" placeholder="မြန်မာစာသားကို ဒီမှာ ထည့်ပါ..." class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-4 text-xs leading-relaxed text-slate-100 focus:outline-none focus:border-blue-500 custom-scroll resize-y">သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>
        <div class="grid grid-cols-2 gap-2">
          <label class="text-[11px] text-slate-400">Voice
            <select id="standaloneTtsVoice" class="mt-1 w-full bg-[#080d1a] border border-slate-700 rounded-xl p-2 text-xs text-white"></select>
          </label>
          <label class="text-[11px] text-slate-400">Speed
            <select id="standaloneTtsSpeed" class="mt-1 w-full bg-[#080d1a] border border-slate-700 rounded-xl p-2 text-xs text-white">
              <option value="-10">0.90x</option><option value="0" selected>1.00x</option><option value="10">1.10x</option><option value="20">1.20x</option>
            </select>
          </label>
        </div>
        <button id="standaloneTtsBtn" onclick="generateStandaloneTTS()" class="w-full py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs">အသံဖိုင် ဖန်တီးမည်</button>
        <audio id="standaloneTtsPlayer" controls class="hidden w-full"></audio>
        <a id="standaloneTtsDownload" class="hidden text-center text-xs text-emerald-300 underline" download="GoRecap-Voiceover.mp3">MP3 ဒေါင်းလုဒ်</a>
      </div>
    </div>

    <!-- VIEW 4: AUTO DUBBING MODE -->
    <div id="panelDubbing" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-cyan-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🎧</span><span>Auto Dubbing • Myanmar Voice</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">ဗီဒီယိုတင်ပါ → မူရင်းအသံကို စာသားထုတ်ပါ → မြန်မာလို ဘာသာပြန်ပါ → AI အသံထည့်ပြီး MP4/WebM Export လုပ်ပါ။ Groq API Key လိုအပ်ပါတယ်။</p>
        <label class="block text-slate-300 font-bold">၁။ မူရင်းဗီဒီယို
          <input id="dubbingVideoInput" type="file" accept="video/mp4,video/webm,video/quicktime,.mp4,.webm,.mov" class="mt-2 w-full text-xs text-slate-300 file:mr-3 file:rounded-xl file:border-0 file:bg-cyan-600 file:px-3 file:py-2 file:font-bold file:text-white"/>
        </label>
        <div class="grid grid-cols-2 gap-2">
          <label class="text-slate-400">မူရင်းဘာသာစကား
            <select id="dubbingSourceLanguage" class="mt-1 w-full bg-[#080d1a] border border-slate-700 rounded-xl p-2 text-xs text-white">
              <option value="auto">Auto Detect</option><option value="English">English</option><option value="Chinese">Chinese</option><option value="Japanese">Japanese</option><option value="Korean">Korean</option><option value="Thai">Thai</option><option value="Burmese">Burmese</option>
            </select>
          </label>
          <label class="text-slate-400">မြန်မာအသံ
            <select id="dubbingVoice" class="mt-1 w-full bg-[#080d1a] border border-slate-700 rounded-xl p-2 text-xs text-white"></select>
          </label>
        </div>
        <label class="block text-slate-300 font-bold">၂။ ထုတ်ယူထားသော မူရင်းစာသား (ပြင်လို့ရသည်)
          <textarea id="dubbingTranscript" rows="4" placeholder="Whisper က ထုတ်ပေးမယ့် မူရင်းစာသား..." class="mt-1 w-full bg-[#080d1a] border border-slate-700 rounded-xl p-3 text-xs leading-relaxed text-white"></textarea>
        </label>
        <label class="block text-slate-300 font-bold">၃။ မြန်မာဘာသာပြန်စာသား (ပြင်လို့ရသည်)
          <textarea id="dubbingMyanmarScript" rows="5" placeholder="AI ဘာသာပြန်ပေးမယ့် မြန်မာစာသား..." class="mt-1 w-full bg-[#080d1a] border border-slate-700 rounded-xl p-3 text-xs leading-relaxed text-white"></textarea>
        </label>
        <label class="flex items-center gap-2 text-slate-300"><input id="dubbingAddSubtitles" type="checkbox" checked class="accent-cyan-500"/> ဗီဒီယိုပေါ် မြန်မာစာတန်းထိုးမည်</label>
        <button id="dubbingStartBtn" onclick="startAutoDubbing()" class="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold">🎧 Auto Dubbing စတင်မည်</button>
        <p id="dubbingStatus" class="text-center text-cyan-300 min-h-5">ဗီဒီယိုဖိုင်ရွေးပြီး စတင်နိုင်ပါပြီ။</p>
        <div id="dubbingResult" class="hidden space-y-3 border-t border-slate-800 pt-3">
          <video id="dubbingOutputVideo" controls playsinline class="w-full rounded-xl bg-black"></video>
          <button onclick="downloadExportedVideoFile()" class="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold">⬇️ Dubbed Video ဒေါင်းလုဒ်</button>
        </div>
        <p class="text-[10px] text-slate-500">မှတ်ချက်: Browser မှာ Video ကို Render လုပ်တာဖြစ်လို့ Tab ကိုဖွင့်ထားပါ။ ဖိုင်ကြီးရင် ဖုန်း/Browser စွမ်းဆောင်ရည်ပေါ်မူတည်ပြီး ကြာနိုင်ပါတယ်။ မူရင်းအသံကို အစားထိုးပြီး မြန်မာ Voiceover တစ်ပုဒ်တည်း ထည့်ပေးပါတယ်။</p>
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

  <!-- POP-UP MODAL (Z-INDEX 999: NO CLIPPING, PROPER SPACING) -->
  <div id="voiceSelectorModalBackdrop" onclick="closeVoiceSelectorModal(event)" class="fixed inset-0 bg-black/85 backdrop-blur-md z-[999] hidden flex items-center justify-center p-4 transition-opacity">
    <div onclick="event.stopPropagation()" class="bg-[#0c1426] border border-slate-700/90 rounded-3xl max-w-md w-full p-5 space-y-3.5 shadow-2xl max-h-[85vh] flex flex-col">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3 shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-blue-400 text-lg">🔊</span>
          <div>
            <h3 class="font-extrabold text-sm text-white">Voice အသံရွေးချယ်ရန်</h3>
            <p class="text-[10px] text-slate-400">13 Crikk & Native Burmese Voices</p>
          </div>
        </div>
        <button type="button" onclick="closeVoiceSelectorModal(event)" class="text-slate-400 hover:text-white p-1 text-base font-bold">✕</button>
      </div>

      <div id="voiceModalItemsContainer" class="overflow-y-auto space-y-2 pr-1 custom-scroll flex-1">
        <!-- Rendered via JS -->
      </div>
    </div>
  </div>

  <!-- API Key Modal -->
  <div id="apiKeysModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-[#0b1222] border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 class="font-extrabold text-sm text-white">API Keys Configuration</h3>
        <button onclick="closeKeysModal()" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="font-bold text-amber-400 block mb-1">Google Gemini API Key</label>
          <input type="password" id="modalGeminiInput" placeholder="AIzaSy..." class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-blue-500" />
        </div>
        <div>
          <label class="font-bold text-blue-400 block mb-1">Groq Whisper API Key</label>
          <input type="password" id="modalGroqInput" placeholder="gsk_..." class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-blue-500" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
        <button onclick="closeKeysModal()" class="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold">Cancel</button>
        <button onclick="saveApiKeysModal()" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold">Save Keys</button>
      </div>
    </div>
  </div>

  <script>
    // 13 Voices Catalog with Bunny Phyoe
    const PERSONAS = [
      { id: "bunny-phyoe", name: "ဘန်နီဖြိုး", enName: "Bunny Phyoe", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ ဘန်နီဖြိုးပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "tayza", name: "တေဇ", enName: "Tayza", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ တေဇပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aung-ye-linn", name: "အောင်ရဲလင်း", enName: "Aung Ye' Linn", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ အောင်ရဲလင်းပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "chue-lay", name: "ချူးလေး", enName: "Chue Lay", gender: "women", badge: "Female", sample: "မင်္ဂလာပါ ချူးလေးပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "n-kai-yar", name: "အန်ခိုင်းရာ", enName: "N Kai Yar", gender: "women", badge: "Female", sample: "မင်္ဂလာပါ အန်ခိုင်းရာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nilar", name: "နီလာ", enName: "Nilar", gender: "women", badge: "Female", sample: "မင်္ဂလာပါ နီလာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "thiha", name: "သီဟ", enName: "Thiha", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ သီဟပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "phyo-ngwe-soe", name: "ဖြိုးငွေစိုး", enName: "Phyo Ngwe Soe", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ ဖြိုးငွေစိုးပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "sinn-tiyar", name: "စင်သီယာ", enName: "Sinn Tiyar", gender: "women", badge: "Female", sample: "မင်္ဂလာပါ စင်သီယာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nay-win", name: "နေဝင်း", enName: "Nay Win", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ နေဝင်းပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "eaindra-bo", name: "အိန္ဒြာဘို", enName: "Eaindra Bo", gender: "women", badge: "Female", sample: "မင်္ဂလာပါ အိန္ဒြာဘိုပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "ji-chaung-wook", name: "ဂျီချန်ဝု", enName: "Ji Chaung Wook", gender: "men", badge: "Male", sample: "မင်္ဂလာပါ ဂျီချန်ဝုပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aye-thidar", name: "အေးသီတာ", enName: "Aye Thidar", gender: "women", badge: "Female", sample: "မင်္ဂလာပါ အေးသီတာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" }
    ];

    let currentSelectedVoiceId = "bunny-phyoe";
    const standaloneVoiceSelect = document.getElementById("standaloneTtsVoice");
    if (standaloneVoiceSelect) standaloneVoiceSelect.innerHTML = PERSONAS.map(p => `<option value="${p.id}">${p.name} (${p.badge})</option>`).join("");
    let activePlayingTestVoiceId = null;
    let selectedRecapAspect = "9:16";
    let currentUploadedRecapFile = null;
    let generatedRecapAudioBlob = null;
    let exportedRenderedVideoBlob = null;
    let videoDurationSeconds = 0;

    // Draggable Blur Box State
    let blurBoxRect = { x: 0.22, y: 0.72, w: 0.55, h: 0.15 };
    let isDraggingBlur = false, isResizingBlur = false;
    let blurDragStartX = 0, blurDragStartY = 0;
    let blurInitialWidth = 160, blurInitialHeight = 50;

    // Draggable Subtitle Box State
    let subBoxPos = { x: 0.10, y: 0.82 };
    let isDraggingSub = false;
    let subDragStartX = 0, subDragStartY = 0;

    // Subtitle Custom Styles
    let subStyles = {
      textColor: "#fde047",
      borderColor: "#000000",
      fontSize: 18
    };

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
      document.querySelectorAll(".rg-tab").forEach(tab => tab.classList.remove("is-active"));
      const activeTab = document.getElementById(
        tool === "transcriber" ? "navTranscriber" :
        tool === "tts" ? "navTts" :
        tool === "dubbing" ? "navDubbing" : "navRecap"
      );
      if (activeTab) activeTab.classList.add("is-active");

      if (tool === "transcriber") {
        pTrans.classList.remove("hidden");
      } else if (tool === "tts") {
        pTts.classList.remove("hidden");
      } else if (tool === "dubbing") {
        pDub.classList.remove("hidden");
      } else {
        pRecap.classList.remove("hidden");
        updateVoiceTriggerLabel();
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
    // MODAL VOICE SELECTION
    // =========================================================================
    function openVoiceSelectorModal(e) {
      if (e) e.stopPropagation();
      document.getElementById("voiceSelectorModalBackdrop").classList.remove("hidden");
      renderVoiceModalList();
    }

    function closeVoiceSelectorModal(e) {
      if (e) e.stopPropagation();
      document.getElementById("voiceSelectorModalBackdrop").classList.add("hidden");
      const audioEl = document.getElementById("globalPreviewAudio");
      if (audioEl) {
        audioEl.pause();
        audioEl.currentTime = 0;
      }
      activePlayingTestVoiceId = null;
    }

    function updateVoiceTriggerLabel() {
      const p = PERSONAS.find(x => x.id === currentSelectedVoiceId) || PERSONAS[0];
      document.getElementById("selectedVoiceTitleTag").innerText = `${p.name} (${p.badge})`;
    }

    function renderVoiceModalList() {
      const container = document.getElementById("voiceModalItemsContainer");
      updateVoiceTriggerLabel();

      container.innerHTML = PERSONAS.map(p => {
        const isSelected = p.id === currentSelectedVoiceId;
        const isPlaying = activePlayingTestVoiceId === p.id;

        return `
          <div
            onclick="selectModalVoice('${p.id}', event)"
            class="p-3.5 rounded-2xl cursor-pointer transition-all flex items-center justify-between gap-3 ${
              isSelected ? 'bg-blue-600/25 border-2 border-blue-500 text-white shadow-lg shadow-blue-500/10' : 'bg-[#080d1a] border border-slate-800/90 hover:border-slate-700 text-slate-200'
            }"
          >
            <!-- Full Name -->
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <span class="font-extrabold text-xs sm:text-sm text-white whitespace-nowrap">${p.name}</span>
              <span class="text-[11px] text-slate-400 font-mono">(${p.enName})</span>
              <span class="text-[9px] px-1.5 py-0.5 rounded font-bold shrink-0 ${
                p.gender === 'men' ? 'bg-blue-950 text-blue-300 border border-blue-800' : 'bg-pink-950 text-pink-300 border border-pink-800'
              }">${p.badge}</span>
              ${isSelected ? '<span class="text-blue-400 font-bold text-xs shrink-0">✓</span>' : ''}
            </div>

            <!-- In-Line Test Voice Button -->
            <button
              type="button"
              onclick="playModalTestVoice('${p.id}', event)"
              class="px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all active:scale-95 shrink-0 ${
                isPlaying
                  ? 'bg-blue-600 text-white shadow-md animate-pulse'
                  : 'text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-700/80'
              }"
            >
              <span>${isPlaying ? '⏹' : '🔊'}</span>
              <span>${isPlaying ? 'Stop' : 'Test Voice'}</span>
            </button>
          </div>
        `;
      }).join("");
    }

    function selectModalVoice(voiceId, e) {
      if (e) e.stopPropagation();
      currentSelectedVoiceId = voiceId;
      updateVoiceTriggerLabel();
      closeVoiceSelectorModal();
      const p = PERSONAS.find(x => x.id === voiceId);
      showToast(`Selected: ${p.name}`, "info");
    }

    // Direct Native Audio Stream
    function playModalTestVoice(voiceId, e) {
      if (e) e.stopPropagation();
      const p = PERSONAS.find(x => x.id === voiceId);
      if (!p) return;

      const audioEl = document.getElementById("globalPreviewAudio");

      // Toggle off if currently playing
      if (activePlayingTestVoiceId === voiceId) {
        audioEl.pause();
        audioEl.currentTime = 0;
        activePlayingTestVoiceId = null;
        renderVoiceModalList();
        return;
      }

      activePlayingTestVoiceId = voiceId;
      renderVoiceModalList();

      // Trigger directly within user click gesture
      audioEl.pause();
      audioEl.src = `/api/preview/${voiceId}?t=${Date.now()}`;
      audioEl.currentTime = 0;

      const playPromise = audioEl.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.warn("Retrying with fallback speech source...", err);
          const encoded = encodeURIComponent(p.sample);
          audioEl.src = `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=my&q=${encoded}`;
          audioEl.playbackRate = p.gender === "men" ? 0.92 : 1.05;
          audioEl.play().catch(() => {
            activePlayingTestVoiceId = null;
            renderVoiceModalList();
          });
        });
      }
    }

    document.getElementById("globalPreviewAudio").onended = () => {
      activePlayingTestVoiceId = null;
      renderVoiceModalList();
    };

    document.getElementById("globalPreviewAudio").onerror = () => {
      activePlayingTestVoiceId = null;
      renderVoiceModalList();
    };

    // =========================================================================
    // ASPECT RATIO SELECTION & PRO 9:16 / 16:9 CONTAINER RESIZING
    // =========================================================================
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

      const wrapper = document.getElementById("videoContainerWrapper");
      const aspectTag = document.getElementById("aspectRatioLabelTag");

      if (ratio === "9:16") {
        wrapper.className = "relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-[9/16] w-full max-w-[310px] mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300";
        aspectTag.innerText = "Aspect: 9:16 (TikTok Zoom Fill)";
      } else if (ratio === "16:9") {
        wrapper.className = "relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-video w-full mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300";
        aspectTag.innerText = "Aspect: 16:9 (YouTube Landscape)";
      } else if (ratio === "1:1") {
        wrapper.className = "relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-square w-full max-w-[340px] mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300";
        aspectTag.innerText = "Aspect: 1:1 (Square Fill)";
      } else if (ratio === "4:3") {
        wrapper.className = "relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-[4/3] w-full mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300";
        aspectTag.innerText = "Aspect: 4:3 (Classic Fill)";
      } else {
        wrapper.className = "relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-[3/4] w-full max-w-[320px] mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300";
        aspectTag.innerText = "Aspect: 3:4 (Portrait Fill)";
      }

      showToast(`Output format: ${ratio} (Zoom-fill without black margins)`, "info");
      toggleEffectPreview();
    }

    function loadRecapVideoFile(file) {
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
      const bgClone = document.getElementById("recapBlurredBackdropEl");
      const url = URL.createObjectURL(file);
      vEl.src = url; bgClone.src = url;
      vEl.onloadedmetadata = () => { videoDurationSeconds = Math.round(vEl.duration) || 180; };
      toggleEffectPreview();
      showToast(`Video loaded: ${file.name} (${sizeMB} MB)`, "success");
    }
    document.getElementById("recapVideoFileInput").addEventListener("change", function() {
      loadRecapVideoFile(this.files && this.files[0]);
    });

    // =========================================================================
    // SUBTITLE STYLES (COLOR, BORDER, SIZE, DRAGGABLE)
    // =========================================================================
    function updateSubtitleStyles() {
      const textColor = document.getElementById("subTextColorInput").value;
      const borderColor = document.getElementById("subBorderColorInput").value;
      const fontSize = parseInt(document.getElementById("subSizeRange").value);

      subStyles.textColor = textColor;
      subStyles.borderColor = borderColor;
      subStyles.fontSize = fontSize;

      document.getElementById("subTextColorCode").innerText = textColor;
      document.getElementById("subBorderColorCode").innerText = borderColor;
      document.getElementById("subSizeLabel").innerText = `${fontSize}px`;

      const subSpan = document.getElementById("subPreviewSpanText");
      const subBox = document.getElementById("draggableSubtitleBox");

      subSpan.style.color = textColor;
      subSpan.style.fontSize = `${fontSize}px`;
      subSpan.style.fontFamily = recapSubtitleFont || "Padauk";
      subSpan.style.textShadow = `-2px -2px 0 ${borderColor}, 2px -2px 0 ${borderColor}, -2px 2px 0 ${borderColor}, 2px 2px 0 ${borderColor}, 0 4px 8px rgba(0,0,0,0.8)`;
      subBox.style.backgroundColor = "rgba(0, 0, 0, 0.75)";
      subBox.style.border = `1.5px solid ${borderColor}`;
    }

    const subBoxEl = document.getElementById("draggableSubtitleBox");
    const containerWrapper = document.getElementById("videoContainerWrapper");

    function initSubtitleDrag() {
      subBoxEl.addEventListener("mousedown", (e) => startDragSubtitle(e));
      subBoxEl.addEventListener("touchstart", (e) => startDragSubtitle(e), { passive: false });
      window.addEventListener("mousemove", (e) => moveDragSubtitle(e));
      window.addEventListener("touchmove", (e) => moveDragSubtitle(e), { passive: false });
      window.addEventListener("mouseup", endDragSubtitle);
      window.addEventListener("touchend", endDragSubtitle);
    }

    function startDragSubtitle(e) {
      isDraggingSub = true;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const rect = subBoxEl.getBoundingClientRect();
      subDragStartX = clientX - rect.left;
      subDragStartY = clientY - rect.top;
      e.preventDefault();
    }

    function moveDragSubtitle(e) {
      if (!isDraggingSub) return;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const containerRect = containerWrapper.getBoundingClientRect();

      let left = clientX - containerRect.left - subDragStartX;
      let top = clientY - containerRect.top - subDragStartY;

      const maxLeft = containerRect.width - subBoxEl.offsetWidth;
      const maxTop = containerRect.height - subBoxEl.offsetHeight;

      left = Math.max(0, Math.min(left, maxLeft));
      top = Math.max(0, Math.min(top, maxTop));

      subBoxEl.style.left = `${left}px`;
      subBoxEl.style.top = `${top}px`;

      subBoxPos.x = left / containerRect.width;
      subBoxPos.y = top / containerRect.height;

      if (e.cancelable) e.preventDefault();
    }

    function endDragSubtitle() { isDraggingSub = false; }
    initSubtitleDrag();

    // =========================================================================
    // DRAGGABLE & RESIZABLE BLUR BOX HANDLING
    // =========================================================================
    const blurBoxEl = document.getElementById("draggableBlurBox");
    const blurHandle = document.getElementById("blurResizeHandle");

    function initBlurInteractions() {
      blurBoxEl.addEventListener("mousedown", (e) => {
        if (e.target === blurHandle) return;
        startDragBlur(e);
      });
      blurBoxEl.addEventListener("touchstart", (e) => {
        if (e.target === blurHandle) return;
        startDragBlur(e);
      }, { passive: false });

      blurHandle.addEventListener("mousedown", (e) => startResizeBlur(e));
      blurHandle.addEventListener("touchstart", (e) => startResizeBlur(e), { passive: false });

      window.addEventListener("mousemove", (e) => {
        moveDragBlur(e);
        moveResizeBlur(e);
      });
      window.addEventListener("touchmove", (e) => {
        moveDragBlur(e);
        moveResizeBlur(e);
      }, { passive: false });

      window.addEventListener("mouseup", () => { isDraggingBlur = false; isResizingBlur = false; });
      window.addEventListener("touchend", () => { isDraggingBlur = false; isResizingBlur = false; });
    }

    function startDragBlur(e) {
      isDraggingBlur = true;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const rect = blurBoxEl.getBoundingClientRect();
      blurDragStartX = clientX - rect.left;
      blurDragStartY = clientY - rect.top;
      e.preventDefault();
    }

    function moveDragBlur(e) {
      if (!isDraggingBlur) return;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      const containerRect = containerWrapper.getBoundingClientRect();

      let left = clientX - containerRect.left - blurDragStartX;
      let top = clientY - containerRect.top - blurDragStartY;

      const maxLeft = containerRect.width - blurBoxEl.offsetWidth;
      const maxTop = containerRect.height - blurBoxEl.offsetHeight;

      left = Math.max(0, Math.min(left, maxLeft));
      top = Math.max(0, Math.min(top, maxTop));

      blurBoxEl.style.left = `${left}px`;
      blurBoxEl.style.top = `${top}px`;

      blurBoxRect.x = left / containerRect.width;
      blurBoxRect.y = top / containerRect.height;
      blurBoxRect.w = blurBoxEl.offsetWidth / containerRect.width;
      blurBoxRect.h = blurBoxEl.offsetHeight / containerRect.height;

      if (e.cancelable) e.preventDefault();
    }

    function startResizeBlur(e) {
      isResizingBlur = true;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      blurDragStartX = clientX;
      blurDragStartY = clientY;
      blurInitialWidth = blurBoxEl.offsetWidth;
      blurInitialHeight = blurBoxEl.offsetHeight;
      e.stopPropagation();
      e.preventDefault();
    }

    function moveResizeBlur(e) {
      if (!isResizingBlur) return;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;

      const deltaX = clientX - blurDragStartX;
      const deltaY = clientY - blurDragStartY;

      const newW = Math.max(50, Math.min(300, blurInitialWidth + deltaX));
      const newH = Math.max(25, Math.min(150, blurInitialHeight + deltaY));

      blurBoxEl.style.width = `${newW}px`;
      blurBoxEl.style.height = `${newH}px`;

      document.getElementById("blurWidthSlider").value = newW;
      document.getElementById("blurHeightSlider").value = newH;
      document.getElementById("blurWTag").innerText = `${newW}px`;
      document.getElementById("blurHTag").innerText = `${newH}px`;

      const containerRect = containerWrapper.getBoundingClientRect();
      blurBoxRect.w = newW / containerRect.width;
      blurBoxRect.h = newH / containerRect.height;

      if (e.cancelable) e.preventDefault();
    }

    function adjustBlurDimensionsFromSlider() {
      const w = parseInt(document.getElementById("blurWidthSlider").value);
      const h = parseInt(document.getElementById("blurHeightSlider").value);
      blurBoxEl.style.width = `${w}px`;
      blurBoxEl.style.height = `${h}px`;
      document.getElementById("blurWTag").innerText = `${w}px`;
      document.getElementById("blurHTag").innerText = `${h}px`;

      const containerRect = containerWrapper.getBoundingClientRect();
      blurBoxRect.w = w / containerRect.width;
      blurBoxRect.h = h / containerRect.height;
    }

    initBlurInteractions();

    function toggleEffectPreview() {
      const vEl = document.getElementById("recapVideoPlayerEl");
      const isMirror = document.getElementById("effectMirrorSwitch")?.checked;
      const isColor = document.getElementById("effectColorGradingSwitch")?.checked;
      const isZoom = document.getElementById("effectBypassZoomSwitch")?.checked;
      const isBlur = document.getElementById("effectBlurSwitch")?.checked;
      const isSub = document.getElementById("effectSubtitleSwitch")?.checked;
      const blurControls = document.getElementById("blurDimensionControls");
      const subCard = document.getElementById("subtitleStylingCard");

      let transformStr = "";
      if (isMirror) transformStr += "scaleX(-1) ";
      if (isZoom) transformStr += "scale(1.12) ";
      vEl.style.transform = transformStr || "none";

      let filterStr = "";
      if (isColor) {
        filterStr += "brightness(1.15) contrast(1.15) saturate(1.15) sepia(0.15) hue-rotate(-5deg) ";
      }
      vEl.style.filter = filterStr || "none";

      if (isBlur) {
        blurBoxEl.classList.remove("hidden");
        blurControls.classList.remove("hidden");
      } else {
        blurBoxEl.classList.add("hidden");
        blurControls.classList.add("hidden");
      }

      if (isSub) {
        subBoxEl.classList.remove("hidden");
        subCard.classList.remove("hidden");
        updateSubtitleStyles();
      } else {
        subBoxEl.classList.add("hidden");
        subCard.classList.add("hidden");
      }
    }

    function syncRecapSliders() {
      const s = parseInt(document.getElementById("recapSpeedRange").value);
      const p = parseInt(document.getElementById("recapPitchRange").value);
      const mult = (1 + s / 100).toFixed(2);
      document.getElementById("recapSpeedValTag").innerText = `${mult}x`;
      document.getElementById("recapPitchValTag").innerText = p === 0 ? "Normal" : (p > 0 ? `+${p}Hz` : `${p}Hz`);

      const vEl = document.getElementById("recapVideoPlayerEl");
      if (vEl) {
        vEl.playbackRate = Math.max(0.7, Math.min(1.8, parseFloat(mult)));
      }
    }

    function adjustRecapSpeed(delta) {
      const el = document.getElementById("recapSpeedRange");
      el.value = Math.max(-20, Math.min(30, parseInt(el.value) + delta));
      syncRecapSliders();
    }

    function adjustRecapPitch(delta) {
      const el = document.getElementById("recapPitchRange");
      el.value = Math.max(-15, Math.min(15, parseInt(el.value) + delta));
      syncRecapSliders();
    }

    async function transcribeSourceMedia() {
      const file = document.getElementById("transcriberFileInput").files?.[0];
      const groqKey = (localStorage.getItem("groq_api_key") || "").trim();
      if (!file) return showToast("ဗီဒီယို သို့မဟုတ် အသံဖိုင် အရင်ရွေးပါ", "error");
      if (!groqKey) { showToast("Groq API Key ထည့်ပေးပါ", "error"); openKeysModal(); return; }
      const btn = document.getElementById("transcribeSourceBtn");
      const result = document.getElementById("transcriberResultText");
      btn.disabled = true;
      try {
        btn.innerText = "⚡ Audio ကို မြန်နှုန်း 8x နဲ့ ထုတ်ယူနေပါတယ်...";
        const audioBlob = await extractAudioForWhisper(file, percent => { btn.innerText = `⚡ Audio Extraction ${percent}%`; });
        const audioName = "gorecap-transcriber.webm";
        if (audioBlob.size > 4 * 1024 * 1024) throw new Error("Audio ဖိုင် 4MB ကျော်နေပါတယ်။ Video ကို ပိုတိုအောင် ဖြတ်ပါ၊ သို့မဟုတ် Audio ကို အပိုင်းခွဲပါ။");
        btn.innerText = "Whisper Server ကို ဆက်သွယ်နေပါတယ်...";
        const form = new FormData();
        form.append("file", audioBlob, audioName);
        const response = await fetch("/api/transcribe", {
          method: "POST",
          headers: { "Authorization": `Bearer ${groqKey}` },
          body: form
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || data.error?.message || `Whisper Error ${response.status}`);
        const transcript = (data.text || "").trim();
        if (!transcript) throw new Error("အသံထဲက စကားပြောစာသား မတွေ့ပါ");
        result.value = transcript;
        showToast("Transcription ပြီးပါပြီ", "success");
      } catch (err) {
        showToast(err.message || "Whisper မအောင်မြင်ပါ", "error");
      } finally {
        btn.disabled = false;
        btn.innerText = "🎙️ စာသားထုတ်ယူမည် (Transcribe)";
      }
    }

    async function startAutoDubbing() {
      const videoFile = document.getElementById("dubbingVideoInput").files?.[0];
      const groqKey = (localStorage.getItem("groq_api_key") || "").trim();
      if (!videoFile) return showToast("Dubbing လုပ်မယ့် ဗီဒီယိုဖိုင် ရွေးပါ", "error");
      if (!groqKey) { showToast("Groq API Key ထည့်ပေးပါ", "error"); openKeysModal(); return; }

      const btn = document.getElementById("dubbingStartBtn");
      const status = document.getElementById("dubbingStatus");
      const setStatus = (message) => { status.textContent = message; btn.textContent = message; };
      btn.disabled = true;
      let transcript = document.getElementById("dubbingTranscript").value.trim();
      let myanmarScript = document.getElementById("dubbingMyanmarScript").value.trim();
      try {
        if (!transcript) {
          setStatus("၁/၄ — မူရင်းအသံကို စာသားထုတ်နေပါတယ်...");
          setStatus("၁/၄ — Video ထဲက Audio ကို 8x မြန်နှုန်းနဲ့ ထုတ်ယူနေပါတယ်...");
          const audioBlob = await extractAudioForWhisper(videoFile, percent => setStatus(`Audio Extraction ${percent}%`));
          if (audioBlob.size > 4 * 1024 * 1024) throw new Error("Audio 4MB ကျော်နေပါတယ်။ ပိုတိုတဲ့ Video အပိုင်းနဲ့ ပြန်စမ်းပါ။");
          const form = new FormData();
          form.append("file", audioBlob, "gorecap-dubbing.webm");
          const transcribeResponse = await fetch("/api/transcribe", {
            method:"POST", headers:{Authorization:`Bearer ${groqKey}`}, body:form
          });
          const transcribeData = await transcribeResponse.json().catch(()=>({}));
          if (!transcribeResponse.ok) throw new Error(transcribeData.detail || transcribeData.error?.message || `Whisper Error ${transcribeResponse.status}`);
          transcript = (transcribeData.text || "").trim();
          if (!transcript) throw new Error("မူရင်းအသံထဲက စကားပြောစာသား မတွေ့ပါ");
          document.getElementById("dubbingTranscript").value = transcript;
        }

        if (!myanmarScript) {
          setStatus("၂/၄ — မြန်မာလို ဘာသာပြန်နေပါတယ်...");
          const language = document.getElementById("dubbingSourceLanguage").value;
          const translateResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method:"POST",
            headers:{Authorization:`Bearer ${groqKey}`,"Content-Type":"application/json"},
            body:JSON.stringify({
              model:"llama-3.3-70b-versatile",
              temperature:0.2,
              messages:[
                {role:"system",content:"You are an expert audiovisual dubbing translator. Translate the supplied dialogue into natural, conversational spoken Burmese (Myanmar). Preserve meaning, names, tone and order. Do not summarize, add explanations, speaker labels, timestamps or sound effects. Return only the Burmese dialogue. Keep the translation concise enough to fit the original scene."},
                {role:"user",content:`Source language: ${language}. Translate this transcript into Burmese for voice dubbing:\n\n${transcript.slice(0,24000)}`}
              ]
            })
          });
          const translateData = await translateResponse.json().catch(()=>({}));
          if (!translateResponse.ok) throw new Error(translateData.error?.message || `Translation Error ${translateResponse.status}`);
          myanmarScript = (translateData.choices?.[0]?.message?.content || "").trim();
          if (!myanmarScript) throw new Error("မြန်မာဘာသာပြန်စာသား မရရှိပါ");
          document.getElementById("dubbingMyanmarScript").value = myanmarScript;
        }

        setStatus("၃/၄ — မြန်မာအသံဖိုင် ဖန်တီးနေပါတယ်...");
        const ttsResponse = await fetch("/api/tts", {
          method:"POST", headers:{"Content-Type":"application/json"},
          body:JSON.stringify({
            text:myanmarScript,
            persona_id:document.getElementById("dubbingVoice").value || "nilar",
            user_rate_offset:0,
            user_pitch_offset:0
          })
        });
        if (!ttsResponse.ok) {
          const errorData = await ttsResponse.json().catch(()=>({}));
          throw new Error(errorData.detail || "Myanmar TTS မအောင်မြင်ပါ");
        }
        const audioBlob = await ttsResponse.blob();
        if (!audioBlob.size) throw new Error("TTS အသံဖိုင် ဗလာဖြစ်နေပါတယ်");

        setStatus("၄/၄ — ဗီဒီယိုနဲ့ မြန်မာအသံ ပေါင်းစပ် Export လုပ်နေပါတယ်...");
        const videoMeta = document.createElement("video");
        videoMeta.preload = "metadata";
        videoMeta.src = URL.createObjectURL(videoFile);
        await new Promise((resolve,reject)=>{
          videoMeta.onloadedmetadata=resolve;
          videoMeta.onerror=()=>reject(new Error("ဒီ Video Format ကို Browser က မဖတ်နိုင်ပါ"));
        });
        if (!Number.isFinite(videoMeta.duration) || videoMeta.duration <= 0) throw new Error("ဗီဒီယိုကြာချိန် မဖတ်နိုင်ပါ");
        const effects = {
          isMirror:false, isColor:false, isZoom:false, isBlur:false,
          isSub:document.getElementById("dubbingAddSubtitles").checked
        };
        const aspect = videoMeta.videoWidth >= videoMeta.videoHeight ? "16:9" : "9:16";
        exportedRenderedVideoBlob = await renderAndExportComposedVideo(
          videoFile, audioBlob, myanmarScript, aspect, effects, videoMeta.duration, 1
        );
        if (!exportedRenderedVideoBlob || exportedRenderedVideoBlob.size < 1000) throw new Error("Video Export ဖိုင် မပြည့်စုံပါ");
        const output = document.getElementById("dubbingOutputVideo");
        if (output.dataset.objectUrl) URL.revokeObjectURL(output.dataset.objectUrl);
        const outputUrl = URL.createObjectURL(exportedRenderedVideoBlob);
        output.dataset.objectUrl = outputUrl;
        output.src = outputUrl;
        document.getElementById("dubbingResult").classList.remove("hidden");
        status.textContent = "ပြီးပါပြီ — Dubbed Video အသင့်ဖြစ်ပါပြီ။";
        btn.textContent = "🎧 ထပ်မံ Dubbing လုပ်မည်";
        showToast("Auto Dubbing နဲ့ Video Export ပြီးပါပြီ", "success");
      } catch (error) {
        status.textContent = error.message || "Auto Dubbing မအောင်မြင်ပါ";
        btn.textContent = "ပြန်လည်ကြိုးစားမည်";
        showToast(status.textContent, "error");
      } finally {
        btn.disabled = false;
      }
    }

    function sendTranscriptToRecap() {
      const transcript = document.getElementById("transcriberResultText").value.trim();
      if (!transcript) return showToast("ပို့မယ့် Transcript မရှိသေးပါ", "error");
      document.getElementById("recapSourceTranscript").value = transcript;
      switchStudioView("recapvd");
      showToast("Transcript ကို Auto Recap ထဲ ပို့ပြီးပါပြီ", "success");
    }

    async function generateStandaloneTTS() {
      const text = document.getElementById("ttsInputTextArea").value.trim();
      if (!text) return showToast("အသံပြောင်းမယ့် စာသား ထည့်ပါ", "error");
      const btn = document.getElementById("standaloneTtsBtn");
      btn.disabled = true;
      btn.innerText = "အသံဖန်တီးနေပါတယ်...";
      try {
        const response = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            persona_id: document.getElementById("standaloneTtsVoice").value || "bunny-phyoe",
            user_rate_offset: parseInt(document.getElementById("standaloneTtsSpeed").value || "0", 10),
            user_pitch_offset: 0
          })
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || "TTS အသံဖန်တီးမှု မအောင်မြင်ပါ");
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const player = document.getElementById("standaloneTtsPlayer");
        const download = document.getElementById("standaloneTtsDownload");
        player.src = url;
        player.classList.remove("hidden");
        download.href = url;
        download.classList.remove("hidden");
        showToast("MP3 အသံဖိုင် အသင့်ဖြစ်ပါပြီ", "success");
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        btn.disabled = false;
        btn.innerText = "အသံဖိုင် ဖန်တီးမည်";
      }
    }

    // =========================================================================
    // ADVANCED COMPOSITOR (ZERO BLACK MARGINS, CUSTOM SUBTITLES & MOVING BLUR)
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
          const sourceVideoUrl = URL.createObjectURL(videoFile);
          sourceVideo.src = sourceVideoUrl;
          sourceVideo.muted = true;
          sourceVideo.playsInline = true;
          await new Promise((r) => { sourceVideo.onloadedmetadata = r; });

          const requestedVideoSpeed = Math.max(0.75, Math.min(2.0, Number(playbackSpeed) || 1.3));
          sourceVideo.playbackRate = requestedVideoSpeed;

          const speechAudio = new Audio();
          const speechAudioUrl = URL.createObjectURL(audioBlob);
          speechAudio.src = speechAudioUrl;
          await new Promise((resolve, reject) => {
            speechAudio.onloadedmetadata = resolve;
            speechAudio.onerror = () => reject(new Error("Voiceover audio metadata ကို ဖတ်မရပါ"));
          });
          // Keep narration at natural speed; adapt source-video speed in 10-second
          // source segments so visual playback follows the narration timeline.
          speechAudio.playbackRate = 1.0;
          let nextVideoSyncMark = 0;
          const updateSegmentPlaybackRate = () => {
            if (!Number.isFinite(sourceVideo.duration) || !Number.isFinite(speechAudio.duration)) return;
            const remainingVideo = Math.max(0.25, sourceVideo.duration - sourceVideo.currentTime);
            const remainingVoice = Math.max(0.25, (speechAudio.duration - speechAudio.currentTime) / speechAudio.playbackRate);
            const adaptiveRate = remainingVideo / remainingVoice;
            sourceVideo.playbackRate = Math.max(0.75, Math.min(2.0, adaptiveRate));
            nextVideoSyncMark = Math.floor(sourceVideo.currentTime / 10) * 10 + 10;
          };
          updateSegmentPlaybackRate();
          sourceVideo.addEventListener("timeupdate", () => {
            if (sourceVideo.currentTime >= nextVideoSyncMark - 0.12) updateSegmentPlaybackRate();
          });

          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          if (!AudioContextClass) throw new Error("ဒီ Browser မှာ Audio Export ကို မထောက်ပံ့ပါ");
          const audioCtx = new AudioContextClass();
          if (audioCtx.state === "suspended") await audioCtx.resume();
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
          if (!MediaRecorder.isTypeSupported(mime)) throw new Error("ဒီ Browser မှာ Video Export Format ကို မထောက်ပံ့ပါ။ Chrome/Edge နောက်ဆုံးဗားရှင်းကို သုံးပါ။");

          const mediaRecorder = new MediaRecorder(mixedStream, { mimeType: mime });
          const recordedChunks = [];

          mediaRecorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) recordedChunks.push(e.data);
          };

          mediaRecorder.onstop = () => {
            const finalBlob = new Blob(recordedChunks, { type: mime });
            mixedStream.getTracks().forEach(track => track.stop());
            audioCtx.close().catch(() => {});
            sourceVideo.pause();
            speechAudio.pause();
            sourceVideo.removeAttribute("src");
            speechAudio.removeAttribute("src");
            sourceVideo.load();
            URL.revokeObjectURL(sourceVideoUrl);
            URL.revokeObjectURL(speechAudioUrl);
            resolve(finalBlob);
          };

          let animationFrameId = null;
          const sentences = scriptText.split(/(?<=[။!?\n])/).filter(s => s.trim().length > 0);
          let startTimeStamp = performance.now();
          const totalExpectedDuration = Math.max(1, Math.min(Math.max(Number(targetDuration) || 180, Number(speechAudio.duration) || 0), 480));

          function renderFrame(now) {
            const elapsed = (now - startTimeStamp) / 1000;

            if (elapsed >= totalExpectedDuration || speechAudio.ended) {
              cancelAnimationFrame(animationFrameId);
              mediaRecorder.stop();
              return;
            }

            ctx.save();
            ctx.filter = "blur(14px) opacity(0.85)";
            ctx.drawImage(sourceVideo, 0, 0, targetW, targetH);
            ctx.restore();

            ctx.save();

            if (effects.isMirror) {
              ctx.translate(targetW, 0);
              ctx.scale(-1, 1);
            }

            let zoomScale = 1.0;
            if (effects.isZoom) {
              zoomScale = 1.10 + 0.04 * Math.sin(elapsed * 0.4);
              ctx.translate(targetW / 2, targetH / 2);
              ctx.scale(zoomScale, zoomScale);
              ctx.translate(-targetW / 2, -targetH / 2);
            }

            if (effects.isColor) {
              ctx.filter = "brightness(1.15) contrast(1.15) saturate(1.15) sepia(0.15) hue-rotate(-5deg)";
            } else {
              ctx.filter = "none";
            }

            const scale = Math.max(targetW / sourceVideo.videoWidth, targetH / sourceVideo.videoHeight);
            const drawW = sourceVideo.videoWidth * scale;
            const drawH = sourceVideo.videoHeight * scale;
            const drawX = (targetW - drawW) / 2;
            const drawY = (targetH - drawH) / 2;

            ctx.drawImage(sourceVideo, drawX, drawY, drawW, drawH);
            ctx.restore();

            if (effects.isBlur) {
              const bx = blurBoxRect.x * targetW;
              const by = blurBoxRect.y * targetH;
              const bw = blurBoxRect.w * targetW;
              const bh = blurBoxRect.h * targetH;

              ctx.save();
              ctx.beginPath();
              ctx.rect(bx, by, bw, bh);
              ctx.clip();
              ctx.globalAlpha = Number(document.getElementById("blurOpacitySlider")?.value || 100) / 100;
              ctx.filter = `blur(${Number(document.getElementById("blurStrengthSlider")?.value || 18)}px)`;
              ctx.drawImage(sourceVideo, drawX, drawY, drawW, drawH);
              ctx.restore();

              ctx.strokeStyle = "rgba(255,255,255,0.2)";
              ctx.lineWidth = 2;
              ctx.strokeRect(bx, by, bw, bh);
            }

            const logoEl=document.getElementById("recapLogoOverlay");
            if(logoEl&&recapLogoUrl&&logoEl.complete&&logoEl.naturalWidth){const lw=targetW*recapLogoWidth,lh=lw*(logoEl.naturalHeight/logoEl.naturalWidth);ctx.save();ctx.globalAlpha=recapLogoOpacity;ctx.drawImage(logoEl,recapLogoPosition.x*targetW,recapLogoPosition.y*targetH,lw,lh);ctx.restore();}

            if (effects.isSub && sentences.length > 0) {
              const audioDur = speechAudio.duration || totalExpectedDuration;
              const progress = Math.min(1.0, speechAudio.currentTime / audioDur);
              const curIdx = Math.min(sentences.length - 1, Math.floor(progress * sentences.length));
              const textToDraw = sentences[curIdx]?.trim() || "";

              if (textToDraw) {
                ctx.save();
                const renderedFontSize = Math.round((subStyles.fontSize / 18) * (targetW * 0.04));
                ctx.font = `bold ${renderedFontSize}px ${recapSubtitleFont || "Padauk"}, sans-serif`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";

                const subX = (subBoxPos.x + 0.4) * targetW;
                const subY = (subBoxPos.y + 0.05) * targetH;
                const maxTextWidth = targetW * 0.88;
                const lineHeight = Math.round(renderedFontSize * 1.28);
                const segments = (typeof Intl.Segmenter === "function")
                  ? Array.from(new Intl.Segmenter("my", {granularity:"grapheme"}).segment(textToDraw), item => item.segment)
                  : Array.from(textToDraw);
                const subtitleLines = [""];
                for (const part of segments) {
                  const candidate = subtitleLines[subtitleLines.length - 1] + part;
                  if (ctx.measureText(candidate).width <= maxTextWidth || !subtitleLines[subtitleLines.length - 1]) {
                    subtitleLines[subtitleLines.length - 1] = candidate;
                  } else if (subtitleLines.length < 2) {
                    subtitleLines.push(part.trimStart());
                  } else {
                    let last = subtitleLines[1];
                    while (last && ctx.measureText(last + "…").width > maxTextWidth) last = Array.from(last).slice(0, -1).join("");
                    subtitleLines[1] = last + "…";
                    break;
                  }
                }
                const textWidth = Math.min(maxTextWidth, Math.max(...subtitleLines.map(line => ctx.measureText(line).width)));
                const padX = 24, padY = 12;
                const blockHeight = lineHeight * subtitleLines.length;

                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.roundRect(
                  subX - textWidth / 2 - padX,
                  subY - blockHeight / 2 - padY,
                  textWidth + padX * 2,
                  blockHeight + padY * 2,
                  12
                );
                ctx.fill();

                ctx.lineWidth = 3;
                ctx.strokeStyle = subStyles.borderColor;
                ctx.fillStyle = subStyles.textColor;
                subtitleLines.forEach((line, index) => {
                  const lineY = subY + (index - (subtitleLines.length - 1) / 2) * lineHeight;
                  ctx.strokeText(line, subX, lineY);
                  ctx.fillText(line, subX, lineY);
                });
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

    // Extract audio client-side so the source video never needs to be uploaded.
    // Playback is accelerated to reduce wait time; Whisper accuracy can vary with
    // highly accelerated speech, so keep the source recording available for retry.
    async function extractAudioForWhisper(videoFile, onProgress) {
      return new Promise((resolve, reject) => {
        const video = document.createElement("video");
        const objectUrl = URL.createObjectURL(videoFile);
        const chunks = [];
        let recorder = null;
        let audioContext = null;
        let finished = false;
        const cleanup = () => {
          video.pause();
          video.removeAttribute("src");
          video.load();
          URL.revokeObjectURL(objectUrl);
          if (audioContext && audioContext.state !== "closed") audioContext.close().catch(() => {});
        };
        const fail = (message) => {
          if (finished) return;
          finished = true;
          cleanup();
          reject(new Error(message));
        };

        video.preload = "auto";
        video.playsInline = true;
        video.playbackRate = 8;
        if ("preservesPitch" in video) video.preservesPitch = true;
        video.src = objectUrl;
        video.onerror = () => fail("Video ဖိုင်ကို ဖတ်မရပါ။ MP4 သို့မဟုတ် WebM ဖိုင်နဲ့ ပြန်စမ်းပါ။");

        try {
          if (!window.MediaRecorder || !(window.AudioContext || window.webkitAudioContext)) {
            throw new Error("ဒီ Browser မှာ Audio Extraction မထောက်ပံ့ပါ။ Chrome နောက်ဆုံးဗားရှင်းနဲ့ ပြန်စမ်းပါ။");
          }
          // Resume audio synchronously from the Generate button gesture for mobile browsers.
          audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const resumePromise = audioContext.resume();
          const source = audioContext.createMediaElementSource(video);
          const destination = audioContext.createMediaStreamDestination();
          source.connect(destination);
          if (!destination.stream.getAudioTracks().length) {
            throw new Error("ဒီ Video ထဲမှာ အသံ Track မတွေ့ပါ။");
          }
          const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
            ? "audio/webm;codecs=opus"
            : (MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "");
          recorder = new MediaRecorder(destination.stream, {
            ...(mimeType ? { mimeType } : {}),
            audioBitsPerSecond: 32000
          });
          recorder.ondataavailable = (event) => {
            if (event.data && event.data.size) chunks.push(event.data);
          };
          recorder.onerror = () => fail("Audio Extraction မအောင်မြင်ပါ။ Browser သို့မဟုတ် Video Format ကို စစ်ဆေးပါ။");
          recorder.onstop = () => {
            if (finished) return;
            finished = true;
            const audioBlob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
            cleanup();
            if (!audioBlob.size) {
              reject(new Error("Video ထဲက အသံကို ထုတ်ယူလို့မရပါ။"));
            } else if (audioBlob.size > 4 * 1024 * 1024) {
              reject(new Error("Audio ဖိုင်က Server တင်နိုင်တဲ့ အရွယ်အစားထက် ကျော်နေပါတယ်။ ပိုတိုတဲ့ Video အပိုင်းနဲ့ စမ်းပါ။"));
            } else {
              resolve(audioBlob);
            }
          };
          video.ontimeupdate = () => {
            if (video.duration && onProgress) {
              onProgress(Math.min(100, Math.floor(video.currentTime / video.duration * 100)));
            }
          };
          video.onended = () => {
            if (recorder && recorder.state !== "inactive") recorder.stop();
          };
          recorder.start(1000);
          Promise.resolve(resumePromise)
            .then(() => video.play())
            .catch(() => fail("Video ကို Browser မှာ ဖွင့်မရပါ။ Chrome နောက်ဆုံးဗားရှင်းနဲ့ ပြန်စမ်းပါ။"));
        } catch (error) {
          fail(error.message || "Audio Extraction မအောင်မြင်ပါ။");
        }
      });
    }

    async function executeAutoRecapVdWorkflow() {
      if (!currentUploadedRecapFile) {
        showToast("Please upload a video file first", "error");
        return;
      }

      const geminiKey = (localStorage.getItem("gemini_api_key") || "").trim();
      const groqKey = (localStorage.getItem("groq_api_key") || "").trim();

      // Whisper is the automatic speech-to-text stage, so Groq is required.
      if (!groqKey) {
        showToast("Auto Transcript အတွက် Groq API Key လိုအပ်ပါတယ်", "error");
        openKeysModal();
        return;
      }
      if (!geminiKey && !groqKey) {
        showToast("Gemini သို့မဟုတ် Groq API Key ထည့်ပါ", "error");
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
      const workflowStatus = document.getElementById("recapWorkflowStatus");
      const workflowStep = document.getElementById("recapWorkflowStep");
      const workflowHint = document.getElementById("recapWorkflowHint");
      const setWorkflowStep = (step, hint) => {
        workflowStatus.classList.remove("hidden");
        workflowStep.innerText = step;
        workflowHint.innerText = hint || "ပြီးဆုံးတဲ့အထိ စောင့်ပေးပါ။";
        label.innerText = step;
      };

      btn.disabled = true;
      resultCard.classList.add("hidden");
      document.getElementById("recapSourceTranscript").value = "";
      document.getElementById("recapTitlesOutput").value = "";
      document.getElementById("recapHashtagsOutput").value = "";
      spinner.classList.remove("hidden");
      icon.classList.add("hidden");
      setWorkflowStep("1/6 — မူရင်းအသံမှ Transcript ထုတ်ယူနေပါတယ်...", "Groq Whisper က Video ထဲက စကားပြောသံကို အလိုအလျောက် စာသားပြောင်းနေပါတယ်။");

      try {
        setWorkflowStep("1/6 — Video ထဲက အသံကို ခွဲထုတ်နေပါတယ်...", "Video အကြီးကြီးကို မတင်ဘဲ Browser ထဲမှာ Audio သီးသန့် ထုတ်ယူနေပါတယ်။");
        const extractedAudio = await extractAudioForWhisper(currentUploadedRecapFile, (percent) => {
          workflowHint.innerText = `Audio ကို မြန်နှုန်း 8x နဲ့ ခွဲထုတ်နေပါတယ်... ${percent}%`;
        });
        setWorkflowStep("1/6 — Audio ကို စာသားပြောင်းနေပါတယ်...", "အသံဖိုင်သေးသေးကို Groq Whisper ဆီပို့ပြီး Transcript ထုတ်နေပါတယ်။");
        const transcribeForm = new FormData();
        transcribeForm.append("file", extractedAudio, "gorecap-audio.webm");
        let transcribeResponse;
        try {
          transcribeResponse = await fetch("/api/transcribe", {
            method: "POST",
            headers: { "Authorization": `Bearer ${groqKey}` },
            body: transcribeForm
          });
        } catch (networkError) {
          throw new Error("Whisper Server ကို မဆက်သွယ်နိုင်ပါ။ Internet connection စစ်ပြီး ထပ်စမ်းပါ။");
        }
        const transcribeData = await transcribeResponse.json().catch(() => ({}));
        if (!transcribeResponse.ok) {
          throw new Error(transcribeData.detail || transcribeData.error?.message || `Whisper Transcript မအောင်မြင်ပါ (${transcribeResponse.status})`);
        }
        const sourceTranscript = (transcribeData.text || "").trim();
        if (sourceTranscript.length < 30) {
          throw new Error("Video ထဲက စကားပြောသံ မလုံလောက်ပါ။ အသံပါဝင်တဲ့ Video ကို ပြန်တင်ပါ။");
        }
        document.getElementById("recapSourceTranscript").value = sourceTranscript;
        setWorkflowStep("2/6 — ဇာတ်လမ်းကို မြန်မာ Movie Recap အဖြစ် ရေးသားနေပါတယ်...", "Transcript ရရှိပါပြီ။ AI က ဇာတ်လမ်းအစမှ အဆုံးအထိ စကားပြောပုံစံနဲ့ ပြန်ရေးနေပါတယ်။");
        const durSecs = videoDurationSeconds || 180;
        const targetWords = Math.max(180, Math.min(520, Math.round(durSecs * 2.2)));

        const prompt = `
Act as a high-energy TikTok movie recap narrator. Translate the following transcript into 100% natural spoken Myanmar language (ဗမာစကားပြော).
Follow these strict rules:
1. Natural & Engaging Narration: Absolutely NO formal or bookish Myanmar words (Strictly avoid သည်။, ၏, သော, ၍). Use conversational particles like တယ်, တာ, ပေါ့, လေ, ဗျာ to make it sound like an exciting story told to a friend. Make the tone fast-paced and thrilling.
2. Transform Dialogues (Indirect Speech): Do NOT translate dialogues as direct quotes. Convert all character dialogues into indirect speech and weave them seamlessly into the narrative recap flow (e.g., instead of writing He said, "I will do this", write 'he angrily told them that he was going to do it').
3. 100% Complete yet Smooth: Translate the entire transcript accurately without skipping details. Keep the story completely intact but ensure it flows naturally in Myanmar.
4. TikTok Safety Bypass (Strictly Follow): Automatically replace restricted words with these safe metaphors:
Alcohol/Beer/Liquor -> 'အထူးဖျော်ရည်'
Cigarettes/Smoking -> 'မီးခိုးတံ'
Drugs/Pills/Injections -> 'ပစ္စည်း' or 'အားဆေး'
Violence/Kill/Death/Blood -> 'ရှင်းထုတ်လိုက်တယ်' / 'အနားယူသွားတယ်' / 'အနီရောင်အမှတ်တွေ'
Swear words -> Intense but safe emotional expressions (e.g., ဟာကွာ, တောက်).
5. Voiceover Optimized (TTS): Keep sentences short and punchy. Use commas ( , ) ONLY for natural breathing pauses to make the AI voice sound fast and smooth.
6. Final Output Format: Provide the translation as ONE continuous flow of text. Absolutely NO line numbering, NO section titles, NO bullet points, NO line breaks, and NO quotation marks (" "). Output ONLY the final Myanmar script with zero introductory or concluding remarks.
Vd to Burmese translate text.

IMPORTANT: Translate every available transcript detail faithfully. Do not summarize, omit scenes, invent events, or invent an ending. The transcript is the only source of story facts.
TRANSCRIPT:
${sourceTranscript.slice(0, 100000)}
        `.trim();

        let finalScript = "";
        const recapProviderErrors = [];

        // The former llama-3.3-70b-versatile model was retired for Free/Developer
        // Groq usage. Use currently supported Groq models with a clear fallback.
        if (groqKey && !geminiKey) {
          const groqModels = [
            { id: "openai/gpt-oss-120b", label: "Groq GPT-OSS 120B" },
            { id: "qwen/qwen3.8-27b", label: "Groq Qwen 3.8 27B" }
          ];
          for (const model of groqModels) {
            try {
              const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
                body: JSON.stringify({
                  model: model.id,
                  messages: [
                    { role: "system", content: prompt },
                    { role: "user", content: `Write a complete ${durSecs}-second storytelling recap in Burmese using only the transcript included in the system instructions. Do not invent plot details.` }
                  ],
                  max_completion_tokens: 6000,
                  temperature: 0.3,
                  ...(model.id === "openai/gpt-oss-120b" ? { reasoning_effort: "low" } : {})
                })
              });
              const data = await res.json().catch(() => ({}));
              if (!res.ok) {
                const detail = data.error?.message || data.message || res.statusText || "Unknown Groq error";
                recapProviderErrors.push(`${model.label} (${res.status}): ${detail}`);
                continue;
              }
              const raw = data.choices?.[0]?.message?.content || "";
              const candidate = sanitizePureScript(typeof raw === "string" ? raw : "");
              if (candidate.length > 80) {
                finalScript = candidate;
                break;
              }
              recapProviderErrors.push(`${model.label}: API က စာသားအလွတ် ပြန်ပေးခဲ့ပါတယ်`);
            } catch (error) {
              recapProviderErrors.push(`${model.label}: ${error.message || "Network error"}`);
            }
          }
        }

        if (!finalScript && geminiKey) {
          try {
            const geminiData = await callGemini(prompt, 8192, geminiKey);
            finalScript = sanitizePureScript(geminiData.text || "");
            if (!finalScript) recapProviderErrors.push("Gemini: စာသားအလွတ် ပြန်ရရှိပါတယ်။");
          } catch (error) {
            recapProviderErrors.push(`Gemini 3.8 Flash: ${error.message || "Network error"}`);
          }
        }

        if (!finalScript) {
          const detail = recapProviderErrors.length
            ? recapProviderErrors.join(" | ").slice(0, 900)
            : "Gemini သို့မဟုတ် Groq API Key မတွေ့ပါ။";
          throw new Error(`AI Recap မအောင်မြင်ပါ။ ${detail}`);
        }

        scriptArea.value = finalScript;
        makeRecapThumbnailPrompt(finalScript);

        try {
          setWorkflowStep("3/6 — TikTok ခေါင်းစဉ်နဲ့ Hashtags ဖန်တီးနေပါတယ်...", "ခေါင်းစဉ် ၃ ခုနဲ့ Hashtags ၅ ခု ထုတ်ပေးနေပါတယ်။");
          const metaPrompt = `Based only on the following Burmese movie recap, return valid JSON only with this exact shape: {"titles":["title 1","title 2","title 3"],"hashtags":["#tag1","#tag2","#tag3","#tag4","#tag5"]}. Titles must be catchy natural Burmese TikTok titles. Exactly 3 titles and exactly 5 relevant TikTok hashtags. No markdown fences or extra text. Recap:\n${finalScript.slice(0, 18000)}`;
          let metaText = "";
          if (geminiKey) {
            try { const meta = await callGemini(metaPrompt, 1200, geminiKey); metaText = meta.text || ""; }
            catch (geminiMetaError) { console.warn("Gemini metadata failed; trying Groq", geminiMetaError); }
          }
          if (!metaText && groqKey) {
            const metaResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
              method: "POST",
              headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
              body: JSON.stringify({ model: "openai/gpt-oss-120b", messages: [{role:"user",content:metaPrompt}], max_completion_tokens: 1200, temperature: 0.2 })
            });
            const metaData = await metaResponse.json().catch(() => ({}));
            if (metaResponse.ok) metaText = metaData.choices?.[0]?.message?.content || "";
            else throw new Error(metaData.error?.message || `Groq metadata failed (${metaResponse.status})`);
          }
          const cleanedMeta = metaText.replace(/```json|```/g, "").trim();
          const jsonMatch = cleanedMeta.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            const social = JSON.parse(jsonMatch[0]);
            document.getElementById("recapTitlesOutput").value = (Array.isArray(social.titles) ? social.titles.slice(0,3) : []).join("\n");
            document.getElementById("recapHashtagsOutput").value = (Array.isArray(social.hashtags) ? social.hashtags.slice(0,5) : []).join(" ");
          }
        } catch (metaError) {
          console.warn("Social metadata generation failed:", metaError);
        }

        setWorkflowStep("4/6 — ရွေးထားတဲ့ မြန်မာအသံ ဖန်တီးနေပါတယ်...", "AI Recap Script ကို ရွေးထားတဲ့ Voice နဲ့ အသံဖိုင်ပြောင်းနေပါတယ်။");

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

        setWorkflowStep("5/6 — Video ကို အလိုအလျောက် Edit လုပ်နေပါတယ်...", "အသံ၊ Zoom၊ Color၊ Subtitle နဲ့ ရွေးထားတဲ့ Aspect Ratio ကို ပေါင်းစပ်နေပါတယ်။");
        showToast("Video Edit နဲ့ အသံပေါင်းစပ်နေပါတယ်...", "info");

        const effects = {
          isMirror: document.getElementById("effectMirrorSwitch")?.checked,
          isColor: document.getElementById("effectColorGradingSwitch")?.checked,
          isZoom: document.getElementById("effectBypassZoomSwitch")?.checked,
          isBlur: document.getElementById("effectBlurSwitch")?.checked,
          isSub: document.getElementById("effectSubtitleSwitch")?.checked
        };

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
        setWorkflowStep("6/6 — ပြီးပါပြီ။ Final Video အသင့်ဖြစ်ပါပြီ။", "အောက်က Preview မှာ ကြည့်ပြီး Download လုပ်နိုင်ပါပြီ။");
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
        label.innerText = "One-Click Generate Recap";
      }
    }

    async function callGemini(prompt, maxOutputTokens = 8192, apiKey = (localStorage.getItem("gemini_api_key") || "").trim()) {
      if (!apiKey) throw new Error("Gemini API Key မရှိပါ။ Settings မှာ ထည့်ပါ။");
      const response = await fetch("/api/gemini", {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey },
        body: JSON.stringify({ prompt, max_output_tokens: maxOutputTokens })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || data.error?.message || `Gemini request failed (${response.status})`);
      return data;
    }

    async function copyRecapField(id) {
      const el = document.getElementById(id);
      const value = (el?.value || "").trim();
      if (!value) return showToast("Copy လုပ်ရန် စာသားမရှိသေးပါ။", "error");
      try { await navigator.clipboard.writeText(value); }
      catch (_) { el.focus(); el.select(); document.execCommand("copy"); }
      showToast("Copied!", "success");
    }

    function downloadExportedVideoFile() {
      if (!exportedRenderedVideoBlob) return showToast("No exported video file ready", "error");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(exportedRenderedVideoBlob);
      const extension = exportedRenderedVideoBlob.type.includes("mp4") ? "mp4" : "webm";
      a.download = `Recap_Go_${selectedRecapAspect.replace(":", "x")}_${Date.now()}.${extension}`;
      document.body.appendChild(a);
      a.click();
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

    const dubbingVoiceSelect = document.getElementById("dubbingVoice");
    if (dubbingVoiceSelect) {
      dubbingVoiceSelect.innerHTML = PERSONAS.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
      dubbingVoiceSelect.value = "nilar";
    }

    function applyTheme(theme) {
      const selected = theme === "light" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", selected);
      document.documentElement.classList.toggle("dark", selected === "dark");
      const toggle = document.getElementById("themeToggle");
      if (toggle) toggle.textContent = selected === "dark" ? "☀️ Light" : "🌙 Dark";
      try { localStorage.setItem("gorecap_theme", selected); } catch (_) {}
    }
    function toggleTheme() {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      applyTheme(current === "dark" ? "light" : "dark");
    }
    try { applyTheme(localStorage.getItem("gorecap_theme") || "dark"); } catch (_) { applyTheme("dark"); }


    // Editor upgrades: logo overlay, blur tuning, custom font and thumbnail tools.
    let recapLogoUrl=null, recapLogoOpacity=.9, recapLogoWidth=.22;
    let recapLogoPosition={x:.72,y:.04}, recapLogoDragging=false, recapLogoDragOffset={x:0,y:0};
    let recapSubtitleFont="Padauk";
    function installEditorEnhancements(){
      const wrap=document.getElementById("videoContainerWrapper");
      const logo=document.createElement("img"); logo.id="recapLogoOverlay"; logo.alt="Logo";
      Object.assign(logo.style,{position:"absolute",zIndex:40,display:"none",width:"22%",maxHeight:"25%",objectFit:"contain",left:"72%",top:"4%",opacity:".9",cursor:"move",touchAction:"none",filter:"drop-shadow(0 2px 5px #0008)"});
      wrap.appendChild(logo);
      logo.addEventListener("pointerdown",e=>{if(!recapLogoUrl)return;const r=logo.getBoundingClientRect();recapLogoDragging=true;recapLogoDragOffset={x:e.clientX-r.left,y:e.clientY-r.top};logo.setPointerCapture(e.pointerId);e.preventDefault();});
      logo.addEventListener("pointermove",e=>{if(!recapLogoDragging)return;const r=wrap.getBoundingClientRect();const x=Math.max(0,Math.min(r.width-logo.offsetWidth,e.clientX-r.left-recapLogoDragOffset.x));const y=Math.max(0,Math.min(r.height-logo.offsetHeight,e.clientY-r.top-recapLogoDragOffset.y));recapLogoPosition={x:x/r.width,y:y/r.height};logo.style.left=(recapLogoPosition.x*100)+"%";logo.style.top=(recapLogoPosition.y*100)+"%";});
      ["pointerup","pointercancel"].forEach(ev=>logo.addEventListener(ev,()=>recapLogoDragging=false));
      const blur=document.getElementById("blurDimensionControls");
      if(blur&&!document.getElementById("blurStrengthSlider")){
        blur.insertAdjacentHTML("beforeend",'<label class="col-span-2 text-[11px] text-slate-300">Blur strength <b id="blurStrengthTag">18px</b><input id="blurStrengthSlider" type="range" min="2" max="36" value="18" class="w-full accent-cyan-400"></label><label class="col-span-2 text-[11px] text-slate-300">Blur opacity <b id="blurOpacityTag">100%</b><input id="blurOpacitySlider" type="range" min="10" max="100" value="100" class="w-full accent-cyan-400"></label>');
        document.getElementById("blurStrengthSlider").oninput=e=>document.getElementById("blurStrengthTag").textContent=e.target.value+"px";
        document.getElementById("blurOpacitySlider").oninput=e=>document.getElementById("blurOpacityTag").textContent=e.target.value+"%";
      }
      const sub=document.getElementById("subtitleStylingCard");
      if(sub&&!document.getElementById("subFontUpload")){
        const box=document.createElement("div");box.className="p-3 rounded-2xl bg-[#080d1a] border border-slate-800 space-y-2";
        box.innerHTML='<label class="font-bold text-slate-300 block">Upload subtitle font (TTF / OTF / WOFF2)</label><input id="subFontUpload" type="file" accept=".ttf,.otf,.woff,.woff2" class="w-full text-[11px]"><p id="subFontStatus" class="text-[10px] text-slate-400">Default: Padauk</p>';sub.appendChild(box);
        document.getElementById("subFontUpload").onchange=async e=>{const file=e.target.files?.[0];if(!file)return;try{const url=URL.createObjectURL(file),face=new FontFace("GoRecapCustomFont",`url(${url})`);await face.load();document.fonts.add(face);recapSubtitleFont="GoRecapCustomFont";document.getElementById("subPreviewSpanText").style.fontFamily=recapSubtitleFont;document.getElementById("subFontStatus").textContent="Loaded: "+file.name;showToast("Subtitle font loaded","success");}catch(_){showToast("Font file ကို ဖတ်မရပါ","error");}};
      }
      const panel=document.getElementById("panelRecapVd");
      if(panel&&!document.getElementById("recapAssetTools")){
        const card=document.createElement("section");card.id="recapAssetTools";card.className="bg-[#0f172b]/95 border border-slate-800 rounded-3xl p-5 space-y-3 text-xs";
        card.innerHTML=`<div class="mb-3 p-3 rounded-2xl bg-[#080d1a] border border-slate-800 space-y-2">
          <label for="recapSourceUrlInput" class="block text-[11px] font-bold text-slate-300">Paste a direct video URL (MP4 / WebM)</label>
          <input id="recapSourceUrlInput" type="url" placeholder="https://example.com/video.mp4" class="w-full rounded-xl bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-white">
          <button id="loadSourceUrlBtn" type="button" class="w-full py-2 rounded-xl bg-blue-600 text-white font-bold">Load Direct Video URL</button>
          <p class="text-[10px] text-slate-400">TikTok / Douyin share links need an authorized download source. This field loads direct video-file URLs only; cross-origin restrictions may apply.</p>
        </div><div class="font-bold text-slate-200 text-sm">🧩 Logo & Thumbnail Tools</div><label class="block font-bold text-slate-300">Logo upload<input id="recapLogoUpload" type="file" accept="image/png,image/jpeg,image/webp" class="mt-2 block w-full"></label><label class="block text-slate-300">Logo size <b id="logoSizeTag">22%</b><input id="logoSizeSlider" type="range" min="8" max="45" value="22" class="w-full"></label><label class="block text-slate-300">Logo opacity <b id="logoOpacityTag">90%</b><input id="logoOpacitySlider" type="range" min="10" max="100" value="90" class="w-full"></label><p class="text-slate-400">Preview ထဲက Logo ကို ဆွဲရွှေ့နိုင်ပြီး Export ထဲမှာလည်း ပါဝင်ပါမယ်။</p><button id="sourceThumbBtn" type="button" class="w-full py-2.5 bg-slate-800 text-white">🖼️ Source Video Thumbnail Download</button><label class="block font-bold text-slate-300">3:4 Thumbnail Prompt<textarea id="recapThumbnailPrompt" rows="4" readonly class="mt-2 w-full"></textarea></label><button id="copyThumbPromptBtn" type="button" class="w-full py-2.5 bg-slate-800 text-white">📋 Thumbnail Prompt Copy</button>`;
        panel.insertBefore(card,document.getElementById("recapResultCard")||null);

        document.getElementById("loadSourceUrlBtn").onclick=async()=>{
          const field=document.getElementById("recapSourceUrlInput"), raw=(field.value||"").trim();
          if(!raw)return showToast("Video URL ထည့်ပေးပါ","error");
          let parsed;try{parsed=new URL(raw);}catch(_){return showToast("URL မှားနေပါတယ်","error");}
          if(!["https:","http:"].includes(parsed.protocol))return showToast("HTTP/HTTPS URL သာ အသုံးပြုနိုင်ပါတယ်","error");
          if(/(^|\\.)((tiktok\\.com)|(douyin\\.com))$/i.test(parsed.hostname.replace(/^www\\./,"")) || /tiktok|douyin/i.test(parsed.hostname)){
            return showToast("TikTok/Douyin Share Link ကို တိုက်ရိုက်မရယူနိုင်သေးပါ။ ခွင့်ပြုထားတဲ့နည်းနဲ့ MP4 ဖိုင်ရယူပြီး Upload လုပ်ပါ","error");
          }
          const button=document.getElementById("loadSourceUrlBtn");button.disabled=true;button.textContent="Downloading video file…";
          try{
            const response=await fetch(parsed.href,{mode:"cors"});
            if(!response.ok)throw new Error("Server returned HTTP "+response.status);
            const type=(response.headers.get("content-type")||"").toLowerCase();
            if(!type.startsWith("video/") && !/\\.(mp4|webm|mov|m4v)(?:$|[?#])/i.test(parsed.pathname+parsed.search))throw new Error("ဒီ URL က တိုက်ရိုက် Video ဖိုင် မဟုတ်ပါ");
            const blob=await response.blob();
            if(!blob.size)throw new Error("Video ဖိုင်အလွတ် ဖြစ်နေပါတယ်");
            if(blob.size>500*1024*1024)throw new Error("Video ဖိုင် 500MB ကျော်နေပါတယ်");
            const ext=type.includes("webm")?"webm":type.includes("quicktime")?"mov":"mp4";
            loadRecapVideoFile(new File([blob],"gorecap-import."+ext,{type:type.startsWith("video/")?type:"video/mp4"}));
          }catch(err){showToast("URL ကနေ Video မရယူနိုင်ပါ။ CORS ပိတ်ထားခြင်း သို့မဟုတ် Share Page URL ဖြစ်နိုင်ပါတယ်။ "+(err.message||""),"error");}
          finally{button.disabled=false;button.textContent="Load Direct Video URL";}
        };
        document.getElementById("recapLogoUpload").onchange=e=>{const file=e.target.files?.[0];if(!file)return;if(recapLogoUrl)URL.revokeObjectURL(recapLogoUrl);recapLogoUrl=URL.createObjectURL(file);logo.src=recapLogoUrl;logo.style.display="block";};
        document.getElementById("logoSizeSlider").oninput=e=>{recapLogoWidth=Number(e.target.value)/100;logo.style.width=e.target.value+"%";document.getElementById("logoSizeTag").textContent=e.target.value+"%";};
        document.getElementById("logoOpacitySlider").oninput=e=>{recapLogoOpacity=Number(e.target.value)/100;logo.style.opacity=String(recapLogoOpacity);document.getElementById("logoOpacityTag").textContent=e.target.value+"%";};
        document.getElementById("sourceThumbBtn").onclick=downloadSourceVideoThumbnail;
        document.getElementById("copyThumbPromptBtn").onclick=()=>copyRecapField("recapThumbnailPrompt");
      }
    }
    function downloadSourceVideoThumbnail(){
      const v=document.getElementById("recapVideoPlayerEl");if(!v?.videoWidth)return showToast("Video ကို အရင် upload လုပ်ပါ","error");
      const c=document.createElement("canvas");c.width=v.videoWidth;c.height=v.videoHeight;c.getContext("2d").drawImage(v,0,0,c.width,c.height);
      c.toBlob(b=>{if(!b)return showToast("Thumbnail ထုတ်မရပါ","error");const u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download="GoRecap_Source_Thumbnail.jpg";a.click();setTimeout(()=>URL.revokeObjectURL(u),1500);},"image/jpeg",.92);
    }
    function makeRecapThumbnailPrompt(script){
      const context=(script||"").replace(/\s+/g," ").slice(0,800);
      const el=document.getElementById("recapThumbnailPrompt");if(el)el.value="Create a cinematic ultra-realistic 3:4 vertical movie recap thumbnail. Use the source video frame as visual reference, preserve the characters and scene identity, dramatic expressive faces, strong foreground subject, cinematic lighting, sharp details, clean composition. Add bold Burmese headline text exactly here: { }. Story context: "+context+". No watermark, no extra text.";
    }

    // Init
    installEditorEnhancements();
    updateVoiceTriggerLabel();
    syncRecapSliders();
    updateSubtitleStyles();
  </script>
</body>
</html>
"""

PREVIEW_AUDIO_CACHE = {}

# 13 Real Distinct Multilingual and Native Burmese Voice Personas
PERSONA_VOICES = [
    {"id": "bunny-phyoe", "name": "ဘန်နီဖြိုး", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "-3%", "sample_text": "မင်္ဂလာပါ ဘန်နီဖြိုးပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "tayza", "name": "တေဇ", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "sample_text": "မင်္ဂလာပါ တေဇပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "aung-ye-linn", "name": "အောင်ရဲလင်း", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+2%", "sample_text": "မင်္ဂလာပါ အောင်ရဲလင်းပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "chue-lay", "name": "ချူးလေး", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+4%", "sample_text": "မင်္ဂလာပါ ချူးလေးပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "n-kai-yar", "name": "အန်ခိုင်းရာ", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+6%", "sample_text": "မင်္ဂလာပါ အန်ခိုင်းရာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "nilar", "name": "နီလာ", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "sample_text": "မင်္ဂလာပါ နီလာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "thiha", "name": "သီဟ", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "sample_text": "မင်္ဂလာပါ သီဟပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "phyo-ngwe-soe", "name": "ဖြိုးငွေစိုး", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+5%", "sample_text": "မင်္ဂလာပါ ဖြိုးငွေစိုးပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "sinn-tiyar", "name": "စင်သီယာ", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "-4%", "sample_text": "မင်္ဂလာပါ စင်သီယာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "nay-win", "name": "နေဝင်း", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+5%", "sample_text": "မင်္ဂလာပါ နေဝင်းပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "eaindra-bo", "name": "အိန္ဒြာဘို", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "sample_text": "မင်္ဂလာပါ အိန္ဒြာဘိုပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "ji-chaung-wook", "name": "ဂျီချန်ဝု", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "-2%", "sample_text": "မင်္ဂလာပါ ဂျီချန်ဝုပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "aye-thidar", "name": "အေးသီတာ", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+2%", "sample_text": "မင်္ဂလာပါ အေးသီတာပါ ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"}
]
PERSONA_DICT = {p["id"]: p for p in PERSONA_VOICES}

class GenerateTTSRequest(BaseModel):
    text: str
    persona_id: str = "bunny-phyoe"
    user_rate_offset: int = 0
    user_pitch_offset: int = 0

def fetch_google_tts_burmese(text: str) -> bytes:
    try:
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(text)}&tl=my&client=tw-ob"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Referer": "https://translate.google.com/"
            }
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            return resp.read()
    except Exception:
        return b""

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
    if persona_id in PREVIEW_AUDIO_CACHE:
        return Response(
            content=PREVIEW_AUDIO_CACHE[persona_id],
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=86400", "Accept-Ranges": "bytes"}
        )

    persona = PERSONA_DICT.get(persona_id, PERSONA_VOICES[0])
    
    # 1. Native Edge-TTS Voice synthesis
    try:
        communicate = edge_tts.Communicate(
            text=persona["sample_text"],
            voice=persona["base_voice"],
            rate=persona.get("base_rate", "+0%")
        )
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if audio_data and len(audio_data) > 300:
            PREVIEW_AUDIO_CACHE[persona_id] = audio_data
            return Response(
                content=audio_data,
                media_type="audio/mpeg",
                headers={"Cache-Control": "public, max-age=86400", "Accept-Ranges": "bytes"}
            )
    except Exception:
        pass

    # 2. Instant Zero-Fail Google Burmese TTS Fallback
    fallback_audio = fetch_google_tts_burmese(persona["sample_text"])
    if fallback_audio and len(fallback_audio) > 100:
        PREVIEW_AUDIO_CACHE[persona_id] = fallback_audio
        return Response(
            content=fallback_audio,
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=86400", "Accept-Ranges": "bytes"}
        )

    raise HTTPException(status_code=500, detail="Voice sample synthesis failed")

@app.post("/api/tts")
@app.post("/tts")
async def generate_speech(req: GenerateTTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="စာသား ထည့်သွင်းပေးရန် လိုအပ်ပါသည်။")
    
    persona = PERSONA_DICT.get(req.persona_id, PERSONA_VOICES[0])
    base_r = int(persona.get("base_rate", "+0%").replace("%", "").replace("+", ""))
    total_rate = max(-50, min(50, base_r + req.user_rate_offset))
    pitch_offset = max(-15, min(15, req.user_pitch_offset))
    rate_str = f"{'+' if total_rate >= 0 else ''}{total_rate}%"
    pitch_str = f"{pitch_offset:+d}Hz"

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
        if audio_data and len(audio_data) > 500:
            return Response(content=audio_data, media_type="audio/mpeg")
    except Exception:
        pass

    fallback_audio = fetch_google_tts_burmese(req.text.strip())
    if fallback_audio and len(fallback_audio) > 200:
        return Response(content=fallback_audio, media_type="audio/mpeg")
    
    raise HTTPException(status_code=500, detail="Voice synthesis failed")

@app.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    authorization: str = Header(default="")
):
    """Proxy Whisper requests server-side to avoid browser-to-Groq fetch/CORS failures."""
    api_key = authorization.removeprefix("Bearer ").strip()
    if not api_key:
        raise HTTPException(status_code=401, detail="Groq API Key မတွေ့ပါ။ Settings မှာ စစ်ဆေးပါ။")

    audio_bytes = await file.read(4 * 1024 * 1024 + 1)
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio ဖိုင်အလွတ်ဖြစ်နေပါတယ်။")
    if len(audio_bytes) > 4 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio ဖိုင် 4MB ကျော်နေပါတယ်။ Video ကို ပိုတိုအောင် ဖြတ်ပြီး ပြန်စမ်းပါ။")

    boundary = "----GoRecapWhisperBoundary7MA4YWxkTrZu0gW"
    filename = (file.filename or "gorecap-audio.webm").replace('"', "")
    content_type = file.content_type or "audio/webm"
    parts = []
    for name, value in (("model", "whisper-large-v3-turbo"), ("response_format", "json")):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        )
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode()
        + audio_bytes + b"\r\n"
    )
    body = b"".join(parts) + f"--{boundary}--\r\n".encode()

    def call_groq():
        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Accept": "application/json",
                "User-Agent": "GoRecap/1.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=50) as response:
                import json
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            import json
            raw = error.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(raw).get("error", {}).get("message", raw)
            except Exception:
                detail = raw or str(error)
            raise HTTPException(status_code=error.code, detail=f"Groq Whisper: {detail[:500]}")
        except Exception as error:
            raise HTTPException(status_code=502, detail=f"Groq Whisper connection failed: {str(error)[:300]}")

    return await asyncio.to_thread(call_groq)


class GeminiGenerateRequest(BaseModel):
    prompt: str
    max_output_tokens: int = 8192
    temperature: float = 0.25


@app.post("/api/gemini")
async def generate_gemini_text(
    req: GeminiGenerateRequest,
    x_goog_api_key: str = Header(default="")
):
    """Server-side Gemini proxy; keeps API keys out of query strings."""
    api_key = x_goog_api_key.strip()
    if not api_key:
        raise HTTPException(status_code=401, detail="Gemini API Key မတွေ့ပါ။ Settings မှာ စစ်ဆေးပါ။")
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt အလွတ်ဖြစ်နေပါတယ်။")
    if len(req.prompt) > 180000:
        raise HTTPException(status_code=413, detail="Prompt အလွန်ရှည်နေပါတယ်။")
    payload = {
        "contents": [{"parts": [{"text": req.prompt}]}],
        "generationConfig": {
            "temperature": max(0.0, min(1.0, req.temperature)),
            "maxOutputTokens": max(256, min(16384, req.max_output_tokens))
        }
    }

    def call_gemini():
        import json
        request = urllib.request.Request(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "GoRecap/2.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=50) as response:
                result = json.loads(response.read().decode("utf-8"))
            parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            output = "\n".join(part.get("text", "") for part in parts if part.get("text")).strip()
            if not output:
                reason = result.get("promptFeedback", {}).get("blockReason") or result.get("candidates", [{}])[0].get("finishReason", "empty response")
                raise HTTPException(status_code=502, detail=f"Gemini returned no text: {reason}")
            return {"text": output, "model": result.get("modelVersion", "gemini-3.8-flash")}
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(raw).get("error", {}).get("message", raw)
            except Exception:
                detail = raw or str(error)
            raise HTTPException(status_code=error.code, detail=f"Gemini API: {detail[:600]}")
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=502, detail=f"Gemini connection failed: {str(error)[:300]}")

    return await asyncio.to_thread(call_gemini)


@app.get("/{full_path:path}")
def catch_all_routes(full_path: str):
    return HTMLResponse(content=HTML_CONTENT)
