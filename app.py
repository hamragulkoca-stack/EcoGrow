import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- SAYFA YAPISI ---
st.set_page_config(page_title="EcoGrow: Art of ESG", layout="wide")
st.title("🌾 EcoGrow: Algoritmik İzlenimcilik ile Sürdürülebilir Tarım Simülasyonu")

# --- SESSİON STATE (Kalıcı Hasar / İyileşme Hafızası İçin) ---
if "prior_damage" not in st.session_state:
    st.session_state.prior_damage = 0.0

# --- SOL MENÜ: MULTİ-KRİTERLİ SENSÖR PANELİ ---
st.sidebar.header("🚜 Akıllı Sera ve Dikey Tarım Sensörleri")

soil_moisture = st.sidebar.slider("Toprak Nemi (%)", 10, 100, 70)
temperature = st.sidebar.slider("Sera Sıcaklığı (°C)", 10, 50, 24)
drought_hours = st.sidebar.slider("Kümülatif Susuz Geçen Süre (Saat)", 0, 48, 0)
light_intensity = st.sidebar.slider("Işık Yoğunluğu (Lux)", 0, 60000, 30000)

st.sidebar.write("---")
if st.sidebar.button("♻️ Kalıcı Hasarı Sıfırla (Toprağı Yenile)"):
    st.session_state.prior_damage = 0.0
    st.rerun()

# --- 🧠 MATEMATİKSEL MODELLEME VE OPTİMİZASYON MOTORU ---

# 1. Sıcaklık Cezası: 40°C kritik eşik. Sonrasında Kritik Çöküş
if temperature <= 40:
    temp_penalty = abs(temperature - 24) * 1.2
else:
    temp_penalty = (abs(40 - 24) * 1.2) + np.exp(temperature - 40) * 8

# 2. Susuzluk Cezası: Zaman ilerledikçe kümülatif (karesiyle orantılı) hasar
drought_penalty = (drought_hours ** 1.8) * 0.5

# 3. Işık Cezası: İdeal aralık 20k - 40k Lux. Azı fotosentezi durdurur, çoğu yakar.
if 20000 <= light_intensity <= 40000:
    light_penalty = 0
elif light_intensity < 20000:
    light_penalty = (20000 - light_intensity) * 0.0015
else:
    light_penalty = np.exp((light_intensity - 40000) / 5000) * 2

# 4. Kümülatif Hafıza ve İyileşme (Recovery) Mekanizması
total_instant_penalty = temp_penalty + drought_penalty + light_penalty

# Ağır hasar durumunda kalıcı hasar birikir, iyi koşullarda yavaşça iyileşir
if total_instant_penalty > 40:
    st.session_state.prior_damage = min(70.0, st.session_state.prior_damage + (total_instant_penalty * 0.02))
else:
    st.session_state.prior_damage = max(0.0, st.session_state.prior_damage - 1.5)

# Nihai Sistem Sağlığı Skoru (0 - 100)
system_health = max(0, min(100, int(100 - (total_instant_penalty + st.session_state.prior_damage))))

# --- 🎨 ALGORİTMİK İZLENİMCİLİK MOTORU (Sanat Akımları) ---
num_strokes = 4500  
t = np.linspace(0, 12 * np.pi, num_strokes)
kaos_factor = (100 - system_health) / 12

r = np.sqrt(t) + kaos_factor * np.random.randn(num_strokes)
x = r * np.cos(t)
y = r * np.sin(t)

# Dokümandaki Sanat Akımları ve Renk Paleti Eşleşmesi
if system_health >= 75:
    art_style = "Claude Monet (İzlenimcilik Modu)"
    cmap_choice = "YlGnBu"  # Pastel yeşiller, su mavileri
    line_alpha = 0.5        
    stroke_len_mod = 1.0    
elif 45 <= system_health < 75:
    art_style = "Paul Klee (Modern Soyutlama Modu)"
    cmap_choice = "viridis" # Geometrik, rasyonel ve kontrollü ritim tonları
    line_alpha = 0.6
    stroke_len_mod = 1.4
else:
    art_style = "Vincent van Gogh (Dışavurumculuk Modu)"
    cmap_choice = "hot"     # Kor kırmızısı, çiyan sarısı, agresif tonlar
    line_alpha = 0.8        
    stroke_len_mod = 2.5    

# Tuvali Oluşturma (Yağlı Boya Efekti)
fig, ax = plt.subplots(figsize=(10, 8), facecolor='black')
ax.set_facecolor('black')

colors = plt.get_cmap(cmap_choice)(np.linspace(0, 1, num_strokes))
angles = np.arctan2(y, x) + (np.pi / 2 if system_health < 45 else 0) 

for i in range(0, num_strokes, 3):  
    dx = np.cos(angles[i]) * (0.2 * stroke_len_mod)
    dy = np.sin(angles[i]) * (0.2 * stroke_len_mod)
    
    brightness = max(0.2, min(1.0, light_intensity / 30000)) if system_health >= 75 else 1.0
    
    ax.plot([x[i], x[i]+dx], [y[i], y[i]+dy], 
            c=colors[i], 
            alpha=line_alpha * brightness, 
            linewidth=1.2 + (kaos_factor * 0.1))

ax.axis('off')

# --- 🖥️ DASHBOARD VE EKRAN TASARIMI ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"### 🖼️ Aktif Akım: **{art_style}**")
    st.metric(label="📊 GENEL SİSTEM SAĞLIĞI", value=f"%{system_health}", 
              delta=f"-{int(st.session_state.prior_damage)} Birikmiş Geçmiş Hasar Etkisi", delta_color="inverse")
    
    st.write("---")
    st.write("#### 📐 Mühendislik ve Ceza Dağılımları:")
    st.progress(min(100, int(temp_penalty * 2)), text=f"🌡️ Termal Stres (Eksponansiyel): {int(temp_penalty)} Pts")
    st.progress(min(100, int(drought_penalty * 2)), text=f"💧 Kümülatif Kuraklık Hasarı: {int(drought_penalty)} Pts")
    st.progress(min(100, int(light_penalty * 2)), text=f"☀️ Işık/Fotosentez Dengesi: {int(light_penalty)} Pts")
    
    st.write("---")
    st.write("### 💼 KURUMSAL DEĞER ÖNERİSİ (B2B SaaS)")
    st.success(
        """• **EcoGrow**, endüstriyel tarım tesislerinin ve gıda holdinglerinin sürdürülebilirlik (ESG) verilerini canlı, yaşayan birer kurumsal sanat tablosuna dönüştürür.

• **SaaS Modeli:** Şirket lobilerindeki ruhsuz ekranlar yerine abonelik modeliyle (Data-Art-as-a-Service) kiralanır.
• **PR & Şeffaflık:** Şirketler yeşil dönüşüm başarılarını yatırımcılarına ve ziyaretçilerine soyut, büyüleyici bir sanat diliyle kanıtlar."""
    )

with col2:
    st.subheader("🎨 Dijital Tuval (Verinin Sanata Dönüşümü)")
    st.pyplot(fig)
    plt.close(fig) # Bellek sızıntısını önlemek için figürü kapatıyoruz
