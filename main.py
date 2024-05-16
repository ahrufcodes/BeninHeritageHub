import streamlit as st
import os
import openai
import srt
from dotenv import load_dotenv
from io import StringIO
import time

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# UI Configuration
st.set_page_config(page_title="BHH", page_icon="🌟")

# Function for App 1: Img and Story Generator
def app1():
    st.image('img/banner.png', use_column_width=True)
    st.title("Visualizing Benin, One Story at a Time")
    st.write("""
     
- **Generate stunning images** based on cultural descriptions in English, Yoruba, and French.
- **Translate subtitles** seamlessly to and from Yoruba for your videos.
- **Immerse yourself** in captivating stories and visual narratives that celebrate our traditions and history.
    """)
    st.audio("bhh.mp3", format="audio/mp3", autoplay=True)

    # Dropdown for cultural themes
    themes = ["Traditional Attire", "Festivals", "Folklore", "History", "Art and craft", "Cuisine" ]
    selected_theme = st.selectbox("Choose a cultural theme", themes)
    
    Image_description = st.text_input("Enter a text to generate an image In Yoruba, English & French", key="img_desc")

    if st.button('Generate Image and Story'):
        if Image_description:
            translated_text = translate_to_yoruba(Image_description)
            st.write(f"Translated to Yoruba: {translated_text}")
            image_prompt = f"{selected_theme}: {Image_description}"  # Theme inclusion in image prompt
            image_url = generate_image(image_prompt)
            st.image(image_url)
            story_concepts = generate_short_story(translated_text)
            st.subheader("Short Story Concept")

            with st.expander("Yoruba"):
                st.write(story_concepts["Yoruba"])

            with st.expander("English"):
                st.write(story_concepts["English"])

            with st.expander("French"):
                st.write(story_concepts["French"])
            
            # Feedback section
            st.subheader("Your Feedback")
            feedback = st.text_area("Please provide your feedback on the generated content.")
            if st.button("Submit Feedback"):
                st.success("Thank you for your feedback!")
        else:
            st.error("Please enter a description to generate an image.")

def translate_to_yoruba(text):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a bilingual AI proficient in Yoruba and French languages. You will translate text based on its original language: from English to Yoruba and French, and from Yoruba or French to English. Maintain the linguistic and cultural nuances in your translations."},
            {"role": "user", "content": f"Translate the following text: '{text}'\n\nInstructions:\n- If the text is in English, translate it to both Yoruba and French.\n- If the text is in Yoruba or French, translate it to English."}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    translation = response.choices[0].message.content.strip()
    return translation

def generate_short_story(translated_text):
    response_yoruba = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative writer from the Benin Republic who specializes in writing short story concepts to captivate tourists and preserve cultural heritage. You write the stories in Yoruba, maintaining linguistic accuracy and including necessary signs in Yoruba."},
            {"role": "user", "content": f"Create a short story concept based on the following text: '{translated_text}' in Yoruba."}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    story_yoruba = response_yoruba.choices[0].message.content.strip()

    response_english = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative writer from the Benin Republic who specializes in writing short story concepts to captivate tourists and preserve cultural heritage. You write the stories in English, maintaining linguistic accuracy."},
            {"role": "user", "content": f"Create a short story concept based on the following text: '{translated_text}' in English."}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    story_english = response_english.choices[0].message.content.strip()

    response_french = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative writer from the Benin Republic who specializes in writing short story concepts to captivate tourists and preserve cultural heritage. You write the stories in French, maintaining linguistic accuracy."},
            {"role": "user", "content": f"Create a short story concept based on the following text: '{translated_text}' in French."}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    story_french = response_french.choices[0].message.content.strip()

    # Added cultural insights or educational content
    cultural_insights = "This story highlights the significance of traditional Yoruba festivals, showcasing their rich heritage and cultural values."
    
    return {
        "Yoruba": f"{story_yoruba}\n\nCultural Insights: {cultural_insights}",
        "English": f"{story_english}\n\nCultural Insights: {cultural_insights}",
        "French": f"{story_french}\n\nCultural Insights: {cultural_insights}"
    }

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    return image_url

# Function for App 2: SRT Translator
def app2():
    st.title('SRT File Translator to Yoruba or Fon')
    st.image('img/srt.png', use_column_width=True)

    # Language selection
    languages = ["Yoruba", "Fon"]
    selected_language = st.selectbox("Choose a language you want the subtitle to be translated to", languages, key="language_select")

    def translate_to_language_batch(texts, target_language):
        joined_texts = "\n\n".join(texts)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"You are a {target_language} AI that translates English text into {target_language}."},
                {"role": "user", "content": f"Translate the following texts to {target_language}:\n\n{joined_texts}"}
            ],
            temperature=1,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        translations = response.choices[0].message.content.strip().split("\n\n")
        return translations

    def translate_srt(file, target_language):
        srt_content = file.read().decode('utf-8')
        subtitles = list(srt.parse(srt_content))

        texts_to_translate = [subtitle.content for subtitle in subtitles]
        batch_size = 40  # batch size No, helps with the number of APi call done at a time
        translated_texts = []

        # Initialize progress bar
        progress_bar = st.progress(0)
        total_batches = (len(texts_to_translate) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts_to_translate), batch_size):
            batch_texts = texts_to_translate[i:i + batch_size]
            translated_texts.extend(translate_to_language_batch(batch_texts, target_language))
            progress_bar.progress(min((i + batch_size) / len(texts_to_translate), 1.0))

        translated_subtitles = []
        for subtitle, translated_text in zip(subtitles, translated_texts):
            translated_subtitle = srt.Subtitle(
                index=subtitle.index,
                start=subtitle.start,
                end=subtitle.end,
                content=translated_text
            )
            translated_subtitles.append(translated_subtitle)

        translated_srt_content = srt.compose(translated_subtitles)
        return translated_srt_content

    uploaded_file = st.file_uploader("Choose an SUBTITLE file to translate", type="srt")

    if uploaded_file is not None:
        with st.spinner(f"A moment Please, we're translating your subtitle for you to enjoy your movie..."):
            start_time = time.time()
            translated_srt_content = translate_srt(uploaded_file, selected_language)
            end_time = time.time()
            st.success(f'Yay! Translation completed in {end_time - start_time:.2f} seconds')

        st.download_button(
            label="Download Translated SRT",
            data=translated_srt_content,
            file_name=f"translated_{selected_language.lower()}.srt",
            mime="text/srt"
        )

# Main function to combine both apps
def main():
    st.sidebar.title('Navbar')
    app_choice = st.sidebar.radio('Go to', ['Generate Image and Story', 'Subtitle Translator'])

    if app_choice == 'Generate Image and Story':
        app1()
    elif app_choice == 'Subtitle Translator':
        app2()

if __name__ == '__main__':
    main()
