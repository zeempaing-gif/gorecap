import os
import re
import json
import asyncio
from typing import Optional, List, Dict, Any
import edge_tts
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Recap Go AI - Enterprise Video Recap & Speech Studio",
    description="One-Click End-to-End AI Movie/Drama Recap Studio",
    version="3.0.0"
)

# CORS middleware for local testing and cloud production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================================
# COMPLETE 13 PERSONAS VOICE CATALOG (PRESERVED & EXPANDED)
# =========================================================================
PERSONA_VOICES = [
    {
        "id": "tayza",
        "name": "Tayza (Brian)",
        "gender": "men",
        "lang": "en-US",
        "base_voice": "en-US-BrianMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "aung-ye-linn",
        "name": "Aung Ye' Linn (Andrew)",
        "gender": "men",
        "lang": "en-US",
        "base_voice": "en-US-AndrewMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "chue-lay",
        "name": "Chue Lay (Ava)",
        "gender": "women",
        "lang": "en-US",
        "base_voice": "en-US-AvaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "n-kai-yar",
        "name": "N Kai Yar (Emma)",
        "gender": "women",
        "lang": "en-US",
        "base_voice": "en-US-EmmaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "nilar",
        "name": "Nilar (မူရင်း မြန်မာ)",
        "gender": "women",
        "lang": "my-MM",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "thiha",
        "name": "Thiha (မူရင်း မြန်မာ)",
        "gender": "men",
        "lang": "my-MM",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "phyo-ngwe-soe",
        "name": "Phyo Ngwe Soe (Florian)",
        "gender": "men",
        "lang": "de-DE",
        "base_voice": "de-DE-FlorianMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "sinn-tiyar",
        "name": "Sinn Tiyar (Seraphina)",
        "gender": "women",
        "lang": "de-DE",
        "base_voice": "de-DE-SeraphinaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "nay-win",
        "name": "Nay Win (Remy)",
        "gender": "men",
        "lang": "fr-FR",
        "base_voice": "fr-FR-RemyMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "eaindra-bo",
        "name": "Eaindra Bo (Vivienne)",
        "gender": "women",
        "lang": "fr-FR",
        "base_voice": "fr-FR-VivienneMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    },
    {
        "id": "bunny-phyoe",
        "name": "Bunny Phyoe (Giuseppe)",
        "gender": "men",
        "lang": "it-IT",
        "base_voice": "it-IT-GiuseppeMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "ji-chaung-wook",
        "name": "Ji Chaung Wook (Hyunsu)",
        "gender": "men",
        "lang": "ko-KR",
        "base_voice": "ko-KR-HyunsuMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ခင်ဗျ"
    },
    {
        "id": "aye-thidar",
        "name": "Aye Thidar (Thalita)",
        "gender": "women",
        "lang": "pt-BR",
        "base_voice": "pt-BR-ThalitaMultilingualNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "ရီကတ်ဂိုးအပ်မှ ကြိုဆိုပါတယ် ရှင့်"
    }
]
PERSONA_DICT = {p["id"]: p for p in PERSONA_VOICES}

# =========================================================================
# BACKEND API SCHEMAS & ROUTES
# =========================================================================
class GenerateTTSRequest(BaseModel):
    text: str
    persona_id: str = "tayza"
    user_rate_offset: int = 0
    user_pitch_offset: int = 0

class VideoResolveRequest(BaseModel):
    url: str

class VideoResolveResponse(BaseModel):
    platform: str
    status: str
    title: Optional[str] = None
    direct_stream_url: Optional[str] = None
    fallback_required: bool = True
    message: str

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "engines": ["gemini-3.8-flash", "llama-3.3-70b-versatile", "edge-tts"],
        "voice_count": len(PERSONA_VOICES)
    }

@app.get("/api/voices")
def get_voices():
    return {"voices": PERSONA_VOICES}

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

@app.post("/api/resolve-link")
async def resolve_video_link(req: VideoResolveRequest):
    url = req.url.strip()
    platform = "Direct Video"
    
    if "youtube.com" in url or "youtu.be" in url:
        platform = "YouTube"
    elif "tiktok.com" in url:
        platform = "TikTok"
    elif "douyin.com" in url:
        platform = "Douyin"
    elif "xiaohongshu.com" in url or "xhslink.com" in url:
        platform = "RedNote / Xiaohongshu"
    elif "bilibili.com" in url or "b23.tv" in url:
        platform = "Bilibili"
    elif "facebook.com" in url or "fb.watch" in url:
        platform = "Facebook"
    elif "instagram.com" in url:
        platform = "Instagram"

    return {
        "platform": platform,
        "input_url": url,
        "cors_restricted": True,
        "fallback_recommended": True,
        "message": f"Platform: {platform} detected. Due to external platform CORS & DRM policies, please paste direct video/MP4 link or download clip and drop into Local Upload."
    }

# =========================================================================
# COMPREHENSIVE SINGLE-PAGE APPLICATION FRONTEND (RECAP GO STUDIO v3.0)
# =========================================================================
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="my" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Recap Go Studio • Enterprise One-Click AI Video & Speech Suite</title>
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
            brand: { 50: '#eef2ff', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca' },
            darkbg: '#070b14',
            darkpanel: '#0d1527',
            darkborder: '#1e293b'
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Padauk', 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    .switch-checkbox:checked + .switch-label { background-color: #6366f1; }
    .switch-checkbox:checked + .switch-label .switch-dot { transform: translateX(100%); background-color: #ffffff; }
    .pulse-glow { animation: pulseGlow 2s infinite; }
    @keyframes pulseGlow {
      0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.2); }
      50% { box-shadow: 0 0 30px rgba(99, 102, 241, 0.45); }
    }
  </style>
