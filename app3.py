import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import geocoder
import os
import tempfile

# 1. Configure Gemini API
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# 2. Language options
languages = {
    "English": "English",
    "Telugu": "తెలుగు",
    "Hindi": "हिंदी",
    "Tamil": "தமிழ்",
    "Kannada": "ಕನ್ನಡ"
}

# 3. Detect location-based language
def detect_location_language():
    try:
        location = geocoder.ip('me')
        region = location.state.lower()
        if 'andhra' in region or 'telangana' in region:
            return "Telugu"
        elif 'tamil' in region:
            return "Tamil"
        elif 'karnataka' in region:
            return "Kannada"
        elif 'uttar' in region or 'madhya' in region or 'bihar' in region:
            return "Hindi"
    except:
        pass
    return "English"

default_lang = detect_location_language()

# 4. UI Setup
st.title("🌿 Plant Disease Detector & Local Remedy Recommender")
st.write("Upload a leaf image to detect disease and get low-cost remedies in your local language.")

selected_language = st.selectbox("🌍 Select Language", list(languages.keys()),
                                 index=list(languages.keys()).index(default_lang))

# 5. Upload leaf image
uploaded_file = st.file_uploader("📷 Upload a leaf image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # 6. Create prompt
    prompt = f"""
You are a plant disease expert. Please respond only in {languages[selected_language]}.

Based on this leaf image:
1. Identify if it has a disease.
2. Name the disease if known.
3. Recommend low-cost fertilizers to improve the plant's health.
4. Recommend low-cost or natural pesticides for treatment or prevention.
"""

    with st.spinner("🔍 Analyzing the image..."):
        response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=[prompt, image]
)

result_text = response.text

    # 7. Display diagnosis
    st.subheader(f"🩺 Diagnosis & Treatment in {languages[selected_language]}")
    st.write(result_text)

    # 8. Voice Output
    st.subheader("🔊 Listen to the result")
    lang_code = {
        "Telugu": "te",
        "Hindi": "hi",
        "Tamil": "ta",
        "Kannada": "kn",
        "English": "en"
    }
    tts = gTTS(text=result_text, lang=lang_code[selected_language])
    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(temp_audio_path)
    st.audio(temp_audio_path, format="audio/mp3")

# 10. Cleanup audio
    os.unlink(temp_audio_path)
