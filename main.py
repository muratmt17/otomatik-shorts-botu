import os
import asyncio
import requests
from google import genai
from google.genai import types
import edge_tts
from PIL import Image

def viral_senaryo_ve_gorsel_promptu_ureti():
    """Gemini API kullanarak viral Shorts senaryosu ve buna uygun görsel promptu üretir."""
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    sistem_talimati = (
        "Sen profesyonel bir YouTube Shorts üreticisisin. Görevin; tarih, bilim veya "
        "psikoloji hakkında şoke edici, maksimum 25-30 saniyelik bir senaryo yazmak "
        "ve bu senaryoyu en iyi temsil edecek dikey bir görsel üretimi için İngilizce prompt hazırlamaktır."
    )

    kullanici_promptu = (
        "Bana bugün için viral olacak şaşırtıcı bir bilgi seç.\n"
        "Bana tam olarak şu JSON formatında cevap ver (başka hiçbir metin ekleme, sadece JSON dön):\n"
        "{\n"
        '  "senaryo": "İlk 3 saniyesi kancalı, akıcı, sonu yorum yapmaya davet eden Türkçe seslendirme metni.",\n'
        '  "gorsel_promptu": "Görsel üretim modeli (Stable Diffusion) için İngilizce, dikey formatta (9:16), fotogerçekçi, dramatik ışıklandırmalı, konuyla ilgili detaylı görsel üretim promptu."\n'
        "}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=kullanici_promptu,
            config=types.GenerateContentConfig(
                system_instruction=sistem_talimati,
                temperature=0.85,
                response_mime_type="application/json" # Kesinlikle JSON dönmesini zorunlu kılıyoruz
            )
        )
        # Gelen JSON cevabını Python sözlüğüne çeviriyoruz
        import json
        data = json.loads(response.text)
        return data["senaryo"], data["gorsel_promptu"]
    except Exception as e:
        print(f"Gemini API Hatası: {e}")
        return None, None

def yapay_zeka_gorseli_uret(prompt):
    """Ücretsiz Hugging Face API kullanarak dikey formatta görsel üretir."""
    print(f"🎨 Görsel üretiliyor... Prompt: {prompt}")
    
    # Hugging Face üzerinde ücretsiz ve harika çalışan Stable Diffusion XL modeli
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    # GitHub Actions sırrı (İsteğe bağlı, token eklemesen de bazen kota dahilinde çalışır ama token ile garanti olur)
    headers = {}
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        headers = {"Authorization": f"Bearer {hf_token}"}
        
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 576,  # 9:16 dikey oranına yakın çözünürlükler
            "height": 1024
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            with open("arka_plan.jpg", "wb") as f:
                f.write(response.content)
            print("📸 Özel yapay zeka görseli 'arka_plan.jpg' olarak kaydedildi.")
            return True
        else:
            print(f"Görsel üretilemedi, Hata Kodu: {response.status_code}")
            return False
    except Exception as e:
        print(f"Görsel üretme hatası: {e}")
        return False

async def metni_seslendir(metin, cikis_ses_yolu):
    """Metni yapay zeka sesiyle Türkçe olarak seslendirir."""
    VOICE = "tr-TR-AhmetNeural" 
    communicate = edge_tts.Communicate(metin, VOICE)
    await communicate.save(cikis_ses_yolu)
    print(f"🔊 Ses dosyası oluşturuldu: {cikis_ses_yolu}")

def hazir_muzik_indir():
    """Arka plana koymak için telifsiz kısa bir fon müziği indirir."""
    print("📥 Fon müziği indiriliyor...")
    muzik_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    with open("muzik.mp3", "wb") as f:
        f.write(requests.get(muzik_url).content)
    print("✅ Müzik hazır.")

def videoyu_olustur():
    """Görseli, sesi ve müziği birleştirerek dikey video üretir (FFmpeg)."""
    print("🎬 Video montajı (Görsel + Ses + Müzik) başlıyor...")
    
    # Bu komut: Tek bir görseli (arka_plan.jpg), ses dosyasının (ses.mp3) süresi kadar uzatır,
    # arkaya fon müziğini kısık sesle ekler ve dikey mp4 video üretir.
    komut = (
        "ffmpeg -y -loop 1 -i arka_plan.jpg -i muzik.mp3 -i ses.mp3 "
        "-filter_complex \"[1:a]volume=0.12[bg]; [2:a]volume=1.0[voice]; [bg][voice]amix=inputs=2:duration=shortest[a]\" "
        "-map 0:v -map \"[a]\" -c:v libx264 -tune stillimage -pix_fmt yuv420p -shortest final_shorts.mp4"
    )
    os.system(komut)
    print("🎉 VİDEO HAZIR! 'final_shorts.mp4' başarıyla üretildi.")

async def ana_akis():
    print("🤖 1. ADIM: Bilgi ve Görsel Konsepti üretiliyor...")
    senaryo, gorsel_prompt = viral_senaryo_ve_gorsel_promptu_ureti()
    
    if not senaryo or not gorsel_prompt:
        print("❌ Senaryo veya görsel promptu alınamadı. İşlem durduruldu.")
        return
        
    print(f"\n📝 Senaryo:\n{senaryo}\n")
    print(f"🖼️ Görsel Promptu: {gorsel_prompt}\n")
    
    print("🤖 2. ADIM: Konuya özel görsel üretiliyor...")
    gorsel_durum = yapay_zeka_gorseli_uret(gorsel_prompt)
    if not gorsel_durum:
        print("❌ Görsel üretilemediği için devam edilemiyor.")
        return
    
    print("🤖 3. ADIM: Seslendirme yapılıyor...")
    await metni_seslendir(senaryo, "ses.mp3")
    
    print("🤖 4. ADIM: Müzik hazırlanıyor...")
    hazir_muzik_indir()
    
    print("🤖 5. ADIM: Video sentezleniyor...")
    videoyu_olustur()

if __name__ == "__main__":
    asyncio.run(ana_akis())