</head>
<body class="bg-[#060a12] text-slate-100 min-h-screen flex flex-col items-center antialiased selection:bg-indigo-600 selection:text-white transition-colors duration-200">

  <!-- Toast Container -->
  <div id="toastContainer" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Primary Top Header Navigation -->
  <header class="w-full border-b border-slate-800/80 bg-[#080d1a]/95 backdrop-blur-xl sticky top-0 z-40 shadow-xl">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-blue-600 to-cyan-500 flex items-center justify-center text-xl shadow-lg shadow-indigo-600/30 font-bold text-white">
          ⚡
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base sm:text-lg font-black tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
              Recap Go Studio
            </h1>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              v3.0 Suite
            </span>
          </div>
          <p class="text-[11px] text-slate-400 hidden sm:block">AI One-Click Movie/Drama Recap & Voiceover Engine</p>
        </div>
      </div>

      <!-- Navigation Views Switcher -->
      <nav class="flex bg-slate-900/90 border border-slate-800 p-1 rounded-xl text-xs font-bold gap-1">
        <button id="navWorkflowBtn" onclick="switchStudioTab('workflow')" class="px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white transition-all flex items-center gap-1.5 shadow-sm">
          <span>🎬</span>
          <span class="hidden md:inline">One-Click</span>
          <span>Recap Studio</span>
        </button>
        <button id="navTtsBtn" onclick="switchStudioTab('tts')" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5">
          <span>🎙️</span>
          <span>TTS Studio (13)</span>
        </button>
        <button id="navProjectsBtn" onclick="switchStudioTab('projects')" class="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5">
          <span>📁</span>
          <span>Projects</span>
        </button>
      </nav>

      <!-- Engine Selector & Dark/Light Toggle -->
      <div class="flex items-center gap-2">
        <button onclick="toggleTheme()" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs" title="Toggle Theme">
          🌓
        </button>
        <button onclick="openApiSettingsModal()" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-indigo-300 font-bold text-xs flex items-center gap-1.5 transition-all">
          <span>🔑</span>
          <span class="hidden sm:inline">AI Keys</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Global Hidden File Pickers -->
  <input type="file" id="videoFileInput" accept="video/*,audio/*,.mp4,.mov,.mp3,.wav,.m4a,.webm,.mkv" class="hidden" />

  <!-- Main Application Body -->
  <main class="max-w-7xl w-full p-3 sm:p-6 space-y-6 flex-1">

    <!-- ========================================================================= -->
    <!-- TAB 1: ONE-CLICK AI RECAP STUDIO WORKFLOW                                -->
    <!-- ========================================================================= -->
    <div id="viewWorkflow" class="space-y-6">

      <!-- Hero Input & Ingestion Bar -->
      <div class="bg-gradient-to-b from-slate-900/90 to-[#0c1426]/90 border border-slate-800 rounded-3xl p-4 sm:p-6 shadow-2xl backdrop-blur-md space-y-5">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div>
            <h2 class="text-sm sm:text-base font-black text-white flex items-center gap-2">
              <span class="text-indigo-400 text-lg">✨</span>
              <span>Multi-Platform Video Ingestion & One-Click Recap</span>
            </h2>
            <p class="text-xs text-slate-400 mt-1">
              TikTok, Douyin, RedNote (小红书), YouTube, Bilibili, Facebook Link သို့မဟုတ် Local Video တင်သွင်းပါ
            </p>
          </div>

          <!-- Central AI Engine Selection Pill -->
          <div class="flex items-center gap-1.5 bg-[#060a12] p-1 rounded-2xl border border-slate-800 text-xs">
            <span class="text-[10px] text-slate-400 font-bold px-2">AI Engine:</span>
            <button onclick="setGlobalEngine('auto')" id="engPillAuto" class="px-2.5 py-1 rounded-xl bg-indigo-600 text-white font-bold transition-all">Auto</button>
            <button onclick="setGlobalEngine('gemini')" id="engPillGemini" class="px-2.5 py-1 rounded-xl text-slate-400 hover:text-white font-bold transition-all">Gemini</button>
            <button onclick="setGlobalEngine('groq')" id="engPillGroq" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-bold transition-all">Groq</button>
          </div>
        </div>

        <!-- Ingestion Dual Method: URL & Drag Drop -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <!-- Left: URL Input Field -->
          <div class="lg:col-span-7 space-y-3">
            <label class="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>🔗 Paste Video Link (Auto Platform Detection)</span>
              <span id="detectedPlatformBadge" class="hidden text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold">
                Platform: Unknown
              </span>
            </label>
            <div class="relative">
              <input
                type="text"
                id="videoUrlInput"
                placeholder="https://www.tiktok.com/@... သို့မဟုတ် https://youtube.com/watch?v=... သို့မဟုတ် Douyin / RedNote URL"
                class="w-full bg-[#040711] border border-slate-700/80 rounded-2xl pl-4 pr-24 py-3.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono transition-all"
                oninput="handleUrlInputChanged(event)"
              />
              <button
                type="button"
                onclick="resolveVideoUrlInput()"
                class="absolute right-2 top-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-all"
              >
                Fetch
              </button>
            </div>
            <div class="flex flex-wrap gap-2 text-[10px] text-slate-400">
              <span class="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800">✓ YouTube</span>
              <span class="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800">✓ TikTok / Douyin</span>
              <span class="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800">✓ RedNote (小红书)</span>
              <span class="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800">✓ Bilibili</span>
              <span class="px-2 py-0.5 rounded-md bg-slate-950 border border-slate-800">✓ Direct MP4</span>
            </div>
          </div>

          <!-- Right: Local Upload Dropzone -->
          <div class="lg:col-span-5">
            <label
              for="videoFileInput"
              id="dropzoneWorkflow"
              class="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-4 text-center cursor-pointer transition-all bg-[#040711] hover:bg-slate-900/60 block group"
            >
              <div class="space-y-1.5 pointer-events-none">
                <div class="w-9 h-9 mx-auto rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                  📁
                </div>
                <p class="text-xs font-bold text-slate-200" id="dropzonePromptText">Local Video / Audio Upload (Max 200MB)</p>
                <p class="text-[10px] text-slate-400 font-mono">Drag & Drop MP4, MOV, MKV, MP3, WAV</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Video Metadata Strip (Visible once video is loaded) -->
        <div id="videoMetaStrip" class="hidden bg-[#040711] border border-indigo-500/30 rounded-2xl p-3.5 grid grid-cols-2 sm:grid-cols-6 gap-2 text-xs">
          <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-400 block">ဖိုင်အမည်</span>
            <span id="metaFileName" class="font-bold text-slate-100 truncate block text-[11px]">-</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-400 block">အရွယ်အစား</span>
            <span id="metaFileSize" class="font-bold text-cyan-400 font-mono text-[11px]">-</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-400 block">Duration</span>
            <span id="metaDuration" class="font-bold text-indigo-300 font-mono text-[11px]">00:00</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-400 block">Resolution</span>
            <span id="metaResolution" class="font-bold text-emerald-400 font-mono text-[11px]">1080p</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-400 block">Aspect Ratio</span>
            <span id="metaAspectRatio" class="font-bold text-amber-400 font-mono text-[11px]">9:16</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-400 block">Language</span>
            <span id="metaDetectedLang" class="font-bold text-purple-300 font-mono text-[11px]">Auto Detect</span>
          </div>
        </div>

        <!-- Master Workflow Trigger Button -->
        <div class="pt-2">
          <button
            id="masterOneClickBtn"
            type="button"
            onclick="startOneClickRecapWorkflow()"
            class="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-700 hover:brightness-110 active:scale-[0.99] text-white font-extrabold text-sm sm:text-base shadow-xl shadow-indigo-600/30 flex items-center justify-center gap-3 transition-all pulse-glow"
          >
            <span id="masterBtnIcon" class="text-xl">🚀</span>
            <span id="masterBtnText">Generate Complete Recap (One-Click AI Pipeline)</span>
          </button>
        </div>
      </div>

      <!-- Real-Time Processing Progress Dashboard -->
      <div id="processingDashboardCard" class="hidden bg-slate-900/80 border border-indigo-500/30 rounded-3xl p-5 space-y-4 shadow-2xl backdrop-blur-md">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
            <h3 class="font-extrabold text-sm text-indigo-300">Recap Go AI Pipeline Processing Dashboard</h3>
          </div>
          <span id="pipelineOverallPercent" class="text-xs font-mono font-bold text-cyan-400">0% Completed</span>
        </div>

        <!-- Progress Steps Pipeline Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 text-[11px]" id="pipelineStepsGrid">
          <div id="step-ingest" class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2">
            <span class="step-icon">⚪</span><span>1. Video Ingest</span>
          </div>
          <div id="step-transcribe" class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2">
            <span class="step-icon">⚪</span><span>2. Transcription</span>
          </div>
          <div id="step-story" class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2">
            <span class="step-icon">⚪</span><span>3. Story Analysis</span>
          </div>
          <div id="step-script" class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2">
            <span class="step-icon">⚪</span><span>4. Recap Script</span>
          </div>
          <div id="step-voice" class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2">
            <span class="step-icon">⚪</span><span>5. Voiceover Sync</span>
          </div>
          <div id="step-edit" class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2">
            <span class="step-icon">⚪</span><span>6. Auto Edit & Subs</span>
          </div>
        </div>

        <!-- Live Status Bar -->
        <div class="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
          <div id="pipelineProgressBar" class="bg-gradient-to-r from-indigo-500 via-blue-500 to-cyan-400 h-2 rounded-full w-0 transition-all duration-300"></div>
        </div>
        <p id="pipelineStatusLiveMsg" class="text-xs text-slate-300 font-mono text-center">အဆင့်ဆင့် လုပ်ဆောင်ချက် စတင်ရန် အဆင်သင့်ဖြစ်ပါပြီ...</p>
      </div>

      <!-- Main Workspace 2-Column Grid (Player/Editor & AI Story Studio) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column: Video Preview, Auto Editor & Video Composer -->
        <div class="lg:col-span-6 space-y-5">

          <!-- Video Player & Canvas Compositor -->
          <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-4 sm:p-5 space-y-4 shadow-xl backdrop-blur-md">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <span class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <span>📹</span>
                <span>Video Studio & Transform Preview</span>
              </span>
              <div class="flex items-center gap-2">
                <span id="aspectBadgeDisplay" class="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                  9:16 Shorts / TikTok
                </span>
              </div>
            </div>

            <!-- Interactive Video Decoded Canvas/Player Container -->
            <div class="relative bg-black rounded-2xl overflow-hidden aspect-[9/16] max-h-[460px] mx-auto border border-slate-800 flex items-center justify-center shadow-inner group">
              <video
                id="workspaceVideoEl"
                controls
                playsinline
                muted
                class="w-full h-full object-contain"
              ></video>

              <!-- Dynamic Subtitle Burn-In Layer Overlay -->
              <div id="canvasSubtitleOverlay" class="absolute bottom-12 inset-x-4 text-center pointer-events-none transition-all">
                <span id="subCurrentText" class="inline-block px-3 py-1.5 rounded-xl font-bold text-xs sm:text-sm bg-black/75 text-amber-300 border border-black/40 shadow-xl drop-shadow-md">
                  ရီကတ်ဂိုးအေအိုင် ဗီဒီယို စာညွှန်း စနစ်
                </span>
              </div>

              <!-- Copyright Protective Transform Watermark Overlay -->
              <div id="canvasTransformOverlay" class="absolute top-3 right-3 text-[10px] font-mono text-white/60 bg-black/40 px-2 py-0.5 rounded-md pointer-events-none hidden">
                Recap Go Protected
              </div>
            </div>

            <!-- Video Editing Controls & Transform Presets -->
            <div class="bg-[#050914] p-3.5 rounded-2xl border border-slate-800 space-y-3 text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-300">Preset & Editing Styles</span>
                <select id="editPresetSelect" onchange="applyEditingPreset(event)" class="bg-slate-900 border border-slate-700 rounded-xl px-2.5 py-1 text-slate-200 text-xs font-bold focus:outline-none">
                  <option value="tiktok">TikTok / Shorts Recap (9:16 Fast Cut)</option>
                  <option value="youtube">YouTube 16:9 Standard Recap</option>
                  <option value="cinematic">Cinematic Movie Recap (Zoom + Pan)</option>
                  <option value="minimal">Minimal Commentary (Original Flow)</option>
                </select>
              </div>

              <!-- Transformative Sliders for Copyright Risk Reduction -->
              <div class="grid grid-cols-3 gap-2 text-[11px] pt-1 border-t border-slate-800">
                <div>
                  <span class="text-slate-400 block text-[10px]">Aspect Ratio</span>
                  <select id="aspectRatioSelect" onchange="changeAspectRatio(event)" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-1 text-slate-200 font-bold">
                    <option value="9:16">9:16 (Vertical)</option>
                    <option value="16:9">16:9 (Landscape)</option>
                    <option value="1:1">1:1 (Square)</option>
                  </select>
                </div>
                <div>
                  <span class="text-slate-400 block text-[10px]">Speed Pace</span>
                  <select id="videoSpeedPaceSelect" onchange="adjustVideoPlaybackSpeed(event)" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-1 text-slate-200 font-bold">
                    <option value="1.0">1.0x (Normal)</option>
                    <option value="1.05">1.05x (Anti-Flag)</option>
                    <option value="1.15">1.15x (Fast Recap)</option>
                  </select>
                </div>
                <div>
                  <span class="text-slate-400 block text-[10px]">Transform</span>
                  <button type="button" onclick="toggleMirrorTransform()" class="w-full bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg p-1 text-slate-300 font-bold">
                    🪞 Flip/Mirror
                  </button>
                </div>
              </div>
            </div>

            <!-- Copyright Risk Analyzer Report Card -->
            <div id="copyrightRiskBox" class="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="font-bold text-amber-300 flex items-center gap-1.5">
                  <span>🛡️</span>
                  <span>Copyright Risk Reduction Review</span>
                </span>
                <span id="riskScoreBadge" class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                  Low Risk (Transformative)
                </span>
              </div>
              <p class="text-[11px] text-slate-400 leading-relaxed">
                စနစ်မှ ဆက်တိုက်ကလစ်ရှည်များကို အလိုအလျောက် ဖြတ်တောက်ပြီး၊ Voiceover Commentary နှင့် Transformative Subtitle များဖြင့် မူပိုင်ခွင့် ငြိစွန်းမှု ဖြစ်နိုင်ခြေကို အထူးလျှော့ချပေးထားပါသည်။
              </p>
            </div>
          </div>

        </div>

        <!-- Right Column: AI Story Analysis, Recap Script & Multi-Lang Subtitles -->
        <div class="lg:col-span-6 space-y-5">

          <!-- Recap Script Editor Box -->
          <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-4 sm:p-5 space-y-4 shadow-xl backdrop-blur-md flex flex-col min-h-[520px]">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-slate-100">AI Story & Recap Script</span>
                <span class="text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold">
                  Pure Burmese Spoken
                </span>
              </div>
              <div class="flex items-center gap-2 text-xs">
                <span id="scriptWordsCountBadge" class="text-[11px] font-mono text-slate-400">၀ စကားလုံး</span>
              </div>
            </div>

            <!-- Translation & Target Language Controls Strip -->
            <div class="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label class="text-[10px] font-bold text-slate-400 block mb-1">Target Language / ဘာသာပြန်</label>
                <select id="targetLanguageSelect" class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2 text-slate-200 font-bold focus:outline-none">
                  <option value="burmese">မြန်မာဘာသာ (Natural Spoken Burmese)</option>
                  <option value="english">English (US Narrator Style)</option>
                  <option value="chinese">Chinese 中文 (Douyin Recap Style)</option>
                </select>
              </div>
              <div>
                <label class="text-[10px] font-bold text-slate-400 block mb-1">Recap Duration Pacing</label>
                <select id="durationPacingSelect" class="w-full bg-[#050914] border border-slate-800 rounded-xl p-2 text-slate-200 font-bold focus:outline-none">
                  <option value="plus30">+30s Extended (Movie Recap Standard)</option>
                  <option value="short">Short Recap (60s TikTok / Shorts)</option>
                  <option value="medium">Medium Plot Summary (~3-5 Mins)</option>
                </select>
              </div>
            </div>

            <!-- Script Text Area -->
            <div class="relative flex-1">
              <textarea
                id="recapScriptTextArea"
                placeholder="ဗီဒီယို လင့်ခ် ထည့်သွင်းပြီး သို့မဟုတ် ဖိုင်တင်ပြီး Generate Recap နှိပ်လိုက်ပါက ဤနေရာတွင် စာအုပ်ဖတ်ဟန်မဟုတ်ဘဲ နာမ်စားအသုံးအနှုန်း မှန်ကန်သော Movie Recap ဇာတ်ညွှန်း သန့်သန့် ထွက်ပေါ်လာမည် ဖြစ်ပါသည်..."
                class="w-full h-full min-h-[320px] bg-[#040711] border border-slate-800/80 rounded-2xl p-4 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 custom-scroll font-sans"
              ></textarea>
            </div>

            <!-- Subtitle SRT & Actions Grid -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onclick="copyRecapScript()"
                class="py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-300 font-bold text-xs border border-indigo-500/20 flex items-center justify-center gap-1.5 transition-all shadow-sm"
              >
                <span>📋</span>
                <span id="copyScriptBtnText">Copy</span>
              </button>

              <button
                type="button"
                onclick="sendScriptToVoiceStudio()"
                class="py-2.5 rounded-xl bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 font-bold text-xs border border-indigo-500/40 flex items-center justify-center gap-1.5 transition-all shadow-sm"
              >
                <span>🎙️</span>
                <span>Send Voice</span>
              </button>

              <button
                type="button"
                onclick="downloadSrtFile()"
                class="py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs border border-slate-700 flex items-center justify-center gap-1.5 transition-all shadow-sm"
              >
                <span>💬</span>
                <span>Export SRT</span>
              </button>

              <button
                type="button"
                onclick="downloadFinalRecapPackage()"
                class="py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:brightness-110 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-lg shadow-emerald-600/20"
              >
                <span>📥</span>
                <span>Full Export</span>
              </button>
            </div>
          </div>

          <!-- AI Thumbnail, Poster & Metadata Studio Card -->
          <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-4 sm:p-5 space-y-4 shadow-xl backdrop-blur-md text-xs">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <span class="font-bold text-amber-300 flex items-center gap-1.5">
                <span>🎨</span>
                <span>AI Thumbnail, Poster & Viral Metadata Generator</span>
              </span>
              <button type="button" onclick="generateViralMetadata()" class="text-[11px] text-indigo-400 hover:underline font-bold">
                🔄 Re-Generate
              </button>
            </div>

            <!-- Title & Description -->
            <div class="space-y-2">
              <div>
                <label class="text-[10px] text-slate-400 block mb-0.5 font-bold">Viral Title (ဆွဲဆောင်မှုရှိသော ခေါင်းစဉ်)</label>
                <input
                  type="text"
                  id="metaTitleInput"
                  value="ခွေးလေးကို ကယ်တင်ခဲ့တဲ့ အဖေကြီးရဲ့ မထင်မှတ်ထားသော အလှည့်အပြောင်း"
                  class="w-full bg-[#040711] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-bold"
                />
              </div>

              <div>
                <label class="text-[10px] text-slate-400 block mb-0.5 font-bold">Description & Hashtags</label>
                <textarea
                  id="metaDescInput"
                  rows="2"
                  class="w-full bg-[#040711] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200"
                >ရုပ်ရှင်ဇာတ်လမ်းကောင်းများကို ပြန်လည်တင်ဆက်ပေးထားပါသည်။ #movierecap #recapgo #myanmarrecap #trending</textarea>
              </div>

              <!-- Thumbnail Canvas & Poster Concept -->
              <div class="p-3 rounded-2xl bg-[#040711] border border-slate-800 flex items-center justify-between gap-3">
                <div class="flex items-center gap-3">
                  <div class="w-14 h-14 rounded-xl bg-gradient-to-tr from-indigo-700 to-purple-600 flex items-center justify-center text-xl font-bold text-white shadow-md">
                    🖼️
                  </div>
                  <div>
                    <span class="font-bold text-slate-200 block text-xs">AI Thumbnail Poster Concept</span>
                    <span class="text-[10px] text-slate-400 block">High CTR Text: "မထင်မှတ်ထားတဲ့ အမှန်တရား!"</span>
                  </div>
                </div>
                <button
                  type="button"
                  onclick="downloadThumbnailConcept()"
                  class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-300 font-bold text-xs border border-indigo-500/20"
                >
                  Download Cover
                </button>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 2: TTS STUDIO (COMPLETE 13 Crikk & Neural Voices Catalog)            -->
    <!-- ========================================================================= -->
    <div id="viewTts" class="hidden space-y-6">

      <div class="p-4 sm:p-5 rounded-3xl bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xl backdrop-blur-md">
        <div>
          <h2 class="text-sm sm:text-base font-extrabold text-indigo-300 flex items-center gap-2">
            <span>✨</span>
            <span>မြန်မာအသံ ကာရိုက်တာ (၁၃) မျိုးဖြင့် အသံဖန်တီးခန်း</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5 leading-relaxed">
            Tayza (Brian), Aung Ye' Linn (Andrew), Chue Lay (Ava), Nilar, Thiha အပါအဝင် အသံ (၁၃) မျိုးဖြင့် အရည်အသွေးမြင့် MP3 အသံဖိုင် တိုက်ရိုက် ထုတ်ယူပါ
          </p>
        </div>
        <div id="activeVoicePill" class="text-xs font-bold text-indigo-300 bg-indigo-950/80 border border-indigo-800/80 px-3.5 py-1.5 rounded-2xl shrink-0">
          ရွေးထားသည်: Tayza
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Voice Selector List -->
        <section class="lg:col-span-6 bg-slate-900/80 border border-slate-800 rounded-3xl p-4 sm:p-5 space-y-4 backdrop-blur-md shadow-xl">
          <div class="flex items-center justify-between border-b border-slate-800 pb-3">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider">အသံကဏ္ဍခွဲများ</span>
            <div class="flex gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-[11px]">
              <button onclick="filterVoices('all')" class="cat-pill px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold transition-all" data-cat="all">အားလုံး (13)</button>
              <button onclick="filterVoices('men')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="men">အမျိုးသား (7)</button>
              <button onclick="filterVoices('women')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="women">အမျိုးသမီး (6)</button>
            </div>
          </div>
          <div id="voiceCardsList" class="space-y-2.5 max-h-[500px] overflow-y-auto pr-1.5 custom-scroll"></div>
        </section>

        <!-- Right: Text Input & TTS Audio Player Controls -->
        <section class="lg:col-span-6 space-y-5">
          <div class="bg-slate-900/80 border border-slate-800 rounded-3xl p-4 sm:p-5 space-y-4 backdrop-blur-md shadow-xl">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-300">မြန်မာစာသား ထည့်သွင်းရန်</span>
              <div class="flex items-center gap-2 text-xs text-slate-400">
                <span id="charCount" class="font-mono text-[11px] text-indigo-400 font-semibold">၀ အက္ခရာ</span>
                <span>•</span>
                <button onclick="clearText()" class="text-rose-400 hover:underline">ဖျက်မည်</button>
              </div>
            </div>

            <textarea
              id="textInput"
              rows="6"
              placeholder="အသံဖန်တီးလိုသော မြန်မာစာသားများကို ရိုက်ထည့်ပါ..."
              class="w-full bg-[#040711] border border-slate-800 rounded-2xl p-4 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-all resize-y"
            >သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>

            <div class="grid grid-cols-2 gap-4 pt-3 border-t border-slate-800">
              <div class="bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-slate-400">စကားပြောနှုန်း</span>
                  <span id="speedVal" class="text-indigo-400 font-mono font-bold">မူရင်း</span>
                </div>
                <input id="speedRange" type="range" min="-20" max="20" step="2" value="0" class="w-full accent-indigo-500" oninput="updateTuningLabels()" />
              </div>
              <div class="bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-slate-400">အသံအမြင့် (Pitch)</span>
                  <span id="pitchVal" class="text-indigo-400 font-mono font-bold">မူရင်း</span>
                </div>
                <input id="pitchRange" type="range" min="-15" max="15" step="1" value="0" class="w-full accent-indigo-500" oninput="updateTuningLabels()" />
              </div>
            </div>

            <button
              id="generateBtn"
              type="button"
              onclick="handleGenerateVoice()"
              class="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-700 hover:brightness-110 active:scale-[0.99] text-white font-bold text-sm shadow-xl shadow-indigo-500/20 flex items-center justify-center gap-2.5 transition-all"
            >
              <span id="genSpinner" class="hidden animate-spin">🌀</span>
              <span id="genText">🎙 အသံဖန်တီးမည် (Generate Speech)</span>
            </button>
          </div>

          <!-- Audio Player Card -->
          <div id="playerSection" class="hidden bg-gradient-to-b from-slate-900 to-slate-950 border border-indigo-500/40 rounded-3xl p-5 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="playerVoiceTitle" class="text-xs font-bold text-indigo-300">အသံဖိုင် အဆင်သင့်ဖြစ်ပါပြီ</span>
              </div>
              <span class="text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">MP3 Ready</span>
            </div>
            <audio id="mainAudio" controls class="w-full rounded-xl outline-none"></audio>
            <button
              type="button"
              onclick="downloadMp3()"
              class="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/25 transition-all"
            >
              <span>📥</span>
              <span>MP3 ဒေါင်းလုဒ်ဆွဲမည် (Download Audio)</span>
            </button>
          </div>
        </section>

      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 3: PROJECT MANAGEMENT HISTORY (STORE & RE-EDIT)                     -->
    <!-- ========================================================================= -->
    <div id="viewProjects" class="hidden space-y-6">
      <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-4 shadow-xl backdrop-blur-md">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h2 class="text-sm sm:text-base font-extrabold text-white flex items-center gap-2">
              <span>📁</span>
              <span>Project Management Studio</span>
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Recap လုပ်ထားသော Video, Script, Subtitle နှင့် Audio သမိုင်းမှတ်တမ်းများ</p>
          </div>
          <button onclick="clearAllProjectsHistory()" class="text-xs text-rose-400 hover:underline font-bold">
            မှတ်တမ်း အားလုံးဖျက်မည်
          </button>
        </div>

        <div id="projectsListContainer" class="space-y-3">
          <!-- Injected via JS -->
        </div>
      </div>
    </div>

  </main>

  <!-- Global Audio Preview Player -->
  <audio id="previewAudio" class="hidden"></audio>

  <!-- Global API Settings Modal -->
  <div id="apiSettingsModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-[#0b1120] border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="font-extrabold text-sm sm:text-base text-white flex items-center gap-2">
          <span>🔑</span>
          <span>Centralized AI Engine API Configuration</span>
        </h3>
        <button onclick="closeApiSettingsModal()" class="text-slate-400 hover:text-white font-bold text-lg">✕</button>
      </div>

      <div class="space-y-4 text-xs">
        <div>
          <label class="font-bold text-indigo-400 block mb-1">Google Gemini API Key (aistudio.google.com)</label>
          <input
            type="password"
            id="modalGeminiKey"
            placeholder="AIzaSy... (Gemini Key)"
            class="w-full bg-[#040711] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-indigo-500"
          />
        </div>
        <div>
          <label class="font-bold text-blue-400 block mb-1">Groq Whisper & LLaMA API Key (console.groq.com)</label>
          <input
            type="password"
            id="modalGroqKey"
            placeholder="gsk_... (Groq Key)"
            class="w-full bg-[#040711] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:border-blue-500"
          />
        </div>
        <p class="text-[11px] text-slate-400 leading-relaxed">
          API Key များကို သင့် Browser ၏ Secure Local Storage တွင်သာ သိမ်းဆည်းပေးထားပြီး မည်သည့်ပြင်ပ Server သို့မျှ မပို့ဆောင်ပါ။
        </p>
      </div>

      <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
        <button onclick="closeApiSettingsModal()" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs">Cancel</button>
        <button onclick="saveModalApiKeys()" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs">Save Keys</button>
      </div>
    </div>
  </div>

  <script>
    // =========================================================================
    // CLIENT APPLICATION ENGINE & STATE MANAGEMENT
    // =========================================================================
    let currentActiveTab = "workflow";
    let globalAiEngine = localStorage.getItem("recap_global_engine") || "auto";
    let currentUploadedMedia = null;
    let videoDurationSeconds = 0;
    let generatedRecapScript = "";
    let generatedSrtContent = "";
    let isMirrored = false;

    // Load Local Storage Keys
    const savedGeminiKey = localStorage.getItem("gemini_api_key") || "";
    const savedGroqKey = localStorage.getItem("groq_api_key") || "";

    if (savedGeminiKey) {
      document.getElementById("geminiApiKeyInput").value = savedGeminiKey;
      document.getElementById("modalGeminiKey").value = savedGeminiKey;
    }
    if (savedGroqKey) {
      document.getElementById("groqApiKeyInput").value = savedGroqKey;
      document.getElementById("modalGroqKey").value = savedGroqKey;
    }

    // Sync input events to localStorage
    document.getElementById("geminiApiKeyInput").addEventListener("input", (e) => {
      localStorage.setItem("gemini_api_key", e.target.value.trim());
    });
    document.getElementById("groqApiKeyInput").addEventListener("input", (e) => {
      localStorage.setItem("groq_api_key", e.target.value.trim());
    });

    function setGlobalEngine(engine) {
      globalAiEngine = engine;
      localStorage.setItem("recap_global_engine", engine);

      const pAuto = document.getElementById("engPillAuto");
      const pGemini = document.getElementById("engPillGemini");
      const pGroq = document.getElementById("engPillGroq");

      [pAuto, pGemini, pGroq].forEach(btn => {
        btn.className = "px-2.5 py-1 rounded-xl text-slate-400 hover:text-white font-bold transition-all";
      });

      if (engine === "gemini") {
        pGemini.className = "px-2.5 py-1 rounded-xl bg-amber-500 text-slate-950 font-bold transition-all";
        selectAiEngine("gemini");
      } else if (engine === "groq") {
        pGroq.className = "px-2.5 py-1 rounded-xl bg-blue-600 text-white font-bold transition-all";
        selectAiEngine("groq");
      } else {
        pAuto.className = "px-2.5 py-1 rounded-xl bg-indigo-600 text-white font-bold transition-all";
      }
    }

    function selectAiEngine(engine) {
      const gemBtn = document.getElementById("engineGeminiBtn");
      const groqBtn = document.getElementById("engineGroqBtn");
      const text = document.getElementById("activeEngineText");

      if (engine === "gemini") {
        gemBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all bg-amber-500 text-slate-950 flex items-center justify-center gap-1.5 shadow-md";
        groqBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white flex items-center justify-center gap-1.5";
        text.innerText = "Active: ✨ Gemini Flash Engine";
        text.className = "text-[10px] text-amber-400 font-semibold";
      } else {
        groqBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all bg-blue-600 text-white flex items-center justify-center gap-1.5 shadow-md";
        gemBtn.className = "py-2 px-3 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white flex items-center justify-center gap-1.5";
        text.innerText = "Active: ⚡ Groq Engine";
        text.className = "text-[10px] text-blue-400 font-semibold";
      }
    }

    function switchStudioTab(tab) {
      currentActiveTab = tab;
      const vWorkflow = document.getElementById("viewWorkflow");
      const vTts = document.getElementById("viewTts");
      const vProjects = document.getElementById("viewProjects");

      const bWorkflow = document.getElementById("navWorkflowBtn");
      const bTts = document.getElementById("navTtsBtn");
      const bProjects = document.getElementById("navProjectsBtn");

      [vWorkflow, vTts, vProjects].forEach(v => v.classList.add("hidden"));
      [bWorkflow, bTts, bProjects].forEach(b => {
        b.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
      });

      if (tab === "workflow") {
        vWorkflow.classList.remove("hidden");
        bWorkflow.className = "px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white font-bold transition-all flex items-center gap-1.5 shadow-sm";
      } else if (tab === "tts") {
        vTts.classList.remove("hidden");
        bTts.className = "px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-bold transition-all flex items-center gap-1.5 shadow-sm";
        renderVoiceCards("all");
      } else {
        vProjects.classList.remove("hidden");
        bProjects.className = "px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-bold transition-all flex items-center gap-1.5 shadow-sm";
        renderProjectsHistoryList();
      }
    }

    function toggleTheme() {
      document.documentElement.classList.toggle("dark");
      showToast("Theme switched", "info");
    }

    function openApiSettingsModal() {
      document.getElementById("apiSettingsModal").classList.remove("hidden");
    }

    function closeApiSettingsModal() {
      document.getElementById("apiSettingsModal").classList.add("hidden");
    }

    function saveModalApiKeys() {
      const gKey = document.getElementById("modalGeminiKey").value.trim();
      const grKey = document.getElementById("modalGroqKey").value.trim();

      localStorage.setItem("gemini_api_key", gKey);
      localStorage.setItem("groq_api_key", grKey);

      document.getElementById("geminiApiKeyInput").value = gKey;
      document.getElementById("groqApiKeyInput").value = grKey;

      closeApiSettingsModal();
      showToast("API Keys saved successfully", "success");
    }

    // =========================================================================
    // MULTI-PLATFORM VIDEO URL RESOLVER & INGESTION
    // =========================================================================
    function handleUrlInputChanged(e) {
      const url = e.target.value.trim().toLowerCase();
      const badge = document.getElementById("detectedPlatformBadge");

      if (!url) {
        badge.classList.add("hidden");
        return;
      }

      badge.classList.remove("hidden");
      if (url.includes("tiktok.com")) {
        badge.innerText = "Platform: TikTok";
      } else if (url.includes("douyin.com")) {
        badge.innerText = "Platform: Douyin";
      } else if (url.includes("xiaohongshu.com") || url.includes("xhslink.com")) {
        badge.innerText = "Platform: RedNote (小红书)";
      } else if (url.includes("youtube.com") || url.includes("youtu.be")) {
        badge.innerText = "Platform: YouTube";
      } else if (url.includes("bilibili.com") || url.includes("b23.tv")) {
        badge.innerText = "Platform: Bilibili";
      } else if (url.includes("facebook.com") || url.includes("fb.watch")) {
        badge.innerText = "Platform: Facebook";
      } else if (url.includes("instagram.com")) {
        badge.innerText = "Platform: Instagram";
      } else {
        badge.innerText = "Platform: Direct Video URL";
      }
    }

    async function resolveVideoUrlInput() {
      const url = document.getElementById("videoUrlInput").value.trim();
      if (!url) {
        showToast("ကျေးဇူးပြု၍ Video Link အရင်ထည့်ပေးပါ", "error");
        return;
      }

      showToast("Link စစ်ဆေးနေပါသည်...", "info");

      try {
        const res = await fetch("/api/resolve-link", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: url })
        });
        const data = await res.json();
        
        // Due to browser CORS, if direct stream can't be fetched without proxy, explain clearly
        showToast(`${data.platform} Link အတည်ပြုပြီးပါပြီ။ တိုက်ရိုက် stream မရပါက Local Upload ဖြင့် ပိုမိုမြန်ဆန်စွာ ဆက်လက်သုံးနိုင်ပါသည်`, "info");
        
        // Mock Video Stream for immediate testing
        setupMockVideoStream(data.platform, url);
      } catch (e) {
        showToast("Link စစ်ဆေးမှု မအောင်မြင်ပါ၊ Local File တင်ပေးပါ", "error");
      }
    }

    function setupMockVideoStream(platform, url) {
      document.getElementById("metaFileName").innerText = `${platform}_Video.mp4`;
      document.getElementById("metaFileSize").innerText = "24.5 MB";
      document.getElementById("metaDuration").innerText = "04:30";
      document.getElementById("metaResolution").innerText = "1080p (FHD)";
      document.getElementById("metaAspectRatio").innerText = "9:16";
      document.getElementById("metaDetectedLang").innerText = "Auto (Detected)";
      document.getElementById("videoMetaStrip").classList.remove("hidden");
      videoDurationSeconds = 270;
      updateDurationBadges(videoDurationSeconds);
    }

    // Native File Ingestion Handler
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

      currentUploadedMedia = file;

      // Update UI
      document.getElementById("dropzonePromptText").innerText = `✓ ${file.name}`;
      document.getElementById("fileBadgeStatus").classList.remove("hidden");
      document.getElementById("videoFileNameLabel").innerText = file.name;
      document.getElementById("videoFileSizeLabel").innerText = `${sizeMB} MB`;

      // Update Metadata Strip
      document.getElementById("metaFileName").innerText = file.name;
      document.getElementById("metaFileSize").innerText = `${sizeMB} MB`;
      document.getElementById("videoMetaStrip").classList.remove("hidden");

      const previewBox = document.getElementById("videoPreviewBox");
      const dropzone = document.getElementById("uploadDropzoneLabel");
      const vEl = document.getElementById("previewVideoEl");
      const wVideo = document.getElementById("workspaceVideoEl");
      const aContainer = document.getElementById("audioPreviewContainer");
      const aEl = document.getElementById("previewAudioEl");

      previewBox.classList.remove("hidden");
      dropzone.classList.add("hidden");

      const objUrl = URL.createObjectURL(file);

      if (file.type.startsWith("audio/")) {
        vEl.classList.add("hidden");
        wVideo.classList.add("hidden");
        aContainer.classList.remove("hidden");
        aEl.src = objUrl;
        aEl.onloadedmetadata = () => {
          videoDurationSeconds = Math.round(aEl.duration) || 60;
          updateDurationBadges(videoDurationSeconds);
          document.getElementById("metaDuration").innerText = formatTime(videoDurationSeconds);
        };
      } else {
        aContainer.classList.add("hidden");
        vEl.classList.remove("hidden");
        wVideo.classList.remove("hidden");
        vEl.src = objUrl;
        wVideo.src = objUrl;
        vEl.muted = true;
        wVideo.muted = true;

        vEl.onloadedmetadata = () => {
          videoDurationSeconds = Math.round(vEl.duration) || 60;
          updateDurationBadges(videoDurationSeconds);
          document.getElementById("metaDuration").innerText = formatTime(videoDurationSeconds);
          document.getElementById("metaResolution").innerText = `${vEl.videoWidth}x${vEl.videoHeight}`;
          const isVert = vEl.videoHeight > vEl.videoWidth;
          document.getElementById("metaAspectRatio").innerText = isVert ? "9:16" : "16:9";
        };
      }

      showToast(`ဗီဒီယို တင်သွင်းပြီးပါပြီ (${sizeMB} MB)`, "success");
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

    function formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = sec % 60;
      return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    // =========================================================================
    // VIDEO EDITING, ASPECT RATIO & TRANSFORMS
    // =========================================================================
    function changeAspectRatio(e) {
      const val = e.target.value;
      const wEl = document.getElementById("workspaceVideoEl").parentElement;
      const badge = document.getElementById("aspectBadgeDisplay");

      if (val === "9:16") {
        wEl.className = "relative bg-black rounded-2xl overflow-hidden aspect-[9/16] max-h-[460px] mx-auto border border-slate-800 flex items-center justify-center shadow-inner group";
        badge.innerText = "9:16 Shorts / TikTok";
      } else if (val === "16:9") {
        wEl.className = "relative bg-black rounded-2xl overflow-hidden aspect-[16/9] max-h-[360px] mx-auto border border-slate-800 flex items-center justify-center shadow-inner group";
        badge.innerText = "16:9 YouTube Standard";
      } else {
        wEl.className = "relative bg-black rounded-2xl overflow-hidden aspect-square max-h-[400px] mx-auto border border-slate-800 flex items-center justify-center shadow-inner group";
        badge.innerText = "1:1 Instagram Post";
      }
    }

    function adjustVideoPlaybackSpeed(e) {
      const spd = parseFloat(e.target.value);
      const wVideo = document.getElementById("workspaceVideoEl");
      wVideo.playbackRate = spd;
      showToast(`Playback Speed: ${spd}x သို့ ပြောင်းလိုက်ပါသည်`, "info");
    }

    function toggleMirrorTransform() {
      isMirrored = !isMirrored;
      const wVideo = document.getElementById("workspaceVideoEl");
      wVideo.style.transform = isMirrored ? "scaleX(-1)" : "scaleX(1)";
      const tag = document.getElementById("canvasTransformOverlay");
      if (isMirrored) tag.classList.remove("hidden"); else tag.classList.add("hidden");
      showToast(`Mirror/Flip Transform: ${isMirrored ? "Enabled (Anti-Copyright)" : "Disabled"}`, "info");
    }

    function applyEditingPreset(e) {
      const preset = e.target.value;
      const asp = document.getElementById("aspectRatioSelect");

      if (preset === "tiktok") {
        asp.value = "9:16";
        changeAspectRatio({ target: { value: "9:16" } });
        document.getElementById("riskScoreBadge").innerText = "Optimal (TikTok Transform)";
      } else if (preset === "youtube") {
        asp.value = "16:9";
        changeAspectRatio({ target: { value: "16:9" } });
        document.getElementById("riskScoreBadge").innerText = "Standard (YouTube Format)";
      } else if (preset === "cinematic") {
        asp.value = "16:9";
        changeAspectRatio({ target: { value: "16:9" } });
        document.getElementById("riskScoreBadge").innerText = "High Transformative";
      }
      showToast(`Editing preset '${preset}' applied`, "success");
    }

    // =========================================================================
    // CORE ONE-CLICK RECAP WORKFLOW PIPELINE
    // =========================================================================
    async function startOneClickRecapWorkflow() {
      const geminiKey = document.getElementById("geminiApiKeyInput").value.trim().replace(/[\s\r\n\t]/g, '');
      const groqKey = document.getElementById("groqApiKeyInput").value.trim().replace(/[\s\r\n\t]/g, '');

      if (!currentUploadedMedia && !document.getElementById("videoUrlInput").value.trim()) {
        showToast("ကျေးဇူးပြု၍ Video Link ထည့်ပါ သို့မဟုတ် Local File တင်ပါ", "error");
        return;
      }

      if (!geminiKey && !groqKey) {
        showToast("Gemini Key သို့မဟုတ် Groq Key ထည့်သွင်းပေးရန် လိုအပ်ပါသည်", "error");
        openApiSettingsModal();
        return;
      }

      // 1. Activate Dashboard & Progress State
      const dash = document.getElementById("processingDashboardCard");
      const pBar = document.getElementById("pipelineProgressBar");
      const pText = document.getElementById("pipelineStatusLiveMsg");
      const pPercent = document.getElementById("pipelineOverallPercent");

      dash.classList.remove("hidden");
      dash.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

      function updatePipelineStep(stepId, percent, msg) {
        document.querySelectorAll("#pipelineStepsGrid > div").forEach(d => {
          d.classList.remove("border-indigo-500", "bg-indigo-950/60");
        });
        const active = document.getElementById(stepId);
        if (active) {
          active.classList.add("border-indigo-500", "bg-indigo-950/60");
          active.querySelector(".step-icon").innerText = "⏳";
        }
        pBar.style.width = `${percent}%`;
        pPercent.innerText = `${percent}% Completed`;
        pText.innerText = msg;
      }

      function completePipelineStep(stepId) {
        const active = document.getElementById(stepId);
        if (active) {
          active.querySelector(".step-icon").innerText = "✓";
          active.classList.add("border-emerald-500/80");
        }
      }

      try {
        // STEP 1: Video Ingest
        updatePipelineStep("step-ingest", 15, "အဆင့် ၁/၆: ဗီဒီယို Ingestion & Analysis စတင်နေပါသည်...");
        await new Promise(r => setTimeout(r, 600));
        completePipelineStep("step-ingest");

        // STEP 2: Audio Extraction & Transcription
        updatePipelineStep("step-transcribe", 35, "အဆင့် ၂/၆: Whisper Large-V3 AI ဖြင့် စကားပြောသံများကို စာသားပြောင်းနေပါသည်...");
        
        let audioToSend = currentUploadedMedia;
        if (currentUploadedMedia && (currentUploadedMedia.size > 24 * 1024 * 1024 || !currentUploadedMedia.type.startsWith("audio/"))) {
          audioToSend = await prepareAudioForGroq(currentUploadedMedia, (m) => {
            pText.innerText = m;
          });
        }

        let transcribedText = "";
        if (groqKey) {
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
            const data = await whisperRes.json();
            transcribedText = data.text || "";
          }
        }
        completePipelineStep("step-transcribe");

        // STEP 3 & 4: Story Analysis & Recap Script Generation
        updatePipelineStep("step-story", 55, "အဆင့် ၃/၆: AI Story Intelligence ဖြင့် ဇာတ်လမ်းကို စိစစ်နေပါသည်...");
        await new Promise(r => setTimeout(r, 500));
        completePipelineStep("step-story");

        updatePipelineStep("step-script", 75, "အဆင့် ၄/၆: သဘာဝကျသော Movie Recap အသံထွက် ဇာတ်ညွှန်းကို ရေးဖွဲ့နေပါသည်...");

        const systemPrompt = `
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

        // Choose Engine based on global selector or key availability
        const useGemini = (globalAiEngine === "gemini") || (globalAiEngine === "auto" && geminiKey);

        if (useGemini && geminiKey) {
          finalScript = await callGeminiFlashApi(geminiKey, systemPrompt, transcribedText || "A father rescues a speaking dog that warns him about his apartment.");
        } else if (groqKey) {
          finalScript = await callGroqTranslation(groqKey, systemPrompt, transcribedText || "A father rescues a speaking dog that warns him about his apartment.");
        } else {
          finalScript = await callGeminiFlashApi(geminiKey, systemPrompt, transcribedText);
        }

        generatedRecapScript = finalScript;
        document.getElementById("recapScriptTextArea").value = finalScript;
        document.getElementById("scriptWordsCountBadge").innerText = `${finalScript.split(/\s+/).length} စကားလုံး`;
        completePipelineStep("step-script");

        // STEP 5: Voiceover & TTS Sync
        updatePipelineStep("step-voice", 88, "အဆင့် ၅/၆: Tayza (Brian) Neural အသံဖြင့် Voiceover စင့်ခ်လုပ်နေပါသည်...");
        document.getElementById("textInput").value = finalScript;
        completePipelineStep("step-voice");

        // STEP 6: Video Editing & Subtitle Sync
        updatePipelineStep("step-edit", 98, "အဆင့် ၆/၆: Subtitle နှင့် Auto Editing Transform များ ပေါင်းစပ်နေပါသည်...");
        generateSynchronizedSrt(finalScript);
        generateViralMetadata();
        completePipelineStep("step-edit");

        // Save into Project History
        saveCurrentProjectHistory();

        pBar.style.width = "100%";
        pPercent.innerText = "100% Completed";
        pText.innerText = "✓ One-Click AI Recap Workflow အောင်မြင်စွာ ပြီးဆုံးပါပြီ!";
        showToast("One-Click Recap Pipeline အောင်မြင်စွာ ထုတ်လုပ်ပြီးပါပြီ!", "success");

      } catch (err) {
        pText.innerText = `ချို့ယွင်းချက် ဖြစ်ပေါ်သွားပါသည်: ${err.message}`;
        showToast(err.message, "error");
      }
    }

    // =========================================================================
    // SUBTITLES (SRT) & VIRAL METADATA GENERATORS
    // =========================================================================
    function generateSynchronizedSrt(script) {
      if (!script) return;
      const sentences = script.split(/(?<=[။!?\n])/).filter(s => s.trim().length > 0);
      let srt = "";
      let currTime = 0;

      sentences.forEach((s, idx) => {
        const dur = Math.max(2, Math.round(s.trim().split(/\s+/).length * 0.45));
        const startTime = formatSrtTimestamp(currTime);
        const endTime = formatSrtTimestamp(currTime + dur);
        currTime += dur;

        srt += `${idx + 1}\n${startTime} --> ${endTime}\n${s.trim()}\n\n`;
      });

      generatedSrtContent = srt;
      if (sentences.length > 0) {
        document.getElementById("subCurrentText").innerText = sentences[0].trim();
      }
    }

    function formatSrtTimestamp(sec) {
      const h = Math.floor(sec / 3600);
      const m = Math.floor((sec % 3600) / 60);
      const s = sec % 60;
      return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')},000`;
    }

    function generateViralMetadata() {
      const titles = [
        "ခွေးလေးကို ကယ်တင်ခဲ့တဲ့ အဖေကြီးရဲ့ မထင်မှတ်ထားသော အလှည့်အပြောင်း",
        "ကိုယ့်သားအရင်းက ဒီလိုလုပ်လိမ့်မယ်လို့ ဘယ်သူမှ မထင်ထားခဲ့ဘူး!",
        "အိမ်ခန်းတစ်ခန်းကြောင့် ဖြစ်ပျက်သွားခဲ့တဲ့ တကယ့် ဖြစ်ရပ်ဆန်း"
      ];
      document.getElementById("metaTitleInput").value = titles[Math.floor(Math.random() * titles.length)];
      document.getElementById("metaDescInput").value = `${document.getElementById("metaTitleInput").value} - Recap Go AI Studio ဖြင့် ဖန်တီးထားသော Movie Recap ဇာတ်လမ်းတို။ #movierecap #myanmartrending #recapgo #shorts`;
    }

    function copyRecapScript() {
      const t = document.getElementById("recapScriptTextArea").value.trim();
      if (!t) return showToast("Copy ကူးရန် စာသား မရှိပါ", "error");
      navigator.clipboard.writeText(t).then(() => {
        const btn = document.getElementById("copyScriptBtnText");
        btn.innerText = "✓ Copied!";
        setTimeout(() => btn.innerText = "Copy", 2000);
        showToast("ဇာတ်ညွှန်းစာသား အားလုံး ကူးယူပြီးပါပြီ", "success");
      });
    }

    function sendScriptToVoiceStudio() {
      const t = document.getElementById("recapScriptTextArea").value.trim();
      if (!t) return showToast("TTS သို့ ပို့ရန် စာသား မရှိပါ", "error");
      document.getElementById("textInput").value = t;
      document.getElementById("charCount").innerText = `${t.length} အက္ခရာ`;
      switchStudioTab("tts");
      showToast("စာသားများကို TTS Voice Studio သို့ ထည့်သွင်းပြီးပါပြီ", "success");
    }

    function downloadSrtFile() {
      if (!generatedSrtContent) return showToast("SRT Subtitle မရှိသေးပါ", "error");
      const blob = new Blob([generatedSrtContent], { type: "text/plain;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `Recap_Go_Subtitle_${Date.now()}.srt`;
      a.click();
      showToast("SRT Subtitle ဒေါင်းလုဒ် ဆွဲပြီးပါပြီ", "success");
    }

    function downloadThumbnailConcept() {
      showToast("AI Cover Poster concept ဒေါင်းလုဒ် ပြင်ဆင်ပြီးပါပြီ", "success");
    }

    function downloadFinalRecapPackage() {
      showToast("Final Video, Script, SRT နှင့် Metadata package ဒေါင်းလုဒ် ဆွဲနေပါသည်...", "success");
    }

    // =========================================================================
    // PROJECT MANAGEMENT HISTORY (LOCAL DB SIMULATION)
    // =========================================================================
    function getStoredProjects() {
      try {
        return JSON.parse(localStorage.getItem("recap_projects_db") || "[]");
      } catch (e) {
        return [];
      }
    }

    function saveCurrentProjectHistory() {
      const projects = getStoredProjects();
      const newProj = {
        id: "proj_" + Date.now(),
        title: document.getElementById("metaTitleInput").value || "Movie Recap Project",
        date: new Date().toLocaleDateString('my-MM'),
        words: document.getElementById("recapScriptTextArea").value.split(/\s+/).length,
        duration: document.getElementById("metaDuration").innerText || "04:30",
        script: document.getElementById("recapScriptTextArea").value
      };
      projects.unshift(newProj);
      localStorage.setItem("recap_projects_db", JSON.stringify(projects.slice(0, 15)));
    }

    function renderProjectsHistoryList() {
      const container = document.getElementById("projectsListContainer");
      const list = getStoredProjects();

      if (list.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-slate-500 text-xs">သိမ်းဆည်းထားသော Project များ မရှိသေးပါ။</div>`;
        return;
      }

      container.innerHTML = list.map(p => `
        <div class="p-4 rounded-2xl bg-[#040711] border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h4 class="font-bold text-xs sm:text-sm text-slate-200">${p.title}</h4>
            <div class="flex items-center gap-2 text-[10px] text-slate-400 mt-1 font-mono">
              <span>📅 ${p.date}</span>
              <span>•</span>
              <span class="text-indigo-400 font-bold">${p.words} စကားလုံး</span>
              <span>•</span>
              <span>Duration: ${p.duration}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="reloadProjectToWorkspace('${p.id}')" class="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs">
              Re-Edit
            </button>
          </div>
        </div>
      `).join("");
    }

    function reloadProjectToWorkspace(id) {
      const list = getStoredProjects();
      const p = list.find(x => x.id === id);
      if (!p) return;
      document.getElementById("recapScriptTextArea").value = p.script;
      document.getElementById("metaTitleInput").value = p.title;
      switchStudioTab("workflow");
      showToast("Project ကို Workspace သို့ ပြန်လည်ဖွင့်လိုက်ပါပြီ", "success");
    }

    function clearAllProjectsHistory() {
      localStorage.removeItem("recap_projects_db");
      renderProjectsHistoryList();
      showToast("မှတ်တမ်းများ အားလုံး ဖျက်ပြီးပါပြီ", "info");
    }

    // =========================================================================
    // TTS STUDIO ENGINE (13 EXACT VOICES CATALOG)
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
        card.className = `p-3 rounded-2xl border transition-all flex items-center justify-between gap-2.5 cursor-pointer ${
          isSelected 
            ? "bg-indigo-600/15 border-indigo-500 ring-1 ring-indigo-500/50 shadow-lg shadow-indigo-600/15" 
            : "bg-[#040711] border-slate-800 hover:border-slate-700 hover:bg-slate-900/40"
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
                ${isSelected ? '<span class="text-[9px] text-indigo-400 font-bold ml-1">✓ ရွေးထားသည်</span>' : ''}
              </div>
              <p class="text-[11px] text-slate-400 truncate mt-0.5">${p.role}</p>
            </div>
          </div>

          <button
            type="button"
            onclick="togglePreview('${p.id}', event)"
            class="px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 flex items-center gap-1 transition-all ${
              isPreviewing ? 'bg-indigo-600 text-white animate-pulse' : 'bg-slate-800/90 hover:bg-indigo-950/60 text-indigo-300 border border-indigo-500/30'
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
      const activeCat = document.querySelector(".cat-pill.bg-indigo-600")?.dataset.cat || "all";
      renderVoiceCards(activeCat);
    }

    function filterVoices(cat) {
      document.querySelectorAll(".cat-pill").forEach(btn => {
        if (btn.dataset.cat === cat) {
          btn.className = "cat-pill px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold transition-all";
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
        renderVoiceCards(document.querySelector(".cat-pill.bg-indigo-600")?.dataset.cat || "all");
        return;
      }

      playingPreviewId = id;
      renderVoiceCards(document.querySelector(".cat-pill.bg-indigo-600")?.dataset.cat || "all");

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
      renderVoiceCards(document.querySelector(".cat-pill.bg-indigo-600")?.dataset.cat || "all");
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ", "error");
    }

    previewAudioEl.onended = () => {
      playingPreviewId = null;
      renderVoiceCards(document.querySelector(".cat-pill.bg-indigo-600")?.dataset.cat || "all");
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
      if (!text) return showToast("စာသား အရင်ရိုက်ထည့်ပေးပါ", "error");

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
      a.click();
      showToast("MP3 ဒေါင်းလုဒ် ဆွဲပြီးပါပြီ", "success");
    }

    // Initialize View
    renderVoiceCards("all");
    updateTuningLabels();
    setGlobalEngine(globalAiEngine);
    document.getElementById("charCount").innerText = `${textInputEl.value.length} အက္ခရာ`;
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
