import streamlit as st
from groq import Groq

st.set_page_config(page_title="Faruk AI", page_icon="🤖")
st.title("🤖 Faruk AI")
st.caption("Işık Hızında Yapay Zeka Asistanınız")

# 1. API Key'i Streamlit Secrets'tan otomatik alıyoruz
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # Eğer Secrets tanımlı değilse yedek olarak sol menüden alır
    api_key = st.sidebar.text_input("Groq API Key Giriniz:", type="password")

if not api_key:
    st.info("Sistemde aktif bir API anahtarı bulunamadı. Lütfen yöneticinizle iletişime geçin.")
    st.stop()

# Groq istemcisi başlatılıyor
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
                # Groq'taki aktif tüm modelleri canlı çeker
                available_models = [m.id for m in client.models.list().data]
                usable_models = [m for m in available_models if "llama" in m or "qwen" in m]
                
                if not usable_models:
                    usable_models = available_models

                success = False
                last_error = ""

                for model_name in usable_models:
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
                    st.error(f"Aktif model bulunamadı: {last_error}")

            except Exception as main_e:
                st.error(f"Hata oluştu: {main_e}")
