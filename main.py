import os
import asyncio
import requests
import json
from google import genai
from google.genai import types
import edge_tts

def viral_shorts_ureti():
    """Gemini API kullanarak senaryo, sinematik görsel promptu ve video içi başlık üretir."""
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    sistem_talimati = (
        "Sen YouTube Shorts ve TikTok üzerinde milyonlarca izlenen bir içerik üreticisisin. "
        "Görevin; tarih, gizem, bilim veya psikoloji hakkında izleyiciyi ekrana kilitleyecek "
        "maksimum 25 saniyelik bir Shorts içeriği tasarlamaktır."
    )

    kullanici_promptu = (
        "Bana bugün için viral olacak çok şaşırtıcı bir konu seç.\n"
        "Bana tam olarak şu JSON formatında cevap ver (başka hiçbir metin ekleme, sadece saf JSON dön):\n"
        "{\n"
        '  "baslik": "Videonun üzerine büyük harflerle yazılacak, maksimum 3-4 kelimelik, ŞOK EDİCİ Türkçe kanca başlık (Örn: BU BİLGİ YASAKLANDI!)",\n'
        '  "senaryo": "İlk 3 saniyesi kancalı, merak uyandırıcı, akıcı, en sonda izleyiciyi yorum yapmaya davet eden Türkçe seslendirme metni.",\n'
        '  "gorsel_promptu": "A hyper-realistic, dramatic vertical (9:16) cinematic masterpiece depicting the scene. Epic composition, volumetric lighting, dark moody atmosphere, award-winning photography, 8k resolution, highly detailed textures, Unreal Engine 5 render style, no text inside image."\n'
        "}\n\n"
        "Not: 'gorsel_promptu' kısmına benim verdiğim şablonun üzerine konuyu tasvir eden İngilizce detayları da ekle."
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
        return data["baslik"], data["senaryo"], data["gorsel_promptu"]
    except Exception as e:
        print(f"Gemini API Hatası: {e}")
        return None, None, None

def yapay_zeka_gorseli_uret(prompt):
    """Sınırsız Pollinations AI motorunu kullanarak sinematik 9:16 dikey görsel üretir."""
    temiz_prompt = requests.utils.quote(prompt)
    # Daha sanatsal ve gelişmiş olan "flux" modelini zorunlu kılıyoruz
    url = f"https://image.pollinations.ai/p/{temiz_prompt}?width=720&height=1280&nologo=true&private=true&model=flux"
    
    print(f"🎨 Sinematik görsel üretiliyor... Model: Flux")
    try:
        response = requests.get(url, timeout=40)
        if response.status_code == 200 and len(response.content) > 5000:
            with open("arka_plan.jpg", "wb") as f:
                f.write(response.content)
            print("📸 Sinematik dikey görsel başarıyla kaydedildi.")
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

def hazir_muzik_indir():
    """Arka plana koymak için telifsiz kısa bir fon müziği indirir."""
    muzik_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    try:
        response = requests.get(muzik_url, timeout=15)
        with open("muzik.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Müzik hazır.")
    except Exception:
        print("Müzik indirilemedi, videoya müziksiz devam edilecek.")

def videoyu_olustur(baslik):
    """Görseli, sesi, müziği ve VİDEO ÜZERİNE METNİ (Kanca Başlık) birleştirir."""
    print(f"🎬 Video montajı ve yazı ekleme başladı... Başlık: {baslik}")
    
    if not os.path.exists("arka_plan.jpg") or not os.path.exists("ses.mp3"):
        print("❌ Eksik kaynak dosyası!")
        return

    # FFmpeg üzerinde videonun üst-orta kısmına büyük, kalın, siyah gölgeli beyaz yazı ekleme filtresi
    # Satır kırılmalarında hata olmaması için başlığı temizliyoruz
    temiz_baslik = baslik.replace("'", "").replace('"', '').upper()
    
    yazi_filtresi = (
        f"scale=720:1280,drawtext=text='{temiz_baslik}':fontcolor=white:fontsize=48:"
        f"font='Sans':x=(w-text_w)/2:y=(h-text_h)/4:box=1:boxcolor=black@0.6:boxborderw=20"
    )

    if os.path.exists("muzik.mp3"):
        komut = (
            f"ffmpeg -y -loop 1 -framerate 25 -i arka_plan.jpg -i muzik.mp3 -i ses.mp3 "
            f"-filter_complex \"[0:v]{yazi_filtresi}[v]; [1:a]volume=0.07[bg]; [2:a]volume=1.0[voice]; [bg][voice]amix=inputs=2:duration=shortest[a]\" "
            f"-map \"[v]\" -map \"[a]\" -c:v libx264 -pix_fmt yuv420p -shortest final_shorts.mp4"
        )
    else:
        komut = (
            f"ffmpeg -y -loop 1 -framerate 25 -i arka_plan.jpg -i ses.mp3 "
            f"-vf \"{yazi_filtresi}\" -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -shortest final_shorts.mp4"
        )
        
    os.system(komut)
    
    if os.path.exists("final_shorts.mp4") and os.path.getsize("final_shorts.mp4") > 100000:
        print("🎉 KANCA BAŞLIKLI VİDEO BAŞARIYLA ÜRETİLDİ!")
    else:
        print("❌ FFmpeg video oluşturamadı.")

async def ana_akis():
    print("🤖 1. ADIM: Bilgi, Başlık ve Sinematik Görsel Konsepti üretiliyor...")
    baslik, senaryo, gorsel_prompt = viral_shorts_ureti()
    
    if not baslik or not senaryo or not gorsel_prompt:
        print("❌ Gemini içerik üretemedi.")
        return
        
    print(f"\n💥 Kanca Başlık: {baslik}")
    print(f"📝 Senaryo: {senaryo}")
    print(f"🖼️ Gelişmiş Görsel Promptu: {gorsel_prompt}\n")
    
    print("🤖 2. ADIM: Profesyonel Flux dikey görseli üretiliyor...")
    if not yapay_zeka_gorseli_uret(gorsel_prompt): return
    
    print("🤖 3. ADIM: Seslendirme yapılıyor...")
    await metni_seslendir(senaryo, "ses.mp3")
    
    print("🤖 4. ADIM: Müzik hazırlanıyor...")
    hazir_muzik_indir()
    
    print("🤖 5. ADIM: FFmpeg ile Başlık Videoya işleniyor...")
    videoyu_olustur(baslik)

if __name__ == "__main__":
    asyncio.run(ana_akis())
