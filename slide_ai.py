import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import base64
from dotenv import load_dotenv
import os

st.set_page_config(layout="wide")

load_dotenv()

@st.cache_data
def get_octo_api_url():
    return os.getenv("OCTO_API_URL")

@st.cache_data
def get_octo_api_key():
    return os.getenv("OCTO_API_KEY")

OCTO_API_URL = get_octo_api_url()
OCTO_API_KEY = get_octo_api_key()

def generate_slides(query, additional_content="No content uploaded"):
    prompt = f"""Create a visually stunning and professional slide presentation on the topic: "{query}".
The presentation should include:
1. A title slide (add class="slide title-slide")
2. An agenda or overview slide (add class="slide content-slide")
3. 4-6 content slides with key points and brief explanations (add class="slide content-slide")
4. A conclusion slide (add class="slide conclusion-slide")

Format the slides using HTML and CSS. Each slide should have a unique, visually appealing background with shapes, gradients, or patterns.
Use a cohesive color scheme throughout the presentation, with vibrant accents and modern typography.
Ensure text is always readable against the background by using appropriate contrast and text shadows if necessary.
Include relevant SVG icons, charts, or illustrations to visualize concepts and enhance the overall design.

Slide structure:
<div class="slide [slide-type]">
    <div class="slide-background">
        <!-- Add SVG shapes, gradients, or patterns here for an interesting background -->
    </div>
    <div class="slide-content">
        <!-- Slide content goes here -->
    </div>
</div>

Additional content uploaded by user to incorporate: {additional_content}

Keep in mind the user input: {query}

Make each slide visually distinct while maintaining a cohesive theme. Use creative layouts, such as split screens, grids, or asymmetrical designs to make the content more engaging.
For content slides, use bullet points, short paragraphs, or infographic-style layouts to present information clearly and concisely.

IMPORTANT: Do not include any text like "Slide X:" or "**Slide X:" at the beginning of each slide. Do not use ```html or ``` markers. Simply provide the HTML content for each slide directly."""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTO_API_KEY}"
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "meta-llama-3-70b-instruct",
        "max_tokens": 3000,
        "presence_penalty": 0,
        "temperature": 0.7,
        "top_p": 1
    }

    response = requests.post(OCTO_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]['message']["content"]
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def generate_script(query, slides_content, additional_content=""):
    prompt = f"""Create an engaging and informative presentation script based on the following:

    Topic: {query}

    Slides Content:
    {slides_content}

    Additional Context:
    {additional_content}

    For each slide, provide a detailed script that:
    1. Introduces the slide's main topic
    2. Elaborates on key points
    3. Provides relevant examples or anecdotes
    4. Transitions smoothly to the next slide

    Format the script as follows:

    [Slide 1: Title]
    Script content for slide 1...

    [Slide 2: Title]
    Script content for slide 2...

    Continue for all slides. Aim for about 2-3 minutes of speaking time per slide. Use a conversational tone while maintaining professionalism.
    Incorporate the additional context where relevant to enrich the presentation.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTO_API_KEY}"
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "wizardlm-2-8x22b",
        "max_tokens": 3000,
        "presence_penalty": 0,
        "temperature": 0.7,
        "top_p": 1
    }

    response = requests.post(OCTO_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]['message']["content"]
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def create_slideshow(slides):
    slideshow_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        body {{
            font-family: 'Poppins', sans-serif;
            background-color: #f0f0f0;
            color: #333333;
        }}
        .slideshow-container {{
            max-width: 900px;
            height: 600px;
            position: relative;
            margin: auto;
            background-color: #ffffff;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .slide {{
            display: none;
            position: relative;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        .slide-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }}
        .slide-content {{
            position: relative;
            z-index: 2;
            padding: 40px;
            height: 100%;
            box-sizing: border-box;
            overflow-y: auto;
        }}
        .title-slide {{
            text-align: center;
        }}
        .title-slide h1 {{
            font-size: 3em;
            margin-bottom: 20px;
            color: #2c3e50;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        .content-slide h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        .slide h2 {{
            font-size: 1.8em;
            color: #3498db;
            margin-bottom: 15px;
        }}
        .slide ul, .slide ol {{
            margin-left: 25px;
            margin-bottom: 20px;
        }}
        .slide li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        .slide p {{
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        .prev, .next {{
            cursor: pointer;
            position: absolute;
            top: 50%;
            width: auto;
            margin-top: -30px;
            padding: 16px;
            color: white;
            font-weight: bold;
            font-size: 20px;
            border-radius: 0 3px 3px 0;
            user-select: none;
            background-color: rgba(0,0,0,0.3);
            transition: 0.3s ease;
            z-index: 3;
        }}
        .next {{
            right: 0;
            border-radius: 3px 0 0 3px;
        }}
        .prev:hover, .next:hover {{
            background-color: rgba(0,0,0,0.8);
        }}
    </style>
    <div class="slideshow-container">
        {slides}
        <a class="prev" onclick="plusSlides(-1)">&#10094;</a>
        <a class="next" onclick="plusSlides(1)">&#10095;</a>
    </div>
    <script>
        var slideIndex = 1;
        var slides = document.getElementsByClassName("slide");
        showSlides(slideIndex);

        function plusSlides(n) {{
            showSlides(slideIndex += n);
        }}

        function showSlides(n) {{
            if (n > slides.length) {{slideIndex = slides.length}}
            if (n < 1) {{slideIndex = 1}}
            for (var i = 0; i < slides.length; i++) {{
                slides[i].style.display = "none";
            }}
            slides[slideIndex-1].style.display = "block";
        }}
    </script>
    """
    return slideshow_html

