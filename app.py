import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

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
num_strokes = 6000  # Akıcı ve yoğun bir görsellik için optimize edildi
t = np.linspace(0, 16 * np.pi, num_strokes)

# Sistem sağlığına göre geometrik kaos katsayısı
kaos_factor = (100 - system_health) / 12

# Girdap denklemi (Van Gogh / Monet geçiş altyapısı)
r = np.sqrt(t) + kaos_factor * np.random.randn(num_strokes)
x = r * np.cos(t)
y = r * np.sin(t)

# Sanat Akımı ve Renk Paleti Belirleme
if system_health >= 75:
    art_style = "Claude Monet (İzlenimcilik Modu)" 
    cmap_choice = "YlGnBu"  # Pastel yeşiller, su mavileri 
    line_alpha = 0.6        
    stroke_len_mod = 1.2    
elif 45 <= system_health < 75:
    art_style = "Paul Klee (Modern Soyutlama Modu)" 
    cmap_choice = "viridis" # Kontrollü ritim tonları 
    line_alpha = 0.7
    stroke_len_mod = 1.6
else:
    art_style = "Vincent van Gogh (Dışavurumculuk Modu)" 
    cmap_choice = "hot"     # Kor kırmızısı, çiyan sarısı 
    line_alpha = 0.9        
    stroke_len_mod = 3.0    

# Tuvali Oluşturma (Yağlı Boya Efekti)
fig, ax = plt.subplots(figsize=(10, 8), facecolor='black')
ax.set_facecolor('black')

colors = plt.get_cmap(cmap_choice)(np.linspace(0, 1, num_strokes))
angles = np.arctan2(y, x) + (np.pi / 2 if system_health < 45 else 0) 

# Performans için LineCollection yapısına geçildi (Hızlı Çizim Sağlar)
segments = []
line_colors = []
alphas = []

for i in range(num_strokes):  
    dx = np.cos(angles[i]) * (0.2 * stroke_len_mod)
    dy = np.sin(angles[i]) * (0.2 * stroke_len_mod)
    
    segments.append([(x[i], y[i]), (x[i]+dx, y[i]+dy)])
    line_colors.append(colors[i])
    
    brightness = max(0.3, min(1.0, light_intensity / 30000)) if system_health >= 75 else 1.0
    alphas.append(line_alpha * brightness)

lc = LineCollection(segments, colors=line_colors, linewidths=1.5 + (kaos_factor * 0.15))
lc.set_alpha(alphas)
ax.add_collection(lc)

ax.autoscale()
ax.axis('off')

# --- 🖥️ DASHBOARD VE EKRAN TASARIMI ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"### 🖼️ Aktif Akım: **{art_style}**")
    st.metric(label="📊 GENEL SİSTEM SAĞLIĞI", value=f"%{system_health}", 
              delta=f"-{int(st.session_state.prior_damage)} Birikmiş Geçmiş Hasar Etkisi", delta_color="inverse")
    
    st.write("---")
    st.write("#### 🧠 Ekosistem Hafızası ve Stres Faktörleri:")
    st.progress(min(100, int(temp_penalty * 2)), text=f"🌡️ Termal Stres (Eksponansiyel): {int(temp_penalty)} Pts")
    st.progress(min(100, int(drought_penalty * 2)), text=f"💧 Kümülatif Kuraklık Hasarı: {int(drought_penalty)} Pts")
    st.progress(min(100, int(light_penalty * 2)), text=f"☀️ Işık/Fotosentez Dengesi: {int(light_penalty)} Pts")
    
    st.write("---")
    st.write("### 💼 KURUMSAL VİZYON VE DEĞER ÖNERİSİ")
    st.success(
        """• **EcoGrow:** Endüstriyel seralar ve gıda holdingleri için karmaşık tarım verilerini lobi ve ofislerde sergilenebilecek canlı bir veri sanatına dönüştürür[cite: 5, 19, 20].

• **Kurumsal Prestij:** Şirketlerin çevre dostu ve sürdürülebilirlik vizyonlarını herkesin anlayacağı estetik bir sanat diliyle kanıtlar.

• **PR & Şeffaflık:** Yeşil dönüşüm başarılarını yatırımcılara ve dış ziyaretçilere ruhsuz tablolar yerine büyüleyici bir dijital tuvalle sunar.

• **Kaynak Optimizasyonu:** Ön plandaki bu estetik prestijin arkasında, tarla verimini artıran ve kaynakları optimize eden hassas bir analiz motoru çalışır."""
    )
    st.write("---")
    st.write("### 📜 FELSEFİ ALTYAPI & TEMATİK BAĞLAM")
    st.info(
        """EcoGrow, yapay zekayı ve tarımsal veriyi sadece teknik bir vizyonla değil, insanlığın en temel üç temasıyla harmanlar:

• ❤️ **AŞK (Claude Monet):** Sensörler ideal değerlerdeyken ortaya çıkan yumuşak fırça darbeleri, insanın doğaya, toprağa ve üretime duyduğu o saf aşkı ve uyumu simgeler.

• 💀 **ÖLÜM (Vincent van Gogh):** Kuraklık, yüksek sıcaklık ve kriz anlarında devreye giren agresif girdaplar ve kor renkler; tarlanın, bitkinin ve ekosistemin dijital çığlığını, yani kaçınılmaz ölümü temsil eder.

• 🇹🇷 **VATAN (Kurumsal Sürdürülebilirlik):** Tüm bu sanatsal ve matematiksel döngü, üzerinde yaşadığımız ve beslendiğimiz toprağı, yani vatanı koruma, kaynakları optimize etme ve geleceğe sürdürülebilir bir yurt bırakma felsefesine dayanır."""
    )
# TUVALİ SAĞ SÜTUNA ÇİZEN BLOK
with col2:
    st.subheader("🎨 Dijital Tuval (Verinin Sanata Dönüşümü)") 
    st.pyplot(fig)
    plt.close(fig)
