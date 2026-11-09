import streamlit as st
import time
import os
from google import genai
from google.genai import types

# 1. Premium Mobile-Responsive Page Styling
st.set_page_config(
    page_title="Bloomberg-Style Intelligence Suite",
    page_icon="📈",
    layout="centered"
)

# Custom Title Header
st.title("📈 Macro Executive Intelligence App")
st.caption("Transforming raw multimedia and market text feeds into premium corporate newsletters.")

# 2. Sidebar Configurations for Mobile/Desktop Control
st.sidebar.header("🔑 Authentication & Styling")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("[Get a Free API Key from Google AI Studio](https://google.com)")

# Newsletter Style Selector Dropdown Widget
editorial_style = st.sidebar.selectbox(
    "Select Editorial Tone",
    ["Bloomberg Terminal (Ultra-Objective & Punchy)", "Financial Times (Analytical & Strategic Macro)"]
)

# 3. Create the Multimedia Submission Interface
st.subheader("📥 Data Ingestion Panel")
uploaded_video = st.file_uploader("Upload Market Update Video (.mp4, .mov)", type=["mp4", "mov"])
raw_text_articles = st.text_area("Or, paste raw corporate articles / transcripts here directly...", height=150)

# Main Processing Button Action
if st.button("🚀 Compile Newsletter Edition"):
    if not api_key:
        st.error("❌ Action Blocked: Please input your Gemini API Key in the left sidebar configuration panel.")
    elif not uploaded_video and not raw_text_articles:
        st.warning("⚠️ Ingestion Error: Please upload a market video file OR paste text data to continue.")
    else:
        # Create an animated user processing layout
        with st.status("Initializing AI Newsroom Engine...", expanded=True) as status:
            client = genai.Client(api_key=api_key)
            contents = []
            
            # Scenario A: User uploaded a video file
            if uploaded_video:
                status.write("🎬 Saving and routing multimedia file stream to Gemini cloud server...")
                temp_path = f"temp_{uploaded_video.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_video.getbuffer())
                
                video_cloud_file = client.files.upload(file=temp_path)
                
                # Monitor background file compilation status
                while video_cloud_file.state.name == "PROCESSING":
                    time.sleep(4)
                    video_cloud_file = client.files.get(name=video_cloud_file.name)
                
                if video_cloud_file.state.name == "FAILED":
                    status.update(label="Video Ingestion Failed!", state="error")
                    st.error("Cloud engine failed to analyze video structure.")
                    os.remove(temp_path)
                    st.stop()
                
                contents.append(video_cloud_file)
                contents.append("Summarize this video highlighting critical financial updates.")
                os.remove(temp_path)
            
            # Scenario B: User pasted raw textual reports instead
            elif raw_text_articles:
                status.write("📝 Parsing unstructured text reports...")
                contents.append(f"Analyze the following financial information:\n\n{raw_text_articles}")

            status.write("🧠 Executing professional editorial prompt guidelines...")
            
            # System instructions dynamically adjusted based on side dropdown selector menu
            if "Bloomberg" in editorial_style:
                system_prompt = (
                    "You are a Managing Editor at a Bloomberg Terminal newsroom. Create a crisp newsletter layout titled '█ BLOOMBERG PULSE'. "
                    "Use short, razor-sharp bullet points. Bold all company tickers, names, and precise figures (e.g., **AAPL**, **$1.2B**, **Fed**). "
                    "Maintain an absolute cold, analytical, and numbers-driven objective tone."
                )
            else:
                system_prompt = (
                    "You are a Senior Macro Strategist for the Financial Times. Create a strategic overview layout titled '█ MACRO STRATEGY BRIEF'. "
                    "Focus heavily on the structural impacts, market trends, and long-term economic implications. "
                    "Format cleanly with analytical headers and bold metrics."
                )

            # Fire request to the highly efficient Gemini 3.8 Flash model
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.25
                )
            )
            
            # Clean up cloud asset after reading to keep account secure
            if uploaded_video:
                client.files.delete(name=video_cloud_file.name)
                
            status.update(label="Newsletter Successfully Compiled!", state="complete", expanded=False)
            
        # 4. Render Layout Results on screen
        st.success("✨ Your Custom Financial Newsletter is Ready!")
        st.markdown("---")
        st.markdown(response.text)
        st.markdown("---")
