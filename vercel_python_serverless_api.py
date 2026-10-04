import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI(title="TTS Pro - Vercel Serverless Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# မြန်မာ အသံကာရိုက်တာ (၁၀) မျိုး
PERSONA_VOICES = [
    # ၁။ လူကြီး/အဖိုး/ဦးလေး အသံများ (Mature Men)
    {
        "id": "u-han",
        "name": "ဦးဟန်",
        "category": "men",
        "gender": "အမျိုးသားကြီး",
        "role": "တည်ကြည် ခန့်ညားသော လူကြီးသံ (သတင်း/အသိပညာပေး)",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "-4%",
        "base_pitch": "-12Hz",
        "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဦးဟန် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },
    {
        "id": "u-kyi",
        "name": "ဦးကြည်",
        "category": "men",
        "gender": "အဖိုး/လူကြီးသံ",
        "role": "အသံဩဇာပြည့်ဝပြီး လေးနက်သော လူကြီးသံ (သမိုင်း/ဝတ္ထု)",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "-6%",
        "base_pitch": "-18Hz",
        "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဦးကြည် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },

    # ၂။ ကောင်လေး/လူငယ် အသံများ (Boys / Young Men)
    {
        "id": "nay-toe",
        "name": "နေတိုး",
        "category": "boy",
        "gender": "လူငယ်အမျိုးသား",
        "role": "တက်ကြွ လန်းဆန်းသော လူငယ်သံ (Movie Recap အကောင်းဆုံး)",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "+4%",
        "base_pitch": "+4Hz",
        "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် နေတိုး ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },
    {
        "id": "tay-za",
        "name": "တေဇ",
        "category": "boy",
        "gender": "လူငယ်အမျိုးသား",
        "role": "သဘာဝကျပြီး ရှင်းလင်းပြတ်သားသော ဇာတ်ကြောင်းပြောသံ",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် တေဇ ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },
    {
        "id": "zaw-zaw",
        "name": "ဇော်ဇော်",
        "category": "boy",
        "gender": "ဆယ်ကျော်သက် ကောင်လေး",
        "role": "သွက်လက် ပေါ့ပါးသော လူငယ်စကားပြောဟန် (Vlog/ဟာသ)",
        "base_voice": "my-MM-ThihaNeural",
        "base_rate": "+7%",
        "base_pitch": "+12Hz",
        "sample_text": "မင်္ဂလာပါ၊ ကျွန်တော် ဇော်ဇော် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },

    # ၃။ အဒေါ်/အမျိုးသမီးကြီး အသံများ (Mature Women)
    {
        "id": "daw-yin",
        "name": "ဒေါ်ရင်",
        "category": "women",
        "gender": "အမျိုးသမီးကြီး",
        "role": "နွေးထွေး ကြင်နာတတ်သော မိခင်သံ (တရားတော်/ဘဝအတွေ့အကြုံ)",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "-4%",
        "base_pitch": "-8Hz",
        "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်ရင် ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },
    {
        "id": "daw-soe",
        "name": "ဒေါ်စိုး",
        "category": "women",
        "gender": "အမျိုးသမီးကြီး",
        "role": "တည်ငြိမ် ရင့်ကျက်သော အိမ်ထောင်ရှင်အမျိုးသမီးသံ",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "-6%",
        "base_pitch": "-14Hz",
        "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ ဒေါ်စိုး ဖြစ်ပါတယ်။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်။"
    },

    # ၄။ မိန်းကလေးငယ်/ကောင်မလေး အသံများ (Young Girls)
    {
        "id": "tha-zin",
        "name": "သဇင်",
        "category": "girl",
        "gender": "မိန်းကလေးငယ်",
        "role": "သွက်လက် ချိုသာသော အပျိုမလေးသံ (Movie Recap/TikTok)",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "+3%",
        "base_pitch": "+6Hz",
        "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ သဇင် ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"
    },
    {
        "id": "may-hnin",
        "name": "မေနှင်း",
        "category": "girl",
        "gender": "မိန်းကလေးငယ်",
        "role": "ကြည်လင် အေးချမ်းသော ကောင်မလေးသံ (ပုံပြင်/ဝတ္ထုဖတ်)",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "+0%",
        "base_pitch": "+0Hz",
        "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ မေနှင်း ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်နော်။"
    },
    {
        "id": "nu-nu",
        "name": "နုနု",
        "category": "girl",
        "gender": "မိန်းကလေးငယ်",
        "role": "နူးညံ့ ချစ်စဖွယ် ကလေးမလေးသံ (ညအိပ်ရာဝင် ပုံပြင်)",
        "base_voice": "my-MM-NilarNeural",
        "base_rate": "+2%",
        "base_pitch": "+12Hz",
        "sample_text": "မင်္ဂလာပါရှင်၊ ကျွန်မ နုနု ပါ။ ရီကတ်ဂိုးအေအိုင်မှာ ကြိုဆိုပါတယ်ရှင်။"
    }
]

PERSONA_DICT = {p["id"]: p for p in PERSONA_VOICES}

class GenerateTTSRequest(BaseModel):
    text: str
    persona_id: str = "nay-toe"
    user_rate_offset: int = 0
    user_pitch_offset: int = 0

@app.get("/api/health")
@app.get("/health")
def health():
    return {"status": "ok", "provider": "Microsoft Edge TTS"}

@app.get("/api/voices")
@app.get("/voices")
def get_voices():
    return {"voices": PERSONA_VOICES}

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