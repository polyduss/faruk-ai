import streamlit as st
from groq import Groq

st.set_page_config(page_title="Faruk AI", page_icon="🤖")
st.title("🤖 Faruk AI")
st.caption("Işık Hızında Yapay Zeka Asistanınız")

# 1. API Key'i Streamlit Secrets'tan alıyoruz
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
                # Groq'un en güncel ve kararlı çalışan ana sohbet modelleri
                preferred_models = [
                    "llama-3.3-70b-versatile",
                    "llama3-8b-8192",
                    "llama3-70b-8192",
                    "mixtral-8x7b-32768"
                ]

                # Canlı modeller arasından da sohbet için uygun olanları ek yedek olarak alıyoruz
                try:
                    all_fetched = [m.id for m in client.models.list().data]
                    extra_models = [
                        m for m in all_fetched 
                        if "llama" in m and not any(bad in m for bad in ["guard", "prompt", "classifier", "specdec", "whisper", "vision"])
                    ]
                except Exception:
                    extra_models = []

                # Öncelikli modeller ilk sırada denenir
                models_to_try = preferred_models + [m for m in extra_models if m not in preferred_models]

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
