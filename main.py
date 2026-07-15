import os
import asyncio
import requests
import json
import subprocess
from google import genai
from google.genai import types
import edge_tts

def viral_shorts_ureti():
    """Gemini API kullanarak senaryo, profesyonel yazı entegreli sinematik görsel promptu üretir."""
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    sistem_talimati = (
        "Sen YouTube Shorts ve TikTok üzerinde milyonlarca izlenen, profesyonel bir içerik üreticisisin. "
        "Görevin; tarih, gizem, bilim veya psikoloji hakkında izleyiciyi ekrana kilitleyecek "
        "maksimum 25 saniyelik bir Shorts içeriği tasarlamaktır. Görsellerin estetiği mükemmel olmalı."
    )

    kullanici_promptu = (
        "Bana bugün için viral olacak çok şaşırtıcı ve spesifik bir konu seç.\n"
        "Bana tam olarak şu JSON formatında cevap ver (başka hiçbir metin ekleme, sadece saf JSON dön):\n"
        "{\n"
        '  "baslik": "Videonun üzerine profesyonelce yazılacak, maksimum 3-4 kelimelik, ŞOK EDİCİ Türkçe kanca başlık (Örn: HAFIZAN SANA İHANET EDİYOR!)",\n'
        '  "senaryo": "İlk 3 saniyesi kancalı, merak uyandırıcı, akıcı, en sonda izleyiciyi yorum yapmaya davet eden Türkçe seslendirme metni.",\n'
        '  "gorsel_prompt_konu": "Bu konuyu tasvir eden hyper-realistic, dramatic vertical cinematic masterpiece sahnesinin sadece İngilizce görsel detayları (Arka plan, atmosfer, aydınlatma, nesneler)." \n'
        "}\n\n"
        "Not: 'baslik' kısmını İngilizceye çevirme, Türkçe kalsın."
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
        return data["baslik"], data["senaryo"], data["gorsel_prompt_konu"]
    except Exception as e:
        print(f"Gemini API Hatası: {e}")
        return None, None, None

def yapay_zeka_gorseli_uret(baslik, prompt_konu):
    """
    Sınırsız Pollinations AI motorunu kullanarak,
    Kanca Başlığı doğrudan görselin içine profesyonelce yerleştirilmiş dikey görsel üretir.
    """
    
    # Gemini'den gelen konuyu ve Türkçe başlığı birleştirip profesyonel bir metin entegrasyonu promptu oluşturuyoruz.
    # Bu aşama, image_0.png'deki gibi bir siyah bant yerine, yazıyı sahnenin bir parçası yapar.
    temiz_baslik = baslik.replace("'", "").replace('"', '').upper()
    gorsel_prompt = (
        f"A hyper-realistic, dramatic vertical (9:16) cinematic masterpiece depicting {prompt_konu}. "
        f"Epic composition, volumetric lighting, dark moody atmosphere, award-winning photography, 8k resolution. "
        f"Integrate the following text in large, bold, clean, white sans-serif lettering near the top-middle third of the image, "
        f"avoiding any dark background bars, styled as professional movie title graphics: '{temiz_baslik}'. "
        f"Ensure perfect spelling of the Turkish text and that it's readable but not distracting."
    )
    
    temiz_prompt = requests.utils.quote(gorsel_prompt)
    url = f"https://image.pollinations.ai/p/{temiz_prompt}?width=720&height=1280&nologo=true&private=true&model=flux"
    
    print(f"🎨 Profesyonel görsel üretiliyor (Metin entegreli)... Başlık: {baslik}")
    try:
        response = requests.get(url, timeout=60) # Yazı üretimi bazen biraz daha uzun sürebilir.
        if response.status_code == 200 and len(response.content) > 5000:
            with open("arka_plan.jpg", "wb") as f:
                f.write(response.content)
            print("📸 Profesyonel dikey görsel (metinli) başarıyla kaydedildi.")
            return True
        return False
    except Exception as e:
        print(f"Görsel hatası: {e}")
        return False

async def metni_seslendir(metin, cikis_ses_yolu):
    """Metni yapay zeka sesiyle Türkçe olarak seslendirir."""
    VOICE = "tr-TR-AhmetNeural" 
    communicate = edge_tts.Communicate(metin, VOICE)
    await communicate.save(cikis_ses_yolu)
    print(f"🔊 Ses dosyası oluşturuldu.")

def videoyu_olustur():
    """Görseli (zaten metni içeriyor) ve seslendirmeyi birleştirir."""
    print(f"🎬 Video montajı başladı (Müziksiz ve sade)...")
    
    if not os.path.exists("arka_plan.jpg") or not os.path.exists("ses.mp3"):
        print("❌ Eksik kaynak dosyası!")
        return

    # FFmpeg komutu artık çok basit; sadece görseli ve sesi birleştiriyoruz.
    # VF filtresi artık drawtext içermiyor, sadece doğru boyuta scale ediyor.
    komut = [
        "ffmpeg", "-y", "-nostdin",
        "-loop", "1", "-framerate", "25", "-i", "arka_plan.jpg",
        "-i", "ses.mp3",
        "-vf", "scale=720:1280", # Boyutu koru
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", "final_shorts.mp4"
    ]
        
    try:
        print("FFmpeg işlemi başlatılıyor...")
        result = subprocess.run(komut, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
        if result.returncode != 0:
            print(f"FFmpeg Hatası:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg işlemi zaman aşımına uğradı!")
    except Exception as e:
        print(f"FFmpeg çalıştırılırken hata: {e}")
    
    if os.path.exists("final_shorts.mp4") and os.path.getsize("final_shorts.mp4") > 100000:
        print("🎉 VİDEO BAŞARIYLA ÜRETİLDİ VE METNİ GÖRSELİN İÇİNDE!")
    else:
        print("❌ FFmpeg video oluşturamadı.")

async def ana_akis():
    print("🤖 1. ADIM: Bilgi ve Profesyonel Görsel Konsepti üretiliyor...")
    baslik, senaryo, gorsel_prompt_konu = viral_shorts_ureti()
    
    if not baslik or not senaryo or not gorsel_prompt_konu:
        print("❌ Gemini içerik üretemedi.")
        return
        
    print(f"\n💥 Kanca Başlık (Yazılacak): {baslik}")
    print(f"📝 Senaryo: {senaryo}")
    print(f"🖼️ Görsel Konu Promptu: {gorsel_prompt_konu}\n")
    
    print("🤖 2. ADIM: Metin entegreli Profesyonel Flux görseli üretiliyor...")
    # Artık başlığı ve konuyu görsel üretme fonksiyonuna birlikte veriyoruz.
    if not yapay_zeka_gorseli_uret(baslik, gorsel_prompt_konu): return
    
    print("🤖 3. ADIM: Seslendirme yapılıyor...")
    await metni_seslendir(senaryo, "ses.mp3")
    
    print("🤖 4. ADIM: FFmpeg ile nihai video paketleniyor...")
    # Videoyu oluştururken artık başlığı vermiyoruz, zaten görselde var.
    videoyu_olustur()

if __name__ == "__main__":
    asyncio.run(ana_akis())
