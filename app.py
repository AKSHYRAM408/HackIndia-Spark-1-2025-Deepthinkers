import time
import re
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
GROK_API_KEY = os.getenv("GROQ_API_KEY")

if not GROK_API_KEY:
    st.error("Error: GROK_API_KEY is not set. Check your .env file.")
    st.stop()

GROK_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def scrape_instagram_comments(reel_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(reel_url)
    time.sleep(5)

    comments_data = []
    
    comment_elements = driver.find_elements(By.CSS_SELECTOR, "ul li")
    for comment_element in comment_elements:
        try:
            username = comment_element.find_element(By.CSS_SELECTOR, "h3").text  # Extract username
            comment = comment_element.find_element(By.CSS_SELECTOR, "span").text  # Extract comment text
            comments_data.append((username, comment))
        except:
            continue  # Skip if data is not found

    driver.quit()
    return comments_data

def scrape_youtube_comments(video_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(video_url)
    time.sleep(10)

    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

    comments_data = []
    
    comment_elements = driver.find_elements(By.CSS_SELECTOR, "#comment")
    for comment_element in comment_elements:
        try:
            username = comment_element.find_element(By.CSS_SELECTOR, "#author-text").text.strip()  # Extract username
            comment = comment_element.find_element(By.CSS_SELECTOR, "#content-text").text.strip()  # Extract comment text
            comments_data.append((username, comment))
        except:
            continue  # Skip if data is not found

    driver.quit()
    return comments_data

def detect_spam(comments_with_users):
    spam_keywords = ["follow me", "free money", "click this link", "DM us", "buy followers", 
                     "promotion", "promo code", "earn cash", "instant profit"]

    spam_comments_list = []

    for user_id, comment in comments_with_users:
        if any(keyword in comment.lower() for keyword in spam_keywords):
            spam_comments_list.append((user_id, comment))

    return spam_comments_list

def analyze_comments_with_grok(comments):
    messages = [
        {"role": "system", "content": "You are an expert social media analyst."},
        {"role": "user", "content": f"Analyze these comments:\n\n{comments}\n\n"
                                     "Tasks:\n"
                                     "1. Determine the positive reach (engagement sentiment).\n"
                                     "2. Suggest improvements for better audience interaction.\n"
                                     "3. Provide actionable recommendations to boost engagement.\n\n"
                                     "Format your response as:\n"
                                     "- Positive Reach: (percentage or description)\n"
                                     "- Negative Reach: (percentage or description)\n"
                                     "- Suggested Improvements: (list)\n"
                                     "- Recommendations (two points): (list)"}
    ]

    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 350
    }

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROK_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    else:
        return f"Error: {response.status_code} - {response.text}"

def suggest_spam_user_restrictions(spam_users_list):
    if not spam_users_list:
        return "No frequent spammers detected."

    spam_details = "\n".join([f"{user_id}: {comment}" for user_id, comment in spam_users_list])

    messages = [
        {"role": "system", "content": "You are a social media expert helping influencers manage spam."},
        {"role": "user", "content": f"Here is a list of users who have repeatedly posted spam comments:\n\n{spam_details}\n\n"
                                     "Suggest the best ways for an influencer to handle these users.\n"
                                     "Provide responses in:\n"
                                     "- Summary of the issue.\n"
                                     "- Recommended actions (limit to 3 practical steps)."}
    ]

    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 150
    }

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROK_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    else:
        return f"Error: {response.status_code} - {response.text}"

st.set_page_config(page_title="Social Media Comment Analyzer", page_icon="📲", layout="wide")

st.markdown("<h1 style='text-align: center; color: #E1306C;'>📲 Social Media Comment Analyzer</h1>", unsafe_allow_html=True)

url = st.text_input("Enter Instagram or YouTube URL:", help="Paste the link of the post/video you want to analyze.")

analyze_button = st.button("Analyze Comments")

if analyze_button:
    if url:
        with st.spinner("Detecting platform and scraping comments..."):
            if "instagram.com" in url:
                platform = "Instagram"
                comments_with_users = scrape_instagram_comments(url)
            elif "youtube.com" in url or "youtu.be" in url:
                platform = "YouTube"
                comments_with_users = scrape_youtube_comments(url)
            else:
                st.error("Invalid URL. Please enter a valid Instagram or YouTube link.")
                st.stop()

        st.success(f"Comments scraped successfully from {platform}!")

        with st.spinner("Analyzing comments with AI..."):
            comments_text = "\n".join([comment for _, comment in comments_with_users])  # Only text comments
            ai_response = analyze_comments_with_grok(comments_text)
        
        spam_comments_list = detect_spam(comments_with_users)

        st.subheader(f"💡 AI Insights on {platform}:")
        st.write(ai_response)

        st.subheader(f"🚨 Spam Detection:")
        st.write(f"Spam Percentage: {len(spam_comments_list) / len(comments_with_users) * 100:.2f}%")

        if spam_comments_list:
            with st.spinner("Getting AI recommendations for spam users..."):
                restriction_suggestions = suggest_spam_user_restrictions(spam_comments_list)

            st.subheader("🔒 AI Recommendations for Restricting Spam Users:")
            st.write(restriction_suggestions)
    else:
        st.error("Please enter a valid URL.")
 
