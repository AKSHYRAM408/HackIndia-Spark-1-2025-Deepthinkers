import time
import re
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load API Key securely from Streamlit Secrets
load_dotenv()
GROK_API_KEY = os.getenv("GROQ_API_KEY")
GROK_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Function to check if Playwright is installed
def check_playwright():
    try:
        import playwright
        return True
    except ImportError:
        return False

# Function to scrape Instagram comments using Playwright
def scrape_instagram_comments(reel_url):
    if not check_playwright():
        st.warning("Playwright is not available. Please install Playwright.")
        return []

    comments = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(reel_url)
        time.sleep(5)

        try:
            comments_elements = page.query_selector_all("ul li span")
            comments = [comment.inner_text() for comment in comments_elements if comment.inner_text().strip()]
        except Exception as e:
            st.error(f"Error scraping Instagram: {e}")

        browser.close()
    return comments

# Function to scrape YouTube comments using Playwright
def scrape_youtube_comments(video_url):
    if not check_playwright():
        st.warning("Playwright is not available. Please install Playwright.")
        return []

    comments = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(video_url)
        time.sleep(5)

        try:
            # Scroll down to load comments
            for _ in range(8):
                page.keyboard.press("PageDown")
                time.sleep(2)

            comments_elements = page.query_selector_all("#content-text")
            comments = [comment.inner_text() for comment in comments_elements if comment.inner_text().strip()]
        except Exception as e:
            st.error(f"Error scraping YouTube: {e}")

        browser.close()
    return comments

# Function to clean comments
def clean_comment(comment):
    return re.sub(r'[^\w\s.,!?\'"-]', '', comment)

spam_keywords = ["follow me", "free money", "click this link", "DM us", "buy followers", "promotion", "promo code", "earn cash", "instant profit"]

# Function to detect spam percentage
def detect_spam(comments):
    total_comments = len(comments)
    spam_count = sum(1 for comment in comments if any(keyword.lower() in comment.lower() for keyword in spam_keywords))
    return round((spam_count / total_comments) * 100, 2) if total_comments > 0 else 0

# Function to analyze comments with Grok AI
def analyze_comments_with_grok(comments):
    if not comments:
        return "No comments found for analysis."

    messages = [
        {"role": "system", "content": "You are an expert social media analyst."},
        {"role": "user", "content": f"Analyze these comments:\n\n{comments}\n\n"
                                     "Tasks:\n"
                                     "1. Determine positive reach (engagement sentiment).\n"
                                     "2. Identify negative reach (if any).\n"
                                     "3. Detect spam patterns (repetitive messages, excessive promotions, bot-like behavior).\n"
                                     "4. Suggest improvements for audience interaction.\n"
                                     "5. Provide two recommendations to boost engagement.\n"
                                     "Format response as:\n"
                                     "- Positive Reach: (percentage or description)\n"
                                     "- Negative Reach: (percentage or description)\n"
                                     "- Suggested Improvements: (list)\n"
                                     "- Recommendations: (list)\n"}
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

# Streamlit UI Setup
st.set_page_config(page_title="Social Media Comment Analyzer", page_icon="📲", layout="wide")

st.markdown("<h1 style='text-align: center; color: #E1306C;'>📲 Social Media Comment Analyzer</h1>", unsafe_allow_html=True)

# Input for URL
url = st.text_input("Enter Instagram or YouTube URL:", help="Paste the link of the post/video you want to analyze.")

# Centering the Button
analyze_button = st.button("Analyze Comments")

if analyze_button:
    if url:
        with st.spinner("Detecting platform and scraping comments..."):
            if "instagram.com" in url:
                platform = "Instagram"
                comments = scrape_instagram_comments(url)
            elif "youtube.com" in url or "youtu.be" in url:
                platform = "YouTube"
                comments = scrape_youtube_comments(url)
            else:
                st.error("Invalid URL. Please enter a valid Instagram or YouTube link.")
                st.stop()

        if not comments:
            st.error("No comments found. Ensure the post is public and try again.")
        else:
            cleaned_comments = [clean_comment(comment) for comment in comments]
            comments_text = "\n".join(cleaned_comments)

            st.success(f"Comments scraped successfully from {platform}!")

            with st.spinner("Analyzing comments with AI..."):
                ai_response = analyze_comments_with_grok(comments_text)
            
            spam_percentage = detect_spam(cleaned_comments)

            st.subheader(f"💡 AI Insights on {platform}:")
            st.write(ai_response)
            st.write(f"🚨 **Spam Percentage:** {spam_percentage}%")
    else:
        st.error("Please enter a valid URL.")
