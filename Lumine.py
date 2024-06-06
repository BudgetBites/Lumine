import streamlit as st
import requests
import pandas as pd
import time
import os

# =============================================================================
# Spoonacular API Configuration
# =============================================================================

# Add FontAwesome CSS for icons
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)

# Function to get recipes based on user input
def get_recipes(params, api_key):
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    headers = {'Content-Type': 'application/json'}
    params['apiKey'] = api_key
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Function to get recipe details
def get_recipe_details(recipe_id, api_key):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'apiKey': api_key,
        'includeNutrition': True
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to get meal types
def get_meal_types():
    return ['Breakfast', 'Lunch', 'Dinner']

# Function to call Spoonacular Image Analysis API
def analyze_image(image_path, api_key):
    url = "https://api.spoonacular.com/food/images/analyze"
    files = {'file': open(image_path, 'rb')}
    params = {'apiKey': api_key}
    response = requests.post(url, files=files, params=params)
    return response.json()

# Function to get similar recipes
def get_similar_recipes(recipe_id, api_key):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/similar'
    params = {
        'apiKey': api_key,
        'number': 5  # Number of similar recipes to fetch
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to save favorite recipes
def save_favorite(recipe_id):
    favorites = st.session_state.get('favorites', [])
    if recipe_id not in favorites:
        favorites.append(recipe_id)
    st.session_state['favorites'] = favorites

# Function to get favorite recipes
def get_favorites(api_key):
    favorites = st.session_state.get('favorites', [])
    favorite_recipes = []
    for recipe_id in favorites:
        recipe_details = get_recipe_details(recipe_id, api_key)
        favorite_recipes.append(recipe_details)
    return favorite_recipes

# Function to remove favorite recipes
def remove_favorite(recipe_id):
    favorites = st.session_state.get('favorites', [])
    if recipe_id in favorites:
        favorites.remove(recipe_id)
    st.session_state['favorites'] = favorites

# Function to generate grocery list
def generate_grocery_list(recipes):
    grocery_list = {}
    for recipe in recipes:
        for ingredient in recipe['extendedIngredients']:
            name = ingredient['name']
            amount = ingredient['amount']
            unit = ingredient['unit']
            if name in grocery_list:
                grocery_list[name]['amount'] += amount
            else:
                grocery_list[name] = {'amount': amount, 'unit': unit}
    return grocery_list

# Function to convert USD to EUR (static conversion rate for simplicity)
def convert_usd_to_eur(usd):
    conversion_rate = 0.85  # Example conversion rate, should be updated with real-time data
    return usd * conversion_rate

# Function to check API key validity and quota
def check_api_key(api_key):
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    params = {'apiKey': api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        headers = response.headers
        quota_used = headers.get('x-api-quota-used', 0)
        quota_remaining = headers.get('x-api-quota-remaining', 150)
        if int(quota_remaining) == 0:
            return False, "You have reached your daily quota limit. Please upgrade to premium or try again tomorrow."
        return True, None
    else:
        return False, "The API key is not correct. Please follow the instructions to obtain a valid API key."

# =============================================================================
# Streamlit Interface Setup
# =============================================================================

# Initial pop-up for API key entry
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

if st.session_state.api_key is None:
    st.markdown("<h1 style='text-align: center;'>Welcome to Lumine🌟</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Before we start, let's get your Secret Ingredient! 🥄</h3>", unsafe_allow_html=True)
    st.write("""
        To start your culinary adventure, follow these steps to get your secret ingredient (API Key):

        1. 🍽️ Visit the [Spoonacular Website](https://spoonacular.com/food-api).
        2. 🍳 Click on "Start" in the top right corner.
        3. 📝 Sign up using your email and password.
        4. 📧 Check your email inbox and verify your account.
        5. 🔑 Log in to Spoonacular.
        6. 👤 Navigate to your profile, click "Show / Hide API key", copy your key, and paste it below.

        Let's get cooking!
    """)
    api_key = st.text_input("🔒 Enter your Secret Ingredient (API Key):", type="password")
    if st.button("Whisk it up!"):
        valid, message = check_api_key(api_key)
        if valid:
            st.session_state.api_key = api_key
            st.success("API key is valid. You can now use the application. 🍀")
            st.experimental_rerun()
        else:
            st.error("Oops! The Secret Ingredient (API Key) might be incorrect, or you've stirred up too many requests today. Please double-check your key or try again tomorrow. 🍲")
            st.markdown("""
                ### API Quota Information 🔑

                It looks like you might have reached your daily quota or entered an incorrect API key. To keep the culinary magic going, you have a few options:

                1. 🛒 **Upgrade Your Plan:** Head over to the [Spoonacular API Pricing](https://spoonacular.com/food-api/pricing) page and choose a plan that suits your cooking style. Options include Free, Cook, Culinarian, Chef, and Enterprise.
                2. 🌟 **Patience is a Virtue:** Continue with the free plan tomorrow without changing your API key. Sometimes, great recipes are worth the wait!
                3. 📝 **Start Fresh:** Create a new account and follow the API key setup steps again. A fresh start can lead to new culinary adventures!
            """)
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0;">
            <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    api_key = st.session_state.api_key

    st.markdown("<h1 style='text-align: center;'>Lumine🌟</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Your Culinary Adventure Awaits🍽️</h2>", unsafe_allow_html=True)

    # Creating tabs with names and icons
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Recipe Wizard 🧙‍♂️",
        "Chef's Favorites ❤️",
        "Magic Grocery List 🛒",
        "Meal Master Planner 📅",
        "Budget Bites 🍩",
        "Food Selfie Classifier 📸"
    ])

    # =============================================================================
    # Recipe Wizard Tab
    # =============================================================================
    with tab1:
        st.header("Welcome to the Lumine Recipe Wizard!")
        st.write("""
            Here in the Wizard's kitchen, you can pick your favorite ingredients and the maximum prep time to conjure up recipes that fit your taste and schedule. Enter your ingredients and cooking time, then click "Let's Spice Things Up" to discover magical recipes. Save your favorite dishes by clicking the heart ❤️ icon.
        """)
        # User input fields for recipes
        st.write("### Select Your Culinary Preferences")
        st.write("Specify the ingredients you have or want to use, separated by commas. For example: chicken, tomato, basil. 🐔🍅🌿")
        selected_ingredients = st.text_input('Enter ingredients (comma separated)', '')
        st.write("Select the maximum time you are willing to spend on cooking. We’ll find recipes that fit within your schedule. ⏱️")
        max_ready_time = st.slider('Indicate Ready Time (minutes)', 10, 120, 30)

        # Button to generate recipes
        if st.button("Let's Spice Things Up"):
            params = {
                'includeIngredients': selected_ingredients,
                'maxReadyTime': max_ready_time,
                'number': 3,  # Number of recipes to fetch
                'instructionsRequired': True,
                'addRecipeInformation': True
            }

            with st.spinner('Whipping up some recipes...'):
                recipes = get_recipes(params, api_key)
                st.session_state.recipes = recipes.get('results', [])

        if 'recipes' in st.session_state:
            st.markdown("<h2 style='text-align: center;'>Lumine’s Recipe Picks 🍝</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center;'>Here are some delicious recipes that match your preferences!</h4>", unsafe_allow_html=True)

            for recipe in st.session_state.recipes:
                recipe_details = get_recipe_details(recipe['id'], api_key)
                if 'title' in recipe_details:
                    price_per_serving_usd = recipe_details.get('pricePerServing', 0) / 100  # pricePerServing is in cents
                    price_per_serving_eur = convert_usd_to_eur(price_per_serving_usd)

                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.subheader(f"{recipe_details['title']} (€{price_per_serving_eur:.2f} Per Serving) 🍽️")
                    with col2:
                        col2_1, col2_2 = st.columns([3, 1])
                        with col2_1:
                            if st.button('❤️', key=f"fav-{recipe['id']}"):
                                if len(st.session_state.get('favorites', [])) < 7:  # Limit to 7 favorites
                                    save_favorite(recipe['id'])
                                    st.toast('Recipe Added! Hooray', icon='🎉')
                                    time.sleep(0.75)
                                    st.toast("Check it out in Chef's Favorites!", icon = "👨‍🍳")
                                else:
                                    st.toast("Chef, you need to remove some of your favorite recipes! 🍲")
                        with col2_2:
                            if st.button('🔗', key=f"link-{recipe['id']}"):
                                js = f"window.open('{recipe_details['sourceUrl']}', '_blank')"
                                html = f"<script>{js}</script>"
                                st.markdown(html, unsafe_allow_html=True)

                    st.write(f"*Ready in {recipe_details['readyInMinutes']} minutes. Servings: {recipe_details['servings']}*")
                    st.image(recipe_details['image'], use_column_width=True)
                    source_name = recipe_details.get('sourceName', 'Recipe')
                    st.markdown(f"Source: [{source_name}]({recipe_details['sourceUrl']})")

                    st.info("### Ingredients 🛒🥕")
                    st.write("The following ingredients are needed to prepare this recipe:")
                    ingredients = "\n".join([f"- {ingredient['original']}" for ingredient in recipe_details['extendedIngredients']])
                    st.markdown(ingredients)

                    st.error("### Instructions 📜👩‍🍳")
                    if recipe_details.get('analyzedInstructions') and len(recipe_details['analyzedInstructions']) > 0 and len(recipe_details['analyzedInstructions'][0]['steps']) > 0:
                        st.write("Follow these steps to create your culinary masterpiece:")
                        instructions = "\n".join([f"{step['number']}. {step['step']}" for step in recipe_details['analyzedInstructions'][0]['steps']])
                        st.markdown(instructions)
                    else:
                        st.write("No instructions available for this recipe.")

                    st.success("### Nutrition Information 🍏💪")
                    st.write("Check out the nutritional benefits of your dish:")
                    nutrition_data = recipe_details['nutrition']['nutrients']
                    nutrition_df = pd.DataFrame(nutrition_data)[['name', 'amount', 'unit', 'percentOfDailyNeeds']]
                    nutrition_df.columns = ['Name', 'Amount per Serving', 'Unit', 'Daily Value (%)']

                    # Format 'Amount per Serving' and 'Daily Value (%)' to remove extra zeros
                    nutrition_df['Amount per Serving'] = nutrition_df['Amount per Serving'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))
                    nutrition_df['Daily Value (%)'] = nutrition_df['Daily Value (%)'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))

                    # Limit the DataFrame to the first 9 rows
                    nutrition_df = nutrition_df.head(9)
                    st.table(nutrition_df)

                else:
                    st.write("Recipe details not found. Please try another combination.")

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =============================================================================
    # Chef's Favorites Tab
    # =============================================================================
    with tab2:
        st.header("Chef's Favorites")
        st.write("""
            This page showcases your favorite recipes. Add recipes to this list by clicking the heart icon ❤️ on the Recipe Wizard 🧙‍♂️ tab. Remove recipes from your favorites by clicking the broken heart 💔 icon. Your favorite recipes will be saved here for easy access.
        """)
        favorite_recipes = get_favorites(api_key)

        if favorite_recipes:
            for recipe in favorite_recipes:
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.subheader(recipe['title'])
                with col2:
                    if st.button('💔', key=f"remove-{recipe['id']}"):
                        remove_favorite(recipe['id'])
                        st.experimental_rerun()

                st.image(recipe['image'], use_column_width=True)
                st.write(f"*Ready in {recipe['readyInMinutes']} minutes. Servings: {recipe['servings']}*")

                st.info("### Ingredients 🛒🥕")
                st.write("The following ingredients are needed to prepare this recipe:")
                ingredients = "\n".join([f"- {ingredient['original']}" for ingredient in recipe['extendedIngredients']])
                st.markdown(ingredients)

                if recipe.get('analyzedInstructions') and len(recipe['analyzedInstructions'][0]['steps']) > 0:
                    st.error("### Instructions 📜👩‍🍳")
                    st.write("Follow these steps to create your culinary masterpiece:")
                    instructions = "\n".join([f"{step['number']}. {step['step']}" for step in recipe['analyzedInstructions'][0]['steps']])
                    st.markdown(instructions)
                else:
                    st.write("No instructions available for this recipe.")

                st.success("### Nutrition Information 🍏💪")
                st.write("Check out the nutritional benefits of your dish:")
                nutrition_data = recipe['nutrition']['nutrients']
                nutrition_df = pd.DataFrame(nutrition_data)[['name', 'amount', 'unit', 'percentOfDailyNeeds']]
                nutrition_df.columns = ['Name', 'Amount per Serving', 'Unit', 'Daily Value (%)']

                # Format 'Amount per Serving' and 'Daily Value (%)' to remove extra zeros
                nutrition_df['Amount per Serving'] = nutrition_df['Amount per Serving'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))
                nutrition_df['Daily Value (%)'] = nutrition_df['Daily Value (%)'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))

                # Limit the DataFrame to the first 9 rows
                nutrition_df = nutrition_df.head(9)
                st.table(nutrition_df)

                source_name = recipe.get('sourceName', 'Recipe')
                st.markdown(f"Source: [{source_name}]({recipe['sourceUrl']})")

        else:
            st.write("You have no favorite recipes yet. Start adding some delicious dishes!")

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =============================================================================
    # Magic Grocery List Generator Tab
    # =============================================================================
    with tab3:
        st.header("Magic Grocery List Generator")
        st.write("""
            This tool conjures up a grocery list based on your favorite recipes. Add recipes to your favorites in the Chef's Favorites ❤️ tab, then come back here to see a consolidated list of ingredients.
        """)

        if 'favorites' in st.session_state and st.session_state['favorites']:
            favorite_recipes = get_favorites(api_key)
            grocery_list = generate_grocery_list(favorite_recipes)

            if grocery_list:
                st.write("### Grocery List")
                grocery_df = pd.DataFrame.from_dict(grocery_list, orient='index')
                grocery_df.reset_index(inplace=True)
                grocery_df.columns = ['Name', 'Amount', 'Unit']

                # Remove rows with null values in 'Amount' or 'Unit'
                grocery_df.dropna(subset=['Amount', 'Unit'], inplace=True)

                # Format the Amount column to remove unnecessary zeros
                grocery_df['Amount'] = grocery_df['Amount'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))

                st.table(grocery_df)

                # Download button for the grocery list
                csv = grocery_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Grocery List",
                    data=csv,
                    file_name='grocery_list.csv',
                    mime='text/csv',
                )
            else:
                st.write("No ingredients found in your favorite recipes.")
        else:
            st.write("You need to have favorite recipes to generate a grocery list. Start adding some delicious dishes!")

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =============================================================================
    # Meal Master Planner Tab
    # =============================================================================
    with tab4:
        st.header("Meal Master Planner")
        st.write("""
            This tool helps you orchestrate your meals for up to 7 days based on your favorite recipes. Add recipes to your favorites in the Chef's Favorites ❤️ tab, then come back here to create a masterful meal plan. Each day will feature a different recipe from your favorites.
        """)

        if 'favorites' in st.session_state and st.session_state['favorites']:
            favorite_recipes = get_favorites(api_key)
            max_days = min(7, len(favorite_recipes))

            meal_plan = []
            total_cost = 0
            for i in range(max_days):
                recipe = favorite_recipes[i % len(favorite_recipes)]
                price_per_serving_usd = recipe.get('pricePerServing', 0) / 100  # pricePerServing is in cents
                price_per_serving_eur = convert_usd_to_eur(price_per_serving_usd)
                total_cost += price_per_serving_eur * recipe['servings']

                meal_plan.append({
                    'Day': f'Day {i + 1}',
                    'Image': recipe['image'],
                    'Recipe': recipe['title'],
                    'Ready Time': f"{recipe['readyInMinutes']} minutes",
                    'Servings': recipe['servings'],
                    'Source': recipe['sourceUrl']
                })

            total_cost_with_discount = total_cost * 0.76  # 24% discount
            saved_amount = total_cost - total_cost_with_discount

            st.write(f"### Your Meal Plan for {max_days} Days (Saved: €{saved_amount:.2f})")

            # Display the meal plan in a structured format
            for day_plan in meal_plan:
                st.write(f"### {day_plan['Day']}")
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(day_plan['Image'], width=170)
                with col2:
                    st.markdown(f"""
                        1. **Recipe:** {day_plan['Recipe']}
                        2. **Ready Time:** {day_plan['Ready Time']}
                        3. **Servings:** {day_plan['Servings']}
                        **Source:** [Link to Recipe]({day_plan['Source']})
                    """)

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"### Total Amount without Discount: €{total_cost:.2f}")
            with col2:
                st.write(f"### Total Amount with Discount: €{total_cost_with_discount:.2f}")

            # Prepare DataFrame for download
            meal_plan_df = pd.DataFrame(meal_plan).drop(columns=['Image'])

            # Download button for the meal plan
            csv = meal_plan_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Meal Plan",
                data=csv,
                file_name='meal_plan.csv',
                mime='text/csv',
            )
        else:
            st.write("You need to have favorite recipes to create a meal plan. Start adding some delicious dishes!")

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
            </div>
            """,
            unsafe_allow_html=True
        )


    # =============================================================================
    # Budget Bites Tab
    # =============================================================================
    with tab5:
        st.header("Data Driven StartUp Lumine's: Budget Bites")

        st.write("""
        We are a group of culinary wizards (a.k.a. students) on a mission to cook up a revolutionary recipe app and generator, spiced with a pinch of machine learning magic. Our app will serve up recipes based on grocery discounts, helping you whip up delicious dishes while saving dough (both kinds!). 🍞💰
        """)

        # Check if the video file exists
        video_path = "Video.mp4"
        if os.path.exists(video_path):
            video_file = open(video_path, "rb")
            video_bytes = video_file.read()
            st.video(video_bytes)
        else:
            st.warning("Sorry, the startup video is currently unavailable. Please check back later.")
            st.write(f"Expected video file at: {os.path.abspath(video_path)}")

        # Start Up Explanation

        st.write("#### Let us tell you about our sizzling start-up idea: Budget Bites! 🍳")

        st.write("""
        Imagine reducing food waste, slashing grocery expenses, and creating mouth-watering meals from discounted items. Sounds like a dream, right? Well, we’re making it a reality! Our interactive platform will let you buy budget-friendly ingredients from multiple stores and turn them into scrumptious recipes. 🛒➡️🍲
        """)

        st.write("""
        With food prices on the rise, more folks are feeling the pinch. They crave recipes that are easy on the wallet but packed with nutrition. Our app will be your trusty sous-chef, providing a feast of recipes based on the best grocery deals in town. 🌍
        """)

        st.write("""
        You’ll be able to tailor your culinary adventures by setting preferences like diet, nutrition, allergies, and cooking skills. Whether you’re a kitchen novice or a seasoned pro, our app will deliver recipes that hit the sweet spot in flavor and price. 🥦🍗
        """)

        st.write("""
        Our secret ingredient? We’ll suggest discounted goodies from various stores using our machine learning know-how. While other apps only show their own deals, we mix and match products from all over to bring you the best savings and recipe ideas. Think of us as your personal shopper and chef, all in one! 🍎🛒👩‍🍳
        """)

        st.write("""
        Our mission is to provide a smorgasbord of quality recipes while helping you make the most of grocery store discounts in the Netherlands. By tackling food waste and high prices, we aim to make cooking affordable, fun, and sustainable for everyone. 🍽️🌟
        """)

        st.markdown("---")

        st.header("Data Driven StartUp Application")

        st.markdown("  ")
        st.markdown("  ")

        # Create a row of two columns for the Figma iframe and the text, without an explicit spacer
        col1, col2 = st.columns(2)

        # Embed the Figma design in the first column (col1)
        figma_embed_code = '''
        <iframe style="border: none; height: 690px; width: 100%; margin-right: 20px;
                      transform: scale(1) translate(0px, 0px); overflow: hidden;"
                src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Fproto%2FMUQ4LgVpNzi8hjL16qpw1C%2FBig-Data-and-Design%3Fnode-id%3D1337-7169%26t%3DITo1SGMcVbUYaqJ8-1%26scaling%3Dscale-down%26page-id%3D1272%253A4969%26starting-point-node-id%3D1337%253A9028"
                allowfullscreen>
        </iframe>
        '''
        col1.markdown(figma_embed_code, unsafe_allow_html=True)

        # New introductory text with three paragraphs
        intro_text_part1 = "In this third block of our Minor, we're crafting a personalized and efficient user experience with a Budget Bites application. Chefs can customize their home page and switch locations to find local discounts. Fully-stocked folders are organized and categorized for specific recipe searches, while profile switching allows for both personalized and non-personalized cooking experiences. Advanced filters include price per serving and budget-friendly options, and chefs can choose to include or exclude AI-generated recipes."
        intro_text_part2 = "Push notifications serve up recipes based on ingredients about to expire, and text-to-speech provides hands-free cooking instructions. Additional features include meal planning, bookmarks, and an activity feed to share your culinary creations with fellow food enthusiasts."
        intro_text_part3 = "Future upgrades will include gesture-based instructions and voice commands for easier interaction, along with AI-generated instructional videos to guide novice chefs through recipes. These features aim to make cooking more intuitive, engaging, and accessible for all chefs, from beginners to seasoned professionals."

        # Display the introductory text in the column with padding at the top for spacing between paragraphs
        col2.markdown(f"<div style='padding-top: 0px;'>{intro_text_part1}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='padding-top: 20px;'>{intro_text_part2}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='padding-top: 20px;'>{intro_text_part3}</div>", unsafe_allow_html=True)

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
            </div>
            """,
            unsafe_allow_html=True
        )


    # =============================================================================
    # Food Selfie Classifier Tab
    # =============================================================================

    with tab6:
        st.header("Welcome to the Culinary Classifier!")
        st.write("""
            Upload a picture of your food and let the magic of AI tell you what it is. This tool will classify your food and provide matching recipes. Simply upload an image and see what it has cooked!
        """)

        # Upload image
        uploaded_file = st.file_uploader("Upload a food picture and see what happens...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Display uploaded image
            st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

            # Save uploaded image to a temporary file
            with open("temp_classify_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Call Spoonacular API to analyze image
            with st.spinner('Analyzing image...'):
                classify_response = analyze_image("temp_classify_image.jpg", api_key)
            if 'category' in classify_response:
                food_category = classify_response['category']['name']
                probability = classify_response['category']['probability']
                st.subheader(f"🧐 I think this is **{food_category}** with a probability of {probability:.2f}!")

                # Display nutrition profile
                if 'nutrition' in classify_response:
                    st.markdown(f"### Nutrition Profile of {food_category}")
                    nutrition_profile = classify_response['nutrition']
                    st.markdown(f"""
                                - **Calories:** {nutrition_profile['calories']['value']} kcal
                                - **Fat:** {nutrition_profile['fat']['value']} g
                                - **Protein:** {nutrition_profile['protein']['value']} g
                                - **Carbohydrates:** {nutrition_profile['carbs']['value']} g
                    """)

                # Display matching recipes
                if 'recipes' in classify_response:
                    st.markdown("<h2 style='text-align: center;'>Lumine’s Recipe Picks 🍝</h2>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>Here are some delicious recipes that match the image: {food_category}!</h4>", unsafe_allow_html=True)
                    recipe_count = 0  # Initialize recipe counter
                    for recipe in classify_response['recipes']:
                        if recipe_count >= 3:
                            break
                        recipe_details = get_recipe_details(recipe['id'], api_key)
                        if 'title' in recipe_details:
                            recipe_count += 1  # Increment recipe counter
                            price_per_serving_usd = recipe_details.get('pricePerServing', 0) / 100  # pricePerServing is in cents
                            price_per_serving_eur = convert_usd_to_eur(price_per_serving_usd)

                            col1, col2 = st.columns([9, 1])
                            with col1:
                                st.subheader(f"{recipe_details['title']} (€{price_per_serving_eur:.2f} Per Serving) 🍽️")
                            with col2:
                                if st.button('🔗', key=f"link-{recipe['id']}"):
                                    js = f"window.open('{recipe_details['sourceUrl']}', '_blank')"
                                    html = f"<script>{js}</script>"
                                    st.markdown(html, unsafe_allow_html=True)

                            st.write(f"*Ready in {recipe_details['readyInMinutes']} minutes. Servings: {recipe_details['servings']}*")
                            st.image(recipe_details['image'], use_column_width=True)
                            source_name = recipe_details.get('sourceName', 'Recipe')
                            st.markdown(f"Source: [{source_name}]({recipe['sourceUrl']})")

                            st.info("### Ingredients 🛒🥕")
                            st.write("The following ingredients are needed to prepare this recipe:")
                            ingredients = "\n".join([f"- {ingredient['original']}" for ingredient in recipe_details['extendedIngredients']])
                            st.markdown(ingredients)

                            if recipe_details.get('analyzedInstructions') and len(recipe_details['analyzedInstructions'][0]['steps']) > 0 and len(recipe_details['analyzedInstructions'][0]['steps']) > 0:
                                st.error("### Instructions 📜👩‍🍳")
                                st.write("Follow these instructions to create your culinary masterpiece:")
                                instructions = "\n".join([f"{step['number']}. {step['step']}" for step in recipe_details['analyzedInstructions'][0]['steps']])
                                st.markdown(instructions)
                            else:
                                st.write("No instructions available for this recipe.")

                            st.success("### Nutrition Information 🍏💪")
                            st.write("Check out the nutritional benefits of your dish:")
                            nutrition_data = recipe_details['nutrition']['nutrients']
                            nutrition_df = pd.DataFrame(nutrition_data)[['name', 'amount', 'unit', 'percentOfDailyNeeds']]
                            nutrition_df.columns = ['Name', 'Amount per Serving', 'Unit', 'Daily Value (%)']

                            # Format 'Amount per Serving' and 'Daily Value (%)' to remove extra zeros
                            nutrition_df['Amount per Serving'] = nutrition_df['Amount per Serving'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))
                            nutrition_df['Daily Value (%)'] = nutrition_df['Daily Value (%)'].apply(lambda x: ('%f' % x).rstrip('0').rstrip('.'))

                            # Limit the DataFrame to the first 9 rows
                            nutrition_df = nutrition_df.head(9)
                            st.table(nutrition_df)

                        else:
                            st.write("Recipe details not found. Please try another combination.")
            else:
                st.write("Could not classify the image. Please try another one.")

            # Footer
            st.markdown("---")
            st.markdown(
                """
                <div style="text-align: center; padding: 10px 0;">
                    <p>Copyright © 2024 Lumine All rights reserved. Made with <span style="color: red;">&#10084;</span> by Singh AmanDeep</p>
                </div>
                """,
                unsafe_allow_html=True
                )