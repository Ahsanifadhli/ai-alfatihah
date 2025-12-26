import gradio as gr
import whisper
import re
import difflib

# 1. Load Model
print("Loading model...")
model = whisper.load_model("small")

# 2. Database Al-Fatihah
DATABASE_ALFATIHAH = {
    1: "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
    2: "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ",
    3: "ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
    4: "مَٰلِكِ يَوْمِ ٱلدِّينِ",
    5: "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
    6: "ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ",
    7: "صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ"
}

# 3. Fungsi Normalisasi
def normalisasi_arab(teks):
    if not teks: return ""
    teks = re.sub(r'[\u064B-\u065F\u0670]', '', teks)
    teks = re.sub(r'[أإٱآ]', 'ا', teks)
    teks = re.sub(r'ى', 'ي', teks)
    teks = re.sub(r'ة', 'ه', teks)
    teks = re.sub(r'ؤ', 'و', teks)
    teks = teks.replace(" ", "")
    return teks.strip()

# 4. Fungsi Utama
def proses_suara(audio_path, ayat_pilihan):
    if audio_path is None:
        return "⚠️ Mohon rekam suara dulu."
    
    nomor_ayat = int(ayat_pilihan.split(" ")[1]) 
    target_raw = DATABASE_ALFATIHAH[nomor_ayat]
    target_clean = normalisasi_arab(target_raw)
    
    try:
        hasil = model.transcribe(audio_path, language='ar', fp16=False)
        ucapan_raw = hasil["text"].strip()
        ucapan_clean = normalisasi_arab(ucapan_raw)
        
        skor = difflib.SequenceMatcher(None, target_clean, ucapan_clean).ratio()
        
        # Format Pesan Hasil
        status = "✅ LULUS" if skor >= 0.70 else "❌ BELUM LULUS"
        
        pesan = f"STATUS: {status}\n"
        pesan += f"📊 Akurasi: {skor:.0%}\n"
        pesan += f"----------------------------\n"
        pesan += f"🎯 Target: {target_raw}\n"
        pesan += f"🗣️ Kamu : {ucapan_raw}"
        
        return pesan
            
    except Exception as e:
        return f"Error: {str(e)}"

# 5. Tampilan Web (UI)
pilihan_ayat = [f"Ayat {i}" for i in range(1, 8)]

interface = gr.Interface(
    fn=proses_suara,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Rekam Suara"),
        gr.Dropdown(choices=pilihan_ayat, label="📖 Pilih Ayat", value="Ayat 1")
    ],
    # --- PERBAIKAN DISINI ---
    outputs=gr.Textbox(label="📝 Hasil Analisis AI", lines=6), 
    # ------------------------
    title="🕌 Tes Hafalan Al-Fatihah AI",
    description="Klik tombol rekam, baca ayat sesuai pilihan, lalu stop. AI akan mengecek bacaanmu.",
    theme="soft"
)

if __name__ == "__main__":
    interface.launch()