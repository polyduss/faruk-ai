import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import pypdf

st.set_page_config(page_title="Faruk AI", page_icon="🤖", layout="wide")
st.title("🤖 Faruk AI")
st.caption("Işık Hızında Yapay Zeka Asistanınız")

# 1. API Key kontrolü
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Groq API Key Giriniz:", type="password")

if not api_key:
    st.info("Sistemde aktif bir API anahtarı bulunamadı. Lütfen yöneticinizle iletişime geçin.")
    st.stop()

client = Groq(api_key=api_key.strip())

# Session state başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOL MENÜ (AYARLAR VE KONTROLLER) ---
with st.sidebar:
    st.header("⚙️ Faruk AI Ayarları")
    
    # Yapay Zeka Özelleştirmeleri
    system_prompt = st.text_area(
        "Sistem Talimatı (Kişilik)",
        value="Senin adın Faruk AI. Kullanıcılara her konuda yardımcı olan, samimi, zeki ve geniş bir genel kültüre sahip bir yapay zeka asistanısın. Sorulara detaylı ve Türkçe cevap ver.",
        help="Faruk AI'nın rolünü buradan değiştirebilirsiniz."
    )
    
    temperature = st.slider(
        "Sıcaklık / Yaratıcılık (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Düşük değerler mantıksal/kesin, yüksek değerler yaratıcı yanıtlar verir."
    )
    
    # Web Arama Modu
    enable_web_search = st.toggle("🌐 Web Arama Modu", value=False, help="Güncel haberler ve maç sonuçları için internette arama yapar.")
    
    st.divider()
    
    # Sohbet Yönetimi
    st.subheader("💬 Sohbet Yönetimi")
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    if st.session_state.messages:
        chat_history_md = "# Faruk AI - Sohbet Geçmişi\n\n"
        for msg in st.session_state.messages:
            role = "Kullanıcı" if msg["role"] == "user" else "Faruk AI"
            chat_history_md += f"### {role}:\n{msg['content']}\n\n---\n\n"
            
        st.download_button(
            label="📥 Sohbeti İndir (.md)",
            data=chat_history_md,
            file_name="faruk_ai_sohbet.md",
            mime="text/markdown",
            use_container_width=True
        )

# --- ANA EKRAN: DOSYA / PDF YÜKLEME ---
with st.expander("📁 PDF veya Metin Dosyası Yükle (Ödev/Ders Notu)"):
    uploaded_file = st.file_uploader("Dosya seçin:", type=["pdf", "txt"])
    file_context = ""
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        file_context += text + "\n"
                st.success(f"✅ '{uploaded_file.name}' okundu!")
            elif uploaded_file.name.endswith(".txt"):
                file_context = uploaded_file.read().decode("utf-8")
                st.success(f"✅ '{uploaded_file.name}' okundu!")
        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")

# --- HOŞ GELDİN MESAJLARI (QUICK PROMPTS) ---
if not st.session_state.messages:
    st.markdown("### 💡 Hızlı Başlangıç")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("📐 Matematik ödevime yardım et", use_container_width=True):
        st.session_state.prompt_input = "Matematik ödevime yardım etmeni istiyorum. Adım adım açıklar mısın?"
    if col2.button("📜 Tarih özeti çıkar", use_container_width=True):
        st.session_state.prompt_input = "Bana önemli bir tarih konusunun kısa ve anlaşılır bir özetini çıkar."
    if col3.button("⚽ Güncel Maç Sonuçları", use_container_width=True):
        st.session_state.prompt_input = "Son oynanan Fenerbahçe maçının sonucunu ve özetini söyle."

# Geçmiş mesajları ekrana yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girdisi alma
prompt = st.chat_input("Faruk AI'ya bir şey sorun...")

if "prompt_input" in st.session_state and st.session_state.prompt_input:
    prompt = st.session_state.prompt_input
    del st.session_state.prompt_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Faruk AI düşünüyor..."):
            try:
                # Web Arama Entegrasyonu (Güncellenmiş Güvenli Fonksiyon)
                search_results = ""
                if enable_web_search:
                    try:
                        with DDGS() as ddgs:
                            results = list(ddgs.text(prompt, max_results=3))
                            if results:
                                search_results = "\n".join([f"- {r.get('title', '')}: {r.get('body', '')}" for r in results])
                    except Exception as se:
                        st.sidebar.warning(f"Arama modunda geçici sorun: {se}")

                # Ekstra bağlamları birleştirme
                extra_info = ""
                if 'file_context' in locals() and file_context:
                    extra_info += f"\n\n[YÜKLENEN DOSYA İÇERİĞİ]:\n{file_context}"
                if search_results:
                    extra_info += f"\n\n[GÜNCEL İNTERNET ARAMA SONUÇLARI]:\n{search_results}"

                # Mesaj geçmişini hazırlama
                formatted_messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages[:-1]:
                    formatted_messages.append({"role": m["role"], "content": m["content"]})
                
                final_user_content = prompt + extra_info
                formatted_messages.append({"role": "user", "content": final_user_content})

                # Groq Modellerini Çekme ve Çalıştırma
                all_models = [m.id for m in client.models.list().data]
                candidate_models = [
                    m for m in all_models 
                    if not any(bad in m.lower() for bad in ["guard", "whisper", "vision", "prompt", "classifier", "specdec"])
                ]

                success = False
                last_error = ""

                for model_name in candidate_models:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=formatted_messages,
                            model=model_name,
                            temperature=temperature
                        )
                        answer = chat_completion.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        success = True
                        break
                    except Exception as e:
                        last_error = str(e)
                        continue

                if not success:
                    st.error(f"Yanıt üretilemedi: {last_error}")

            except Exception as main_e:
                st.error(f"Hata oluştu: {main_e}")
