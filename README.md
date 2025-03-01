Social Media Comment Analyzer

Overview

The Social Media Comment Analyzer is an AI-powered tool that scrapes comments from Instagram and YouTube, detects spam, and analyzes sentiment to provide insights for influencers. The tool is built using Streamlit, Selenium, and Groq AI.

Features

Scrape Instagram & YouTube comments

Detect spam comments using keyword filtering

Analyze sentiment with AI (Groq API)

Provide engagement insights & recommendations

Suggest actions to manage spam users

Installation

Prerequisites

Ensure you have the following installed:

Python 3.x

Google Chrome

ChromeDriver (automatically managed by webdriver-manager)

Usage

Run the Streamlit app:

streamlit run app.py

How to Use

Enter an Instagram or YouTube post/video URL.

Click on Analyze Comments.

View AI-generated insights on engagement.

See spam detection results.

Get AI-powered recommendations for managing spam.

Technologies Used

Python (Main Programming Language)

Selenium (Web Scraping)

Streamlit (Web App Framework)

Groq API (AI-based Analysis)

dotenv (Environment Variable Management)

Notes

The tool runs in headless mode for faster scraping.

Ensure Instagram and YouTube page structures are still compatible with the scraping logic.

API usage may have rate limits; check Groq API documentation.

Contributors

Team Deepthinkers
