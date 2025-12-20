# bilingual_flashcards_from_docx.py
import base64
import streamlit as st
from docx import Document
import re
from gtts import gTTS
import io

# 📂 Path to your text document
doc_path = "Flash Card Text.docx"

# 📖 Load text from Word document
def load_flashcards(doc_path):
    doc = Document(doc_path)
    flashcards = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:  # skip empty lines
            continue
        
        # Split by " : " (space-colon-space) to handle the format correctly
        parts = text.split(" : ")
        
        if len(parts) >= 3:
            # Extract just the phrase (remove "Student:" or "Teacher:" prefix)
            english_full = parts[0].strip()
            english = re.sub(r'^(Student|Teacher):\s*', '', english_full)
            
            # Extract Arabic text from [text] format
            arabic_raw = parts[1].strip()
            arabic_match = re.search(r'\[(.*?)\]', arabic_raw)
            arabic = arabic_match.group(1) if arabic_match else arabic_raw
            
            # Get transliteration
            translit = parts[2].strip()
            
            flashcards.append((english, arabic, translit))
    
    return flashcards

# 🚫 Remove emojis from text using regex
def remove_emojis(text):
    """Remove all emojis from text using regex"""
    # Unicode ranges for emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # Chinese characters and others
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# 🔊 Generate audio file from text (without emojis)
def text_to_speech(text, lang="en"):
    """Convert text to speech and return audio bytes"""
    try:
        # Remove emojis from text before converting to speech
        clean_text = remove_emojis(text)
        
        # Clean up extra spaces that might be left after removing emojis
        clean_text = ' '.join(clean_text.split())
        
        # If the text becomes empty after removing emojis, use a fallback
        if not clean_text.strip():
            if lang == "en":
                clean_text = "No text available"
            else:
                clean_text = "لا يوجد نص"
            
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

# 🎴 Display flashcards with voiceover
def show_flashcards(flashcards, reverse=False):
    st.title("📚 Bilingual Flashcards with Voiceover")
    st.write("🔹 Check the box below each card to reveal the translation and play sound.")
    
    for i, (english, arabic, translit) in enumerate(flashcards):
        with st.container():
            st.markdown('<div style="border:1px solid #ddd; padding:15px; border-radius:8px; margin-bottom:15px;">', unsafe_allow_html=True)
            
            if not reverse:
                # English → Arabic mode
                st.markdown(f"### 🔹 **{english}**")
                
                # English voice button
                col1, col2 = st.columns([1, 4])
                with col1:
                    voice_key = f"en_voice_{i}"
                    if st.button(f"🔊 English", key=voice_key):
                        audio_bytes = text_to_speech(english, lang="en")
                        if audio_bytes:
                            # Create a unique audio player for each button
                            audio_html = f"""
                            <audio autoplay="true" style="display:none;">
                            <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes.read()).decode()}" type="audio/mp3">
                            </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                            st.success("Playing English audio...")
                
                if st.checkbox("Show Arabic & Transliteration", key=f"en_ar_{i}"):
                    st.markdown(
                        f"""
                        <div style='text-align:right; direction:rtl; font-size:32px; color:#008000; font-weight:bold; margin-top:15px;'>{arabic}</div>
                        <div style='text-align:left; font-size:18px; font-style:italic; color:#555; margin-top:10px;'>Transliteration: {translit}</div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Arabic voice button
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        voice_key = f"ar_voice_{i}"
                        if st.button(f"🔊 Arabic", key=voice_key):
                            audio_bytes = text_to_speech(arabic, lang="ar")
                            if audio_bytes:
                                # Create a unique audio player for each button
                                audio_html = f"""
                                <audio autoplay="true" style="display:none;">
                                <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes.read()).decode()}" type="audio/mp3">
                                </audio>
                                """
                                st.markdown(audio_html, unsafe_allow_html=True)
                                st.success("Playing Arabic audio...")
            
            else:
                # Arabic → English mode
                st.markdown(
                    f"<div style='text-align:right; direction:rtl; font-size:32px; color:#000080; font-weight:bold;'>{arabic}</div>",
                    unsafe_allow_html=True
                )
                
                # Arabic voice button
                col1, col2 = st.columns([1, 4])
                with col1:
                    voice_key = f"ar_voice_first_{i}"
                    if st.button(f"🔊 Arabic", key=voice_key):
                        audio_bytes = text_to_speech(arabic, lang="ar")
                        if audio_bytes:
                            # Create a unique audio player for each button
                            audio_html = f"""
                            <audio autoplay="true" style="display:none;">
                            <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes.read()).decode()}" type="audio/mp3">
                            </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                            st.success("Playing Arabic audio...")
                
                if st.checkbox("Show English & Transliteration", key=f"ar_en_{i}"):
                    st.markdown(
                        f"""
                        <div style='text-align:left; font-size:28px; color:#008000; font-weight:bold; margin-top:15px;'>{english}</div>
                        <div style='text-align:left; font-size:18px; font-style:italic; color:#555; margin-top:10px;'>Transliteration: {translit}</div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # English voice button
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        voice_key = f"en_voice_second_{i}"
                        if st.button(f"🔊 English", key=voice_key):
                            audio_bytes = text_to_speech(english, lang="en")
                            if audio_bytes:
                                # Create a unique audio player for each button
                                audio_html = f"""
                                <audio autoplay="true" style="display:none;">
                                <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes.read()).decode()}" type="audio/mp3">
                                </audio>
                                """
                                st.markdown(audio_html, unsafe_allow_html=True)
                                st.success("Playing English audio...")
            
            st.markdown('</div>', unsafe_allow_html=True)

# 🚀 Run the app
if __name__ == "__main__":
    try:
        flashcards = load_flashcards(doc_path)
        
        if not flashcards:
            st.warning("⚠️ No flashcards loaded. Check document format.")
        else:
            st.success(f"✅ Loaded {len(flashcards)} flashcards with voiceover!")
            
            # Voiceover settings
            with st.expander("⚙️ Voice Settings"):
                st.info("Note: Voice synthesis uses Google Text-to-Speech (gTTS)")
                st.write("✅ Emojis are automatically removed from voice output")
                st.write("Example: 'Hello 👋' will speak as 'Hello'")
                st.write("English voice: Standard English TTS")
                st.write("Arabic voice: Standard Arabic TTS")
                st.write("Internet connection is required for voice generation.")
            
            # Preview first parsed card
            with st.expander("🔍 Preview first card with voice"):
                en, ar, tr = flashcards[0]
                st.text(f"English (display): {en}")
                st.text(f"English (for voice): {remove_emojis(en)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔊 Play English", key="preview_en"):
                        audio_bytes = text_to_speech(en, lang="en")
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                
                st.text(f"Arabic (display): {ar}")
                st.text(f"Arabic (for voice): {remove_emojis(ar)}")
                
                with col2:
                    if st.button("🔊 Play Arabic", key="preview_ar"):
                        audio_bytes = text_to_speech(ar, lang="ar")
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                
                st.text(f"Transliteration: {tr}")
        
        mode = st.radio("Choose mode:", ["English → Arabic", "Arabic → English"])
        reverse = mode == "Arabic → English"
        show_flashcards(flashcards, reverse=reverse)
        
    except FileNotFoundError:
        st.error(f"❌ File not found: `{doc_path}`")
        st.info("Update the `doc_path` variable with the correct path.")
    except Exception as e:
        st.error(f"❌ Error: {e}")