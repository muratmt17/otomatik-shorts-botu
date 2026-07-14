import os
import asyncio
import requests
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
        '  "gorsel_promptu": "A dramatic, photorealistic vertical (9:16) image depicting the scene, highly detailed, cinematic lighting, 8k resolution"\n'
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
        import json
        data = json.loads(response.text)
        return data["senaryo"], data["gorsel_promptu"]
    except Exception as e:
        print(f"Gemini API Hatası (Metin): {e}")
        return None, None

def yapay_zeka_gorseli_uret(prompt):
    """Google Gemini Imagen API kullanarak dikey formatta görsel üretir."""
    print(f"🎨 Gemini Imagen ile görsel üretiliyor... Prompt: {prompt}")
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    try:
        # En güncel ve genel erişime açık Imagen 3 ana model adını kullanıyoruz
        result = client.models.generate_images(
            model='imagen-3.0-generate-002', 
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="9:16",
                person_generation="ALLOW_ADULT",
            )
        )
        
        for generated_image in result.generated_images:
            with open("arka_plan.jpg", "wb") as f:
                f.write(generated_image.image.image_bytes)
                
        print("📸 Özel yapay zeka görseli başarıyla 'arka_plan.jpg' olarak kaydedildi.")
        return True
    except Exception as e:
        print(f"Gemini Görsel Üretme Hatası: {e}")
        print("⚠️ Görsel üretilemediği için yedek (standart) bir görsel oluşturuluyor...")
        
        # Eğer API modeli bölge/hesap kısıtlamasından dolayı yine reddederse, 
        # sistemin çökmemesi için internetten hemen telifsiz dikey şık bir görsel çekiyoruz.
        try:
            yedek_url = "https://images.pexels.com/photos/281260/pexels-photo-281260.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
            response = requests.get(yedek_url, timeout=15)
            with open("arka_plan.jpg", "wb") as f:
                f.write(response.content)
            print("ℹ️ Yedek görsel başarıyla indirildi. Sistem devam ediyor!")
            return True
        except Exception as yedek_hata:
            print(f"Yedek görsel de alınamadı: {yedek_hata}")
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
        print("❌ Eksik dosya var, video birleştirilemiyor!")
        return

    if os.path.exists("muzik.mp3"):
        komut = (
            "ffmpeg -y -loop 1 -i arka_plan.jpg -i muzik.mp3 -i ses.mp3 "
            "-filter_complex \"[1:a]volume=0.12[bg]; [2:a]volume=1.0[voice]; [bg][voice]amix=inputs=2:duration=shortest[a]\" "
            "-map 0:v -map \"[a]\" -c:v libx264 -tune stillimage -pix_fmt yuv420p -shortest final_shorts.mp4"
        )
    else:
        komut = (
            "ffmpeg -y -loop 1 -i arka_plan.jpg -i ses.mp3 "
            "-c:v libx264 -tune stillimage -c:a aac -pix_fmt yuv420p -shortest final_shorts.mp4"
        )
        
    os.system(komut)
    if os.path.exists("final_shorts.mp4"):
        print("🎉 VİDEO HAZIR! 'final_shorts.mp4' başarıyla üretildi.")
    else:
        print("❌ FFmpeg video oluşturamadı.")

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
        print("❌ Görsel düzeneği kurulamadı. Devam edilemiyor.")
        return
    
    print("🤖 3. ADIM: Seslendirme yapılıyor...")
    await metni_seslendir(senaryo, "ses.mp3")
    
    print("🤖 4. ADIM: Müzik hazırlanıyor...")
    hazir_muzik_indir()
    
    print("🤖 5. ADIM: Video sentezleniyor...")
    videoyu_olustur()

if __name__ == "__main__":
    asyncio.run(ana_akis())