def main():
    st.title("AI-Generated Slide Presentation")
    
    if 'slides_content' not in st.session_state:
        st.session_state.slides_content = None
    if 'script' not in st.session_state:
        st.session_state.script = None
    if 'script_index' not in st.session_state:
        st.session_state.script_index = 0
    
    query = st.text_area("Enter your presentation topic:")
    
    uploaded_files = st.file_uploader("Upload additional content (optional)", type=['txt', 'py'], accept_multiple_files=True)
    additional_content = ""
    if uploaded_files:
        for file in uploaded_files:
            additional_content += file.getvalue().decode("utf-8") + "\n\n"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Generate Presentation"):
            with st.spinner("Generating slides..."):
                generated_html = generate_slides(query, additional_content)
                
                if generated_html:
                    st.session_state.slides_content = generated_html
                    slideshow = create_slideshow(generated_html)
                    st.components.v1.html(slideshow, height=650, scrolling=True)
                    
                    # Provide download option
                    b64 = base64.b64encode(generated_html.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="presentation.html">Download HTML</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("Failed to generate slides. Please try again.")
        
        if st.session_state.slides_content:
            st.markdown("### Current Presentation")
            slideshow = create_slideshow(st.session_state.slides_content)
            st.components.v1.html(slideshow, height=650, scrolling=True)
    
    with col2:
        if st.button("Generate Script"):
            if st.session_state.slides_content:
                with st.spinner("Generating script..."):
                    script = generate_script(query, st.session_state.slides_content, additional_content)
                    if script:
                        st.session_state.script = script
                        st.session_state.script_index = 0
                        st.success("Script generated successfully!")
                    else:
                        st.error("Failed to generate script. Please try again.")
            else:
                st.warning("Please generate slides first.")
        
        if st.session_state.script:
            st.markdown("### Presentation Script")
            script_parts = st.session_state.script.split('[Slide')
            
            # Display current slide script
            if script_parts:
                current_part = script_parts[st.session_state.script_index + 1]
                title = current_part.split(']', 1)[0].strip()
                content = current_part.split(']', 1)[1].strip()
                st.subheader(f"Slide {st.session_state.script_index + 1}: {title}")
                st.markdown(content)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous Slide") and st.session_state.script_index > 0:
                    st.session_state.script_index -= 1
            with col2:
                if st.button("Next Slide") and st.session_state.script_index < len(script_parts) - 2:
                    st.session_state.script_index += 1

if __name__ == "__main__":
    main()