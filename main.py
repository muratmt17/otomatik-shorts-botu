import os
import asyncio
import requests
import json
from google import genai
from google.genai import types
import edge_tts

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
        '  "gorsel_promptu": "Cinematic lighting, photorealistic, 8k resolution, detailed scene description without commas"\n'
        "}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=kullanici_promptu,
            config=types.GenerateContentConfig(
                system_instruction=sistem_talimati,
                temperature=0.85,
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        return data["senaryo"], data["gorsel_promptu"]
    except Exception as e:
        print(f"Gemini API Hatası (Metin): {e}")
        return None, None

def yapay_zeka_gorseli_uret(prompt):
    """Ücretsiz ve sınırsız Pollinations AI motorunu kullanarak 9:16 dikey görsel üretir."""
    # Boşlukları URL formatına uygun hale getiriyoruz
    temiz_prompt = requests.utils.quote(prompt)
    
    # Tam dikey format (720x1280) ve en kararlı çalışan Flux/Flux-Anime yapay zeka görsel motoru
    url = f"https://image.pollinations.ai/p/{temiz_prompt}?width=720&height=1280&nologo=true&private=true"
    
    print(f"🎨 Görsel motoru tetikleniyor... Bağlantı: {url}")
    
    try:
        response = requests.get(url, timeout=40)
        if response.status_code == 200 and len(response.content) > 5000:
            with open("arka_plan.jpg", "wb") as f:
                f.write(response.content)
            print("📸 Konuya özel harika dikey görsel 'arka_plan.jpg' olarak kaydedildi.")
            return True
        else:
            print(f"Görsel motorundan geçersiz yanıt döndü. Kod: {response.status_code}")
            return False
    except Exception as e:
        print(f"Görsel indirilirken hata oluştu: {e}")
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
    try:
        response = requests.get(muzik_url, timeout=15)
        with open("muzik.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Müzik hazır.")
    except Exception as e:
        print(f"Müzik indirme hatası: {e}")

def videoyu_olustur():
    """Görseli, sesi ve müziği birleştirerek dikey video üretir (FFmpeg)."""
    print("🎬 Video montajı (Görsel + Ses + Müzik) başlıyor...")
    
    if not os.path.exists("arka_plan.jpg") or not os.path.exists("ses.mp3"):
        print("❌ Eksik kaynak dosyası olduğundan video birleştirilemedi!")
        return

    if os.path.exists("muzik.mp3"):
        komut = (
            "ffmpeg -y -loop 1 -framerate 25 -i arka_plan.jpg -i muzik.mp3 -i ses.mp3 "
            "-filter_complex \"[1:a]volume=0.08[bg]; [2:a]volume=1.0[voice]; [bg][voice]amix=inputs=2:duration=shortest[a]\" "
            "-map 0:v -map \"[a]\" -c:v libx264 -pix_fmt yuv420p -vf \"scale=720:1280\" -shortest final_shorts.mp4"
        )
    else:
        komut = (
            "ffmpeg -y -loop 1 -framerate 25 -i arka_plan.jpg -i ses.mp3 "
            "-map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -vf \"scale=720:1280\" -shortest final_shorts.mp4"
        )
        
    os.system(komut)
    
    if os.path.exists("final_shorts.mp4") and os.path.getsize("final_shorts.mp4") > 100000:
        size_mb = os.path.getsize("final_shorts.mp4") / (1024 * 1024)
        print(f"🎉 VİDEO BAŞARIYLA ÜRETİLDİ! Dosya boyutu: {size_mb:.2f} MB.")
    else:
        print("❌ FFmpeg gerçek bir video dosyası oluşturamadı veya dosya boş.")

async def ana_akis():
    print("🤖 1. ADIM: Bilgi ve Görsel Konsepti üretiliyor...")
    senaryo, gorsel_prompt = viral_senaryo_ve_gorsel_promptu_ureti()
    
    if not senaryo or not gorsel_prompt:
        print("❌ Senaryo veya görsel promptu alınamadı. İşlem durduruldu.")
        return
        
    print(f"\n📝 Senaryo:\n{senaryo}\n")
    print(f"🖼️ Görsel Promptu: {gorsel_prompt}\n")
    
    print("🤖 2. ADIM: Konuya özel dikey görsel üretiliyor...")
    gorsel_durum = yapay_zeka_gorseli_uret(gorsel_prompt)
    if not gorsel_durum:
        print("❌ Görsel düzeneği kurulamadı.")
        return
    
    print("🤖 3. ADIM: Seslendirme yapılıyor...")
    await metni_seslendir(senaryo, "ses.mp3")
    
    print("🤖 4. ADIM: Müzik hazırlanıyor...")
    hazir_muzik_indir()
    
    print("🤖 5. ADIM: Video Sentezleniyor (FFmpeg)...")
    videoyu_olustur()

if __name__ == "__main__":
    asyncio.run(ana_akis())
