import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from gtts import gTTS
import urllib.parse
import os
import uuid

# 🔍 Suggest YouTube video search link based on ingredients
def get_ingredient_based_video_search_link(ingredients):
    keywords = ["chicken", "mutton", "egg", "fish", "prawns", "paneer", "potato", "rice", "tomato", "spinach"]
    search_terms = []

    lower_ingredients = [ing.lower() for ing in ingredients]

    for kw in keywords:
        if any(kw in ing for ing in lower_ingredients):
            search_terms.append(kw)

    if not search_terms:
        search_terms.append("vegetarian curry")

    query = " ".join(search_terms) + " recipe"
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"

# API Key
groq_api_key = "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"

# Groq + LLaMA setup
llm = ChatGroq(api_key=groq_api_key, model_name="llama3-70b-8192")
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

# Streamlit page config
st.set_page_config(page_title="AI Recipe Generator 🍽", page_icon="🥘")
st.title("🧠 AI Recipe Generator")
st.write("Choose your ingredients from the categories below:")

# Ingredient categories
spices = ["Turmeric", "Cumin seeds", "Mustard seeds", "Coriander powder", "Garam masala", "Red chili powder",
          "Black pepper", "Fennel seeds", "Cardamom", "Cloves", "Cinnamon", "Nutmeg", "Asafoetida (hing)",
          "Curry leaves", "Bay leaves", "Fenugreek seeds", "Caraway seeds (shah jeera)", "Star anise",
          "Saffron", "Paprika", "Oregano", "Basil (dried)", "Thyme", "Rosemary", "Chaat masala",
          "Amchur powder (dry mango)", "Ajwain (carom seeds)", "Rock salt / Black salt", "Ginger",
          "Garlic", "Onion powder", "Tamarind", "Vinegar", "Soy sauce", "Tomato ketchup", "Mustard sauce"]

vegetables = ["Tomato", "Onion", "Potato", "Carrot", "Beetroot", "Cauliflower", "Broccoli", "Cabbage", "Spinach",
              "Green peas", "French beans", "Bottle gourd (lauki)", "Ridge gourd (turai)", "Bitter gourd (karela)",
              "Pumpkin", "Brinjal (eggplant)", "Capsicum (bell pepper)", "Chillies (green/red)", "Lady’s finger (okra/bhindi)",
              "Radish", "Corn", "Mushrooms", "Spring onion", "Zucchini", "Turnip", "Leek", "Kale", "Lettuce", "Cucumber"]

fruits = ["Apple", "Banana", "Orange", "Mango", "Pineapple", "Grapes", "Watermelon", "Papaya", "Pomegranate",
          "Strawberry", "Blueberry", "Raspberry", "Kiwi", "Guava", "Pear", "Chikoo (sapodilla)", "Custard apple",
          "Dragon fruit", "Avocado", "Lychee", "Plum", "Coconut", "Dates", "Fig"]

non_veg = ["Chicken (breast, thighs, wings, drumsticks)", "Egg (boiled, scrambled, fried)", "Mutton (goat/lamb)",
           "Fish (salmon, tilapia, rohu, sardine)", "Prawns / Shrimp", "Crab", "Lobster", "Squid",
           "Duck", "Pork", "Beef", "Turkey", "Bacon", "Sausage", "Ham"]

# UI for selection
def multi_select_buttons(label, items):
    st.markdown(f"### {label}")
    cols = st.columns(3)
    selected = []
    for i, item in enumerate(items):
        if cols[i % 3].checkbox(item):
            selected.append(item)
    return selected

selected_spices = multi_select_buttons("🌶 Spices & Condiments", spices)
selected_veggies = multi_select_buttons("🥕 Vegetables", vegetables)
selected_fruits = multi_select_buttons("🍎 Fruits", fruits)
selected_nonveg = multi_select_buttons("🍗 Non-Veg Items", non_veg)

selected_ingredients = selected_spices + selected_veggies + selected_fruits + selected_nonveg

# Generate recipe
if st.button("🍳 Generate Recipe"):
    if not selected_ingredients:
        st.warning("Please select at least one ingredient.")
    else:
        user_input = ", ".join(selected_ingredients)
        prompt = (
            f"You are a helpful AI chef. Given the ingredients: {user_input}, "
            "generate a creative recipe name, list of ingredients with quantities, and detailed step-by-step instructions."
        )

        with st.spinner("Generating your recipe..."):
            try:
                response = conversation.predict(input=prompt)

                if response and isinstance(response, str):
                    st.success("Here's your recipe!")
                    st.markdown(response)

                    recipe_title = response.split("\n")[0].strip().replace("Recipe Title:", "")
                    st.subheader("🍽 Recipe Title:")
                    st.write(recipe_title)

                    # 👂 Generate TTS audio from the recipe using gTTS
                    st.subheader("🔊 Listen to Recipe:")
                    tts = gTTS(text=response, lang='en')
                    audio_path = f"recipe_audio_{uuid.uuid4().hex}.mp3"
                    tts.save(audio_path)
                    
                    audio_file = open(audio_path, 'rb')
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format='audio/mp3')

                    st.subheader("🔗 YouTube Search Link:")
                    video_url = get_ingredient_based_video_search_link(selected_ingredients)
                    st.markdown(f"[Click to find related videos 🍿]({video_url})", unsafe_allow_html=True)

                    # Clean up temp file after
                    audio_file.close()
                    os.remove(audio_path)

                else:
                    st.warning("Failed to generate a proper recipe response.")

            except Exception as e:
                st.error(f"Error: {e}")
