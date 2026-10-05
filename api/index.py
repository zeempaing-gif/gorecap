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
<html lang="my" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>TTS Pro • မြန်မာအသံ စတူဒီယို</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Plus Jakarta Sans', 'Padauk', 'sans-serif'],
            burmese: ['Padauk', 'sans-serif']
          },
          colors: {
            surface: {
              DEFAULT: '#090d16',
              card: '#0f172a',
              input: '#030712',
              hover: '#1e293b'
            }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Padauk', 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 5px; }
    .custom-scroll::-webkit-scrollbar-track { background: transparent; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 9999px; }
    .custom-scroll::-webkit-scrollbar-thumb:hover { background: #475569; }
    @keyframes barWave {
      0%, 100% { height: 4px; }
      50% { height: 18px; }
    }
    .wave-bar { animation: barWave 0.8s ease-in-out infinite; }
  </style>
</head>
<body class="bg-[#090d16] text-slate-100 min-h-screen flex flex-col items-center antialiased selection:bg-amber-500 selection:text-slate-950">

  <!-- Floating Toast Notification System -->
  <div id="toastContainer" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Header Nav -->
  <header class="w-full border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-lg shadow-lg shadow-amber-500/20 font-bold text-slate-950">
          🎙️
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-bold tracking-tight text-white font-sans">TTS Pro Studio</h1>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 font-sans">
              Burmese AI
            </span>
          </div>
          <p class="text-[11px] text-slate-400 hidden sm:block">သဘာဝကျသော မြန်မာအသံနှင့် Movie Recap အသံဖန်တီးခန်း</p>
        </div>
      </div>

      <!-- Cloud Status Badge -->
      <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-full text-xs text-slate-300">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-[11px] font-medium font-sans">Vercel Cloud Active</span>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-5xl w-full p-4 sm:p-6 space-y-6 flex-1">
    
    <!-- Hero Banner / Quick Info -->
    <div class="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-orange-500/5 to-transparent border border-amber-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h2 class="text-sm font-bold text-amber-300 flex items-center gap-1.5">
          <span>✨</span>
          <span>ပရော်ဖက်ရှင်နယ် မြန်မာအသံ ကာရိုက်တာ (၁၀) မျိုး</span>
        </h2>
        <p class="text-xs text-slate-400 mt-0.5 leading-relaxed">
          အောက်ပါ ကာရိုက်တာများမှ မိမိစိတ်ကြိုက် အသံကို ရွေးချယ်ပြီး အသံစမ်းဖွင့်ကြည့်နိုင်ပါသည်
        </p>
      </div>
      <div id="activeVoicePill" class="text-xs font-bold text-amber-300 bg-amber-950/80 border border-amber-800/80 px-3 py-1.5 rounded-xl shrink-0">
        ရွေးထားသည်: နေတိုး
      </div>
    </div>

    <!-- Main Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- Left Column: Voice Personas Catalog -->
      <section class="lg:col-span-6 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 space-y-4 backdrop-blur-sm">
        
        <!-- Filter Tabs -->
        <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <span class="text-xs font-bold text-slate-300 uppercase tracking-wider font-sans">အသံကဏ္ဍခွဲများ</span>
          <div class="flex gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-[11px]">
            <button onclick="filterVoices('all')" class="cat-pill px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-bold transition-all" data-cat="all">အားလုံး</button>
            <button onclick="filterVoices('men')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="men">လူကြီး</button>
            <button onclick="filterVoices('boy')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="boy">လူငယ်</button>
            <button onclick="filterVoices('women')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="women">အမျိုးသမီး</button>
            <button onclick="filterVoices('girl')" class="cat-pill px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 transition-all" data-cat="girl">မိန်းကလေး</button>
          </div>
        </div>

        <!-- Voice Cards Container -->
        <div id="voiceCardsList" class="space-y-2.5 max-h-[460px] overflow-y-auto pr-1.5 custom-scroll">
          <!-- Injected via JavaScript -->
        </div>
      </section>

      <!-- Right Column: Input & Studio Controls -->
      <section class="lg:col-span-6 space-y-5">

        <!-- Editor Box -->
        <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 sm:p-5 space-y-4 backdrop-blur-sm shadow-xl">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-300 font-sans">မြန်မာစာသား ထည့်သွင်းရန်</span>
            <div class="flex items-center gap-2 text-xs text-slate-400">
              <span id="charCount" class="font-mono text-[11px] text-amber-400 font-semibold">၀ အက္ခရာ</span>
              <span>•</span>
              <button onclick="clearText()" class="text-rose-400 hover:underline">ဖျက်မည်</button>
            </div>
          </div>

          <!-- Textarea -->
          <textarea
            id="textInput"
            rows="6"
            placeholder="အသံဖန်တီးလိုသော မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ..."
            class="w-full bg-[#030712] border border-slate-800 rounded-xl p-3.5 text-sm leading-relaxed text-slate-100 placeholder-slate-600 focus:outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/50 transition-all resize-y"
          >သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။</textarea>

          <!-- Quick Text Presets -->
          <div class="flex flex-wrap items-center gap-1.5 text-xs text-slate-400">
            <span class="text-[11px]">နမူနာ:</span>
            <button onclick="setSample(1)" class="px-2 py-0.5 rounded-md bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-[11px]">🎬 Recap</button>
            <button onclick="setSample(2)" class="px-2 py-0.5 rounded-md bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-[11px]">📰 သတင်း</button>
            <button onclick="setSample(3)" class="px-2 py-0.5 rounded-md bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-[11px]">📖 ဝတ္ထု/ပုံပြင်</button>
          </div>

          <!-- Fine Tuning Controls (Speed & Pitch) -->
          <div class="grid grid-cols-2 gap-4 pt-3 border-t border-slate-800/80">
            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <div class="flex justify-between text-xs mb-1.5">
                <span class="text-slate-400 font-medium">စကားပြောနှုန်း</span>
                <span id="speedVal" class="text-amber-400 font-mono font-bold">မူရင်း</span>
              </div>
              <input
                id="speedRange"
                type="range"
                min="-20"
                max="20"
                step="2"
                value="0"
                class="w-full accent-amber-500 cursor-pointer"
                oninput="updateTuningLabels()"
              />
              <div class="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>နှေး</span>
                <span>ပုံမှန်</span>
                <span>မြန်</span>
              </div>
            </div>

            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <div class="flex justify-between text-xs mb-1.5">
                <span class="text-slate-400 font-medium">အသံအမြင့် (Pitch)</span>
                <span id="pitchVal" class="text-amber-400 font-mono font-bold">မူရင်း</span>
              </div>
              <input
                id="pitchRange"
                type="range"
                min="-15"
                max="15"
                step="1"
                value="0"
                class="w-full accent-amber-500 cursor-pointer"
                oninput="updateTuningLabels()"
              />
              <div class="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>ဩဇာ</span>
                <span>ပုံမှန်</span>
                <span>ကြည်</span>
              </div>
            </div>
          </div>

          <!-- Generate Action Button -->
          <button
            id="generateBtn"
            type="button"
            onclick="handleGenerateVoice()"
            class="w-full py-4 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:brightness-110 active:scale-[0.99] text-slate-950 font-bold text-sm shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2.5 transition-all"
          >
            <span id="genSpinner" class="hidden animate-spin text-base">🌀</span>
            <span id="genText">🎙️️ အသံဖန်တီးမည် (Generate Speech)</span>
          </button>
        </div>

        <!-- Audio Output & Player Card -->
        <div id="playerSection" class="hidden bg-gradient-to-b from-slate-900 to-slate-950 border border-amber-500/40 rounded-2xl p-5 space-y-4 shadow-2xl">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <!-- Animated Wave Visualizer -->
              <div class="flex items-center gap-0.5 h-5 px-2 py-1 bg-amber-500/10 rounded-lg border border-amber-500/20">
                <span class="w-1 bg-amber-400 rounded-full wave-bar" style="animation-delay: 0.1s"></span>
                <span class="w-1 bg-amber-400 rounded-full wave-bar" style="animation-delay: 0.3s"></span>
                <span class="w-1 bg-amber-400 rounded-full wave-bar" style="animation-delay: 0.2s"></span>
                <span class="w-1 bg-amber-400 rounded-full wave-bar" style="animation-delay: 0.4s"></span>
              </div>
              <span id="playerVoiceTitle" class="text-xs font-bold text-amber-300">အသံဖိုင် အဆင်သင့်ဖြစ်ပါပြီ</span>
            </div>
            <span class="text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">
              MP3 Ready
            </span>
          </div>

          <audio id="mainAudio" controls class="w-full rounded-xl outline-none"></audio>

          <button
            type="button"
            onclick="downloadMp3()"
            class="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:scale-[0.99] text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/25 transition-all"
          >
            <span>📥</span>
            <span>MP3 ဒေါင်းလုဒ်ဆွဲမည် (Download Audio)</span>
          </button>
        </div>

      </section>

    </div>
  </main>

  <!-- Hidden Preview Audio Element -->
  <audio id="previewAudio" class="hidden"></audio>

  <script>
    const PERSONAS = [
      {
        id: "nay-toe",
        name: "နေတိုး",
        category: "boy",
        icon: "👦",
        badge: "လူငယ်အမျိုးသား",
        role: "တက်ကြွ လန်းဆန်းသော လူငယ်သံ (Movie Recap အကောင်းဆုံး)",
        sample: "မင်္ဂလာပါ၊ ကျွန်တော် နေတိုး ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "tha-zin",
        name: "သဇင်",
        category: "girl",
        icon: "👧",
        badge: "မိန်းကလေးငယ်",
        role: "သွက်လက် ချိုသာသော အပျိုမလေးသံ (TikTok / Shorts အထူးကောင်း)",
        sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ သဇင် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"
      },
      {
        id: "tay-za",
        name: "တေဇ",
        category: "boy",
        icon: "🧑",
        badge: "လူငယ်အမျိုးသား",
        role: "သဘာဝကျပြီး ရှင်းလင်းပြတ်သားသော ဇာတ်ကြောင်းပြောဟန်",
        sample: "မင်္ဂလာပါ၊ ကျွန်တော် တေဇ ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "may-hnin",
        name: "မေနှင်း",
        category: "girl",
        icon: "🌸",
        badge: "မိန်းကလေးငယ်",
        role: "ကြည်လင် အေးချမ်းသော ကောင်မလေးသံ (ဝတ္ထုဖတ်/စာအုပ်)",
        sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ မေနှင်း ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"
      },
      {
        id: "u-han",
        name: "ဦးဟန်",
        category: "men",
        icon: "👨",
        badge: "လူကြီးအမျိုးသား",
        role: "တည်ကြည် ခန့်ညားသော လူကြီးသံ (သတင်း/အသိပညာပေး)",
        sample: "မင်္ဂလာပါ၊ ကျွန်တော် ဦးဟန် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "u-kyi",
        name: "ဦးကြည်",
        category: "men",
        icon: "👴",
        badge: "အဖိုး/လူကြီးသံ",
        role: "အသံဩဇာပြည့်ဝပြီး လေးနက်သော အဖိုးကြီးသံ (သမိုင်း/ဒဏ္ဍာရီ)",
        sample: "မင်္ဂလာပါ၊ ကျွန်တော် ဦးကြည် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "daw-yin",
        name: "ဒေါ်ရင်",
        category: "women",
        icon: "👩",
        badge: "အမျိုးသမီးကြီး",
        role: "နွေးထွေး ကြင်နာတတ်သော မိခင်သံ (တရားတော်/ဘဝအတွေ့အကြုံ)",
        sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်ရင် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "daw-soe",
        name: "ဒေါ်စိုး",
        category: "women",
        icon: "🧕",
        badge: "အမျိုးသမီးကြီး",
        role: "တည်ငြိမ် ရင့်ကျက်သော အိမ်ထောင်ရှင်အမျိုးသမီးသံ",
        sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်စိုး ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "zaw-zaw",
        name: "ဇော်ဇော်",
        category: "boy",
        icon: "🧒",
        badge: "ဆယ်ကျော်သက်",
        role: "သွက်လက် ပေါ့ပါးသော လူငယ်စကားပြောဟန် (Vlog/ဟာသ)",
        sample: "မင်္ဂလာပါ၊ ကျွန်တော် ဇော်ဇော် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
      },
      {
        id: "nu-nu",
        name: "နုနု",
        category: "girl",
        icon: "🎀",
        badge: "ကလေးမလေးသံ",
        role: "နူးညံ့ ချစ်စဖွယ် ကလေးမလေးသံ (ညအိပ်ရာဝင် ပုံပြင်)",
        sample: "မင်္ဂလာပါရှင်၊ ကျွန်မ နုနု ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်ရှင်။"
      }
    ];

    let selectedId = "nay-toe";
    let playingPreviewId = null;
    let generatedBlob = null;

    const previewAudioEl = document.getElementById("previewAudio");
    const mainAudioEl = document.getElementById("mainAudio");
    const textInputEl = document.getElementById("textInput");

    function showToast(msg, type = "info") {
      const container = document.getElementById("toastContainer");
      const toast = document.createElement("div");
      toast.className = `px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold flex items-center gap-2 transition-all transform duration-300 translate-y-2 opacity-0 pointer-events-auto border ${
        type === 'error' ? 'bg-rose-950 border-rose-800 text-rose-200' :
        type === 'success' ? 'bg-emerald-950 border-emerald-800 text-emerald-200' :
        'bg-slate-900 border-slate-700 text-slate-200'
      }`;
      toast.innerHTML = `<span>${type === 'error' ? '⚠️️' : type === 'success' ? '✓' : 'ℹ️'}</span><span>${msg}</span>`;
      container.appendChild(toast);

      setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
      }, 20);

      setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

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
              isPreviewing
                ? 'bg-amber-500 text-slate-950 animate-pulse'
                : 'bg-slate-800/90 hover:bg-amber-950/60 text-amber-300 border border-amber-500/30'
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
      showToast("အသံစမ်းဖွင့်၍ မရသေးပါ။ စက္ကန့် ၃၀ ခန့်စောင့်ပြီး ပြန်လည်စမ်းသပ်ပေးပါ", "error");
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

    function setSample(type) {
      if (type === 1) {
        textInputEl.value = "သူက အိမ်ထဲကို ဝင်သွားပြီးတော့ ခဏအကြာမှာ ပြန်ထွက်လာတယ်။ အရာအားလုံးက မထင်မှတ်ထားတဲ့အတိုင်း ဖြစ်ပျက်သွားခဲ့ပါတယ်။";
      } else if (type === 2) {
        textInputEl.value = "ယနေ့ ညနေပိုင်းတွင် ထူးခြားသော မိုးလေဝသ အခြေအနေများနှင့် ပတ်သက်၍ အထူးသတိပေးချက်တစ်ရပ် ထုတ်ပြန်လိုက်ပါသည်။";
      } else {
        textInputEl.value = "ဟိုးရှေးရှေးတုန်းက သာယာလှပတဲ့ ရွာကလေးတစ်ရွာမှာ ကြင်နာတတ်တဲ့ သူငယ်ချင်းနှစ်ယောက် ရှိကြသတဲ့။";
      }
      document.getElementById("charCount").innerText = `${textInputEl.value.length} အက္ခရာ`;
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
          showToast(`${persona.name} ၏ အသံဖိုင်ကို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ`, "success");
        } else {
          const data = await res.json().catch(() => ({}));
          showToast(data.detail || "အသံဖန်တီးရာတွင် အဆင်မပြေဖြစ်သွားပါသည်", "error");
        }
      } catch (err) {
        showToast("ချိတ်ဆက်မှု မအောင်မြင်ပါ။ ခဏစောင့်ပြီး ပြန်လည်စမ်းသပ်ပေးပါ", "error");
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

    // Init
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
@app.get("/health")
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
