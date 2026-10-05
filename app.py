import streamlit as st
from groq import Groq

st.set_page_config(page_title="Faruk AI", page_icon="🤖")
st.title("🤖 Faruk AI")
st.caption("Işık Hızında Yapay Zeka Asistanınız")

# 1. API Key'i Streamlit Secrets'tan otomatik alıyoruz
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Groq API Key Giriniz:", type="password")

if not api_key:
    st.info("Sistemde aktif bir API anahtarı bulunamadı. Lütfen yöneticinizle iletişime geçin.")
    st.stop()

client = Groq(api_key=api_key.strip())

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Faruk AI'ya bir şey sorun..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Faruk AI düşünüyor..."):
            try:
                # Groq'taki aktif modelleri çekip sadece geçerli sohbet modellerini filtreliyoruz
                all_models = [m.id for m in client.models.list().data]
                
                # Sınıflandırma, guard, ses ve taslak modellerini ele, sadece ana sohbet modellerini tut
                chat_models = [
                    m for m in all_models 
                    if ("llama-3" in m or "qwen" in m) 
                    and not any(bad in m for bad in ["guard", "prompt", "classifier", "specdec", "whisper"])
                ]
                
                # Yedek liste: Öncelikli çalışmasını istediğimiz resmi sohbet modelleri
                fallback_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
                models_to_try = chat_models + [m for m in fallback_models if m not in chat_models]

                success = False
                last_error = ""

                for model_name in models_to_try:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Senin adın Faruk AI. Kullanıcılara her konuda yardımcı olan, samimi, zeki ve geniş bir genel kültüre sahip bir yapay zeka asistanısın. Sorulara detaylı ve Türkçe cevap ver."
                                },
                                *st.session_state.messages
                            ],
                            model=model_name,
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
                    st.error(f"Aktif sohbet modeli bulunamadı: {last_error}")

            except Exception as main_e:
                st.error(f"Hata oluştu: {main_e}")
