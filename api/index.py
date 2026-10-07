# STREAMING_CHUNK:Configuring FastAPI server and core imports...
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

# STREAMING_CHUNK:Defining HTML UI styling, scripts and responsive layout...
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
    #draggableSubtitleBox {
      touch-action: none;
      user-select: none;
      cursor: move;
    }
    .resize-handle {
      touch-action: none;
      user-select: none;
      cursor: nwse-resize;
    }
    .video-cover-fill {
      object-fit: cover !important;
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
              Pro Studio
            </span>
          </div>
          <p class="text-[10px] text-slate-400">Burmese Video Recap & Dubbing</p>
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

        <!-- Live Video Preview Box with Draggable Subtitle & Blur Box -->
        <div id="recapVideoPreviewBox" class="hidden space-y-3 bg-[#080d1a] border border-blue-500/40 rounded-2xl p-3.5">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-blue-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span id="aspectRatioLabelTag">Aspect: 9:16 (Zoom Fill)</span>
            </span>
            <label for="recapVideoFileInput" class="text-blue-400 hover:underline cursor-pointer text-[11px] font-bold">Change</label>
          </div>

          <!-- Video Wrapper -->
          <div
            id="videoContainerWrapper"
            class="relative overflow-hidden rounded-2xl bg-[#030712] border border-slate-800 aspect-[9/16] w-full max-w-[310px] mx-auto flex items-center justify-center select-none shadow-2xl transition-all duration-300"
          >
            <!-- Blurred clone background layer -->
            <video id="recapBlurredBackdropEl" class="absolute inset-0 w-full h-full object-cover filter blur-lg opacity-40 scale-110 pointer-events-none" muted playsinline></video>

            <!-- Main video layer -->
            <video id="recapVideoPlayerEl" controls playsinline muted class="relative z-10 w-full h-full video-cover-fill transition-all duration-300"></video>

            <!-- Moveable & Resizable Blur Box -->
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

            <!-- Moveable Subtitles Layer (Shown only when Subtitles switch is ON) -->
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

      <!-- 2. OUTPUT FORMAT (ASPECT RATIO PREVIEWS 9:16 & 16:9) -->
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
          <!-- YouTube (16:9) -->
          <div onclick="selectAspectRatio('16:9')" id="aspectCard16_9" class="aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-8 h-4.5 rounded-sm border-2 border-slate-400 aspect-video mb-1"></div>
            <span class="font-bold text-slate-100 block">YouTube</span>
            <span class="text-[10px] text-slate-400 block font-mono">16:9 Landscape</span>
          </div>

          <!-- TikTok (9:16) -->
          <div onclick="selectAspectRatio('9:16')" id="aspectCard9_16" class="aspect-card p-4 rounded-2xl bg-blue-950/40 border-2 border-blue-500 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center ring-1 ring-blue-500/50 shadow-lg shadow-blue-500/20">
            <div class="w-4 h-7 rounded-sm border-2 border-blue-400 aspect-[9/16] mb-1"></div>
            <span class="font-bold text-blue-300 block">TikTok</span>
            <span class="text-[10px] text-blue-400/90 block font-mono">9:16 Portrait</span>
          </div>

          <!-- Square (1:1) -->
          <div onclick="selectAspectRatio('1:1')" id="aspectCard1_1" class="aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-5 h-5 rounded-sm border-2 border-slate-400 mb-1"></div>
            <span class="font-bold text-slate-100 block">Square</span>
            <span class="text-[10px] text-slate-400 block font-mono">1:1</span>
          </div>

          <!-- Classic (4:3) -->
          <div onclick="selectAspectRatio('4:3')" id="aspectCard4_3" class="aspect-card p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-6 h-4.5 rounded-sm border-2 border-slate-400 aspect-[4/3] mb-1"></div>
            <span class="font-bold text-slate-100 block">Classic</span>
            <span class="text-[10px] text-slate-400 block font-mono">4:3</span>
          </div>

          <!-- Portrait (3:4) -->
          <div onclick="selectAspectRatio('3:4')" id="aspectCard3_4" class="aspect-card col-span-2 p-4 rounded-2xl bg-[#080d1a] border border-slate-800 hover:border-blue-500/60 cursor-pointer transition-all space-y-1.5 flex flex-col items-center justify-center">
            <div class="w-4.5 h-6 rounded-sm border-2 border-slate-400 aspect-[3/4] mb-1"></div>
            <span class="font-bold text-slate-100 block">Portrait</span>
            <span class="text-[10px] text-slate-400 block font-mono">3:4</span>
          </div>
        </div>
      </div>

      <!-- 3. CUSTOM VOICE SELECTION (WITH IN-LINE TEST VOICE BUTTONS AS IN REFERENCE) -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs relative">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
          <span class="font-bold text-slate-200 text-sm flex items-center gap-2">
            <span class="text-blue-400">🔊</span>
            <span>Voice အသံရွေးရန်</span>
          </span>
          <span class="text-[10px] text-blue-400 font-mono">13 Voices Available</span>
        </div>

        <!-- Custom Dropdown Trigger Button -->
        <div class="relative">
          <button
            type="button"
            id="voiceDropdownTriggerBtn"
            onclick="toggleVoiceDropdownMenu(event)"
            class="w-full bg-[#080d1a] border border-slate-700/80 hover:border-blue-500 rounded-2xl p-3.5 flex items-center justify-between text-slate-100 font-bold transition-all shadow-md active:scale-[0.99]"
          >
            <div class="flex items-center gap-2.5 truncate">
              <span class="text-blue-400 text-sm font-mono tracking-tighter animate-pulse">||||</span>
              <span id="selectedVoiceLabel" class="text-sm font-bold text-white truncate">တေဇ - Tayza (Male)</span>
            </div>
            <span class="text-slate-400 text-xs ml-2">▼</span>
          </button>

          <!-- Floating Voice Selection Menu with In-line Test Voice Buttons -->
          <div
            id="customVoiceDropdownMenu"
            class="hidden absolute left-0 right-0 top-full mt-2 z-50 bg-[#0d162a]/95 border border-slate-700/90 rounded-2xl shadow-2xl backdrop-blur-xl p-2 space-y-1 max-h-72 overflow-y-auto custom-scroll"
          >
            <!-- Injected via JavaScript with Name, Gender, and [Test Voice] button -->
          </div>
        </div>
      </div>

      <!-- 4. EFFECTS & BYPASS (WITH SUBTITLES TOGGLE SWITCH) -->
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl backdrop-blur-md text-xs">
        <div class="border-b border-slate-800 pb-2 flex items-center justify-between">
          <span class="font-bold text-slate-200 text-sm">Effects & Bypass</span>
          <span class="text-[10px] text-slate-500 font-mono">Custom Settings</span>
        </div>

        <!-- Subtitles Toggle Switch -->
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

        <!-- Copyright Bypass (Dynamic Zoom) -->
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

        <!-- Moveable & Resizable Blur Shape Box -->
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

          <!-- Blur Box Dimension Sliders -->
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
            <span>Subtitle Customizer (စာတန်း အရောင်နှင့် အရွယ်အစား)</span>
          </div>
          <span class="text-[10px] text-emerald-400 font-bold">Active</span>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <!-- Text Color Picker -->
          <div class="p-2.5 rounded-2xl bg-[#080d1a] border border-slate-800 space-y-1.5">
            <label class="text-[11px] font-bold text-slate-300 block">စာသားအရောင် (Text Color)</label>
            <div class="flex items-center gap-2">
              <input type="color" id="subTextColorInput" value="#fde047" onchange="updateSubtitleStyles()" class="w-8 h-8 rounded-lg cursor-pointer bg-transparent border-0" />
              <span id="subTextColorCode" class="font-mono text-[10px] text-slate-400">#fde047</span>
            </div>
          </div>

          <!-- Border / Stroke Color Picker -->
          <div class="p-2.5 rounded-2xl bg-[#080d1a] border border-slate-800 space-y-1.5">
            <label class="text-[11px] font-bold text-slate-300 block">ဘောင်အရောင် (Border / Stroke)</label>
            <div class="flex items-center gap-2">
              <input type="color" id="subBorderColorInput" value="#000000" onchange="updateSubtitleStyles()" class="w-8 h-8 rounded-lg cursor-pointer bg-transparent border-0" />
              <span id="subBorderColorCode" class="font-mono text-[10px] text-slate-400">#000000</span>
            </div>
          </div>
        </div>

        <!-- Subtitle Size Slider -->
        <div class="space-y-1.5 p-2.5 rounded-2xl bg-[#080d1a] border border-slate-800">
          <div class="flex justify-between items-center">
            <span class="font-bold text-slate-300">စာသားအရွယ်အစား (Font Size)</span>
            <span id="subSizeLabel" class="font-mono text-amber-400 font-bold">18px</span>
          </div>
          <input type="range" id="subSizeRange" min="12" max="32" step="1" value="18" oninput="updateSubtitleStyles()" class="w-full accent-amber-500 cursor-pointer" />
        </div>

        <p class="text-[10px] text-slate-400 text-center font-mono">
          💡 အပေါ်ရှိ ဗီဒီယိုပေါ်တွင် စာတန်း Box လေးကို လက်ဖြင့် ဖိဆွဲပြီး ကြိုက်သည့်နေရာသို့ ရွှေ့ထားနိုင်ပါသည်။
        </p>
      </div>

      <!-- 6. VOICE SETTINGS CARD WITH 1.20X PACING SYNC -->
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

      <!-- 7. MAIN GENERATE RECAP BUTTON -->
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
          <span class="text-blue-400">📤</span>
          <span>File Upload</span>
        </div>
        <p class="text-xs text-slate-300">AI Transcriber mode is ready.</p>
        <button onclick="switchStudioView('recapvd')" class="w-full py-3 rounded-2xl bg-blue-600 text-white font-bold text-xs">Go to Auto Recap VD</button>
      </div>
    </div>

    <!-- VIEW 3: TTS VOICE OVER STUDIO -->
    <div id="panelTts" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3.5 shadow-2xl">
        <div class="flex items-center justify-between text-xs border-b border-slate-800 pb-2.5">
          <span class="font-bold text-blue-400 text-sm">📄 Burmese Script</span>
        </div>
        <textarea id="ttsInputTextArea" rows="5" class="w-full bg-[#080d1a] border border-slate-800 rounded-2xl p-4 text-xs leading-relaxed text-slate-100 focus:outline-none focus:border-blue-500 custom-scroll resize-y">သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>
        <button onclick="switchStudioView('recapvd')" class="w-full py-3 rounded-2xl bg-blue-600 text-white font-bold text-xs">Open in Auto Recap VD</button>
      </div>
    </div>

    <!-- VIEW 4: AUTO DUBBING MODE -->
    <div id="panelDubbing" class="hidden space-y-4">
      <div class="bg-[#0f172b]/95 border border-slate-800/90 rounded-3xl p-5 space-y-3 shadow-2xl text-xs">
        <h3 class="font-bold text-sm text-cyan-400 flex items-center gap-2 border-b border-slate-800 pb-3">
          <span>🎧</span><span>Auto Dubbing Mode</span>
        </h3>
        <p class="text-slate-300 leading-relaxed">Translate original speech with timestamps and replace audio with synchronized voiceover.</p>
        <button onclick="switchStudioView('recapvd')" class="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold">Open Auto Recap VD</button>
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
    // 13 Voices Catalog with Burmese names & guaranteed working native voices
    const PERSONAS = [
      { id: "tayza", name: "တေဇ - Tayza", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aung-ye-linn", name: "အောင်ရဲလင်း - Aung Ye' Linn", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "chue-lay", name: "ချူးလေး - Chue Lay", gender: "women", badge: "Female", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "n-kai-yar", name: "အန်ခိုင်းရာ - N Kai Yar", gender: "women", badge: "Female", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nilar", name: "နီလာ - Nilar", gender: "women", badge: "Female", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "thiha", name: "သီဟ - Thiha", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "phyo-ngwe-soe", name: "ဖြိုးငွေစိုး - Phyo Ngwe Soe", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "sinn-tiyar", name: "စင်သီယာ - Sinn Tiyar", gender: "women", badge: "Female", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "nay-win", name: "နေဝင်း - Nay Win", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "eaindra-bo", name: "အိန္ဒြာဘို - Eaindra Bo", gender: "women", badge: "Female", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" },
      { id: "bunny-phyoe", name: "ဘန်နီဖြိုး - Bunny Phyoe", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "ji-chaung-wook", name: "ဂျီချန်ဝု - Ji Chaung Wook", gender: "men", badge: "Male", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ" },
      { id: "aye-thidar", name: "အေးသီတာ - Aye Thidar", gender: "women", badge: "Female", sample: "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်" }
    ];

    let currentSelectedVoiceId = "tayza";
    let isSampleAudioPlaying = false;
    let currentlyPlayingVoiceId = null;
    let isVoiceMenuOpen = false;
    let selectedRecapAspect = "9:16";
    let currentUploadedRecapFile = null;
    let generatedRecapAudioBlob = null;
    let exportedRenderedVideoBlob = null;
    let videoDurationSeconds = 0;

    // Draggable Blur Box State (Normalized 0.0 - 1.0)
    let blurBoxRect = { x: 0.22, y: 0.72, w: 0.55, h: 0.15 };
    let isDraggingBlur = false, isResizingBlur = false;
    let blurDragStartX = 0, blurDragStartY = 0;
    let blurInitialWidth = 160, blurInitialHeight = 50;

    // Draggable Subtitle Box State (Normalized 0.0 - 1.0)
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

      if (tool === "transcriber") {
        pTrans.classList.remove("hidden");
      } else if (tool === "tts") {
        pTts.classList.remove("hidden");
      } else if (tool === "dubbing") {
        pDub.classList.remove("hidden");
      } else {
        pRecap.classList.remove("hidden");
        renderCustomVoiceDropdownMenu();
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
    // CUSTOM VOICE DROPDOWN MENU & IN-LINE "TEST VOICE" BUTTONS (IMAGE 1000049252.jpg)
    // =========================================================================
    function toggleVoiceDropdownMenu(e) {
      if (e) e.stopPropagation();
      isVoiceMenuOpen = !isVoiceMenuOpen;
      const menu = document.getElementById("customVoiceDropdownMenu");
      if (isVoiceMenuOpen) {
        menu.classList.remove("hidden");
        renderCustomVoiceDropdownMenu();
      } else {
        menu.classList.add("hidden");
      }
    }

    document.addEventListener("click", function(e) {
      const menu = document.getElementById("customVoiceDropdownMenu");
      const trigger = document.getElementById("voiceDropdownTriggerBtn");
      if (menu && !menu.contains(e.target) && !trigger.contains(e.target)) {
        menu.classList.add("hidden");
        isVoiceMenuOpen = false;
      }
    });

    function renderCustomVoiceDropdownMenu() {
      const menu = document.getElementById("customVoiceDropdownMenu");
      const currentVoice = PERSONAS.find(p => p.id === currentSelectedVoiceId) || PERSONAS[0];
      document.getElementById("selectedVoiceLabel").innerText = `${currentVoice.name} (${currentVoice.badge})`;

      menu.innerHTML = PERSONAS.map(p => {
        const isSelected = p.id === currentSelectedVoiceId;
        const isPlaying = currentlyPlayingVoiceId === p.id;

        return `
          <div
            onclick="selectCustomVoice('${p.id}', event)"
            class="p-2.5 rounded-xl cursor-pointer transition-all flex items-center justify-between gap-2 ${
              isSelected ? 'bg-blue-600/25 border border-blue-500/50 text-white' : 'hover:bg-slate-800/80 text-slate-200'
            }"
          >
            <div class="flex items-center gap-2 truncate">
              <span class="font-bold text-xs sm:text-sm truncate">${p.name} (${p.badge})</span>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onclick="playTestVoiceAudio('${p.id}', event)"
                class="px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1 transition-all ${
                  isPlaying
                    ? 'bg-blue-600 text-white animate-pulse shadow-md'
                    : 'bg-slate-800 hover:bg-slate-700 text-blue-300 border border-slate-700/80'
                }"
              >
                <span>${isPlaying ? '⏹' : '🔊'}</span>
                <span>${isPlaying ? 'Stop' : 'Test Voice'}</span>
              </button>
              ${isSelected ? '<span class="text-blue-400 font-extrabold text-sm">✓</span>' : ''}
            </div>
          </div>
        `;
      }).join("");
    }

    function selectCustomVoice(voiceId, e) {
      if (e) e.stopPropagation();
      currentSelectedVoiceId = voiceId;
      const p = PERSONAS.find(x => x.id === voiceId);
      document.getElementById("selectedVoiceLabel").innerText = `${p.name} (${p.badge})`;
      document.getElementById("customVoiceDropdownMenu").classList.add("hidden");
      isVoiceMenuOpen = false;
      showToast(`Selected: ${p.name}`, "info");
    }

    async function playTestVoiceAudio(voiceId, e) {
      if (e) e.stopPropagation();
      const pAudio = document.getElementById("samplePreviewAudio");

      if (currentlyPlayingVoiceId === voiceId) {
        pAudio.pause();
        currentlyPlayingVoiceId = null;
        renderCustomVoiceDropdownMenu();
        return;
      }

      currentlyPlayingVoiceId = voiceId;
      renderCustomVoiceDropdownMenu();

      try {
        let res = await fetch(`/api/preview/${voiceId}`);
        if (!res.ok) res = await fetch(`/preview/${voiceId}`);
        if (res.ok) {
          const blob = await res.blob();
          pAudio.src = URL.createObjectURL(blob);
          await pAudio.play();
          return;
        }
      } catch (err) {}

      currentlyPlayingVoiceId = null;
      renderCustomVoiceDropdownMenu();
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ", "error");
    }

    document.getElementById("samplePreviewAudio").onended = () => {
      currentlyPlayingVoiceId = null;
      renderCustomVoiceDropdownMenu();
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
      const bgClone = document.getElementById("recapBlurredBackdropEl");
      const url = URL.createObjectURL(file);

      vEl.src = url;
      bgClone.src = url;

      vEl.onloadedmetadata = () => {
        videoDurationSeconds = Math.round(vEl.duration) || 180;
      };

      toggleEffectPreview();
      showToast(`Video loaded: ${file.name} (${sizeMB} MB)`, "success");
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
      subSpan.style.textShadow = `-2px -2px 0 ${borderColor}, 2px -2px 0 ${borderColor}, -2px 2px 0 ${borderColor}, 2px 2px 0 ${borderColor}, 0 4px 8px rgba(0,0,0,0.8)`;
      subBox.style.backgroundColor = "rgba(0, 0, 0, 0.75)";
      subBox.style.border = `1.5px solid ${borderColor}`;
    }

    // Draggable Subtitle Box Handling
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
      document.getElementById("blurHTag").innerText = `${newH}px`;

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

      // Transforms
      let transformStr = "";
      if (isMirror) transformStr += "scaleX(-1) ";
      if (isZoom) transformStr += "scale(1.12) ";
      vEl.style.transform = transformStr || "none";

      // Pro Color Grading: Bright +15, Sat +15, Warmth +15, Contrast +15, Tint +5
      let filterStr = "";
      if (isColor) {
        filterStr += "brightness(1.15) contrast(1.15) saturate(1.15) sepia(0.15) hue-rotate(-5deg) ";
      }
      vEl.style.filter = filterStr || "none";

      // Moveable & Resizable Blur Box
      if (isBlur) {
        blurBoxEl.classList.remove("hidden");
        blurControls.classList.remove("hidden");
      } else {
        blurBoxEl.classList.add("hidden");
        blurControls.classList.add("hidden");
      }

      // Moveable Subtitles Layer & Settings Card
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

    // =========================================================================
    // ADVANCED COMPOSITOR (ZERO BLACK MARGINS, CUSTOM SUBTITLES & MOVING BLUR)
    // =========================================================================
    async function renderAndExportComposedVideo(videoFile, audioBlob, scriptText, targetAspect, effects, targetDuration, playbackSpeed) {
      return new Promise(async (resolve, reject) => {
        try {
          const canvas = document.getElementById("offscreenRenderCanvas");
          const ctx = canvas.getContext("2d");

          let targetW = 720, targetH = 1280; // 9:16 portrait
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

          sourceVideo.playbackRate = playbackSpeed || 1.20;

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
          const totalExpectedDuration = Math.max(12, Math.min(targetDuration || 180, 480));

          function renderFrame(now) {
            const elapsed = (now - startTimeStamp) / 1000;

            if (elapsed >= totalExpectedDuration || (speechAudio.ended && sourceVideo.currentTime >= (sourceVideo.duration * 0.95))) {
              cancelAnimationFrame(animationFrameId);
              mediaRecorder.stop();
              return;
            }

            // 1. Draw soft blurred backdrop clone (Zero black bars!)
            ctx.save();
            ctx.filter = "blur(14px) opacity(0.85)";
            ctx.drawImage(sourceVideo, 0, 0, targetW, targetH);
            ctx.restore();

            ctx.save();

            // 2. Mirror transform
            if (effects.isMirror) {
              ctx.translate(targetW, 0);
              ctx.scale(-1, 1);
            }

            // 3. Dynamic Bypass Zoom (Smooth breathing scale)
            let zoomScale = 1.0;
            if (effects.isZoom) {
              zoomScale = 1.10 + 0.04 * Math.sin(elapsed * 0.4);
              ctx.translate(targetW / 2, targetH / 2);
              ctx.scale(zoomScale, zoomScale);
              ctx.translate(-targetW / 2, -targetH / 2);
            }

            // 4. Pro Color Grading Filter (Bright 15+, Sat 15+, Warmth 15+, Contrast 15+, Tint 5+)
            if (effects.isColor) {
              ctx.filter = "brightness(1.15) contrast(1.15) saturate(1.15) sepia(0.15) hue-rotate(-5deg)";
            } else {
              ctx.filter = "none";
            }

            // 5. COVER & ZOOM FILL (Eliminates all top/bottom black margins)
            const scale = Math.max(targetW / sourceVideo.videoWidth, targetH / sourceVideo.videoHeight);
            const drawW = sourceVideo.videoWidth * scale;
            const drawH = sourceVideo.videoHeight * scale;
            const drawX = (targetW - drawW) / 2;
            const drawY = (targetH - drawH) / 2;

            ctx.drawImage(sourceVideo, drawX, drawY, drawW, drawH);
            ctx.restore();

            // 6. Resizable & Moveable Blur Box on Canvas
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

              ctx.strokeStyle = "rgba(255,255,255,0.2)";
              ctx.lineWidth = 2;
              ctx.strokeRect(bx, by, bw, bh);
            }

            // 7. Custom Position, Color & Sized Subtitles rendering
            if (effects.isSub && sentences.length > 0) {
              const audioDur = speechAudio.duration || totalExpectedDuration;
              const progress = Math.min(1.0, speechAudio.currentTime / audioDur);
              const curIdx = Math.min(sentences.length - 1, Math.floor(progress * sentences.length));
              const textToDraw = sentences[curIdx]?.trim() || "";

              if (textToDraw) {
                ctx.save();
                const renderedFontSize = Math.round((subStyles.fontSize / 18) * (targetW * 0.04));
                ctx.font = `bold ${renderedFontSize}px Padauk, sans-serif`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";

                const subX = (subBoxPos.x + 0.4) * targetW;
                const subY = (subBoxPos.y + 0.05) * targetH;
                const textWidth = ctx.measureText(textToDraw).width;
                const padX = 24, padY = 14;

                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.roundRect(
                  subX - textWidth / 2 - padX,
                  subY - padY,
                  textWidth + padX * 2,
                  padY * 2,
                  12
                );
                ctx.fill();

                ctx.lineWidth = 3;
                ctx.strokeStyle = subStyles.borderColor;
                ctx.strokeText(textToDraw, subX, subY);

                ctx.fillStyle = subStyles.textColor;
                ctx.fillText(textToDraw, subX, subY);
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

    // Auto Recap VD Execute Workflow
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
        const durSecs = videoDurationSeconds || 180;
        const targetWords = Math.max(180, Math.min(520, Math.round(durSecs * 2.2)));

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

        label.innerText = "3/3: ဗီဒီယိုနှင့် အသံ ပေါင်းစပ် ထုတ်လုပ်နေပါသည်...";
        showToast("Color Grading, Blur, Zoom နှင့် အသံ ပေါင်းစပ်နေပါသည်...", "info");

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
    renderCustomVoiceDropdownMenu();
    syncRecapSliders();
    updateSubtitleStyles();
  </script>
</body>
</html>
"""

# STREAMING_CHUNK:Configuring Edge-TTS personas catalog with strictly quoted keys...
PERSONA_VOICES = [
    {"id": "tayza", "name": "တေဇ - Tayza", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "base_pitch": "-4Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "aung-ye-linn", "name": "အောင်ရဲလင်း - Aung Ye' Linn", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+2%", "base_pitch": "+2Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "chue-lay", "name": "ချူးလေး - Chue Lay", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+4%", "base_pitch": "+6Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "n-kai-yar", "name": "အန်ခိုင်းရာ - N Kai Yar", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+6%", "base_pitch": "+10Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "nilar", "name": "နီလာ - Nilar", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "thiha", "name": "သီဟ - Thiha", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+0%", "base_pitch": "+0Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "phyo-ngwe-soe", "name": "ဖြိုးငွေစိုး - Phyo Ngwe Soe", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+5%", "base_pitch": "+8Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "sinn-tiyar", "name": "စင်သီယာ - Sinn Tiyar", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "-4%", "base_pitch": "-4Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "nay-win", "name": "နေဝင်း - Nay Win", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "+6%", "base_pitch": "+4Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "eaindra-bo", "name": "အိန္ဒြာဘို - Eaindra Bo", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+0%", "base_pitch": "-6Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"},
    {"id": "bunny-phyoe", "name": "ဘန်နီဖြိုး - Bunny Phyoe", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "-4%", "base_pitch": "-10Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "ji-chaung-wook", "name": "ဂျီချန်ဝု - Ji Chaung Wook", "gender": "men", "base_voice": "my-MM-ThihaNeural", "base_rate": "-2%", "base_pitch": "+3Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"},
    {"id": "aye-thidar", "name": "အေးသီတာ - Aye Thidar", "gender": "women", "base_voice": "my-MM-NilarNeural", "base_rate": "+2%", "base_pitch": "+4Hz", "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"}
]
PERSONA_DICT = {p["id"]: p for p in PERSONA_VOICES}

class GenerateTTSRequest(BaseModel):
    text: str
    persona_id: str = "tayza"
    user_rate_offset: int = 0
    user_pitch_offset: int = 0

# STREAMING_CHUNK:Declaring route handlers for web pages and Edge-TTS synthesis...
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
        fallback_voice = "my-MM-ThihaNeural" if persona.get("gender") == "men" else "my-MM-NilarNeural"
        try:
            communicate = edge_tts.Communicate(
                text=persona["sample_text"],
                voice=fallback_voice,
                rate="+0%",
                pitch="+0Hz"
            )
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return Response(content=audio_data, media_type="audio/mpeg")
        except Exception:
            raise HTTPException(status_code=500, detail="Voice synthesis failed")

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
        fallback_voice = "my-MM-ThihaNeural" if persona.get("gender") == "men" else "my-MM-NilarNeural"
        try:
            communicate = edge_tts.Communicate(
                text=req.text.strip(),
                voice=fallback_voice,
                rate=rate_str,
                pitch=pitch_str
            )
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return Response(content=audio_data, media_type="audio/mpeg")
        except Exception:
            raise HTTPException(status_code=500, detail=str(e))

# STREAMING_CHUNK:Handling catch-all fallback routes...
@app.get("/{full_path:path}")
def catch_all_routes(full_path: str):
    return HTMLResponse(content=HTML_CONTENT)
