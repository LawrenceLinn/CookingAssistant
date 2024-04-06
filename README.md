# Cooking Assistant

## Introduction

Cooking Assistant is an innovative chatbot designed to make your culinary exploration as effortless and personalized as possible. By utilizing cutting-edge visual recognition technology, Cooking Assistant identifies ingredients in your fridge and then recommends recipes that cater to your specific preferences. Whether you're a seasoned chef or a beginner, our chatbot is here to inspire your next home-cooked meal with recommendations that match your taste, dietary restrictions, and what you have on hand.

## Features

- **Ingredient Recognition**: Take a photo of the inside of your fridge, and our AI will identify and list the ingredients you have available.
- **Personalized Recipe Recommendations**: Based on the ingredients identified and your dietary preferences, receive curated recipes that suit your taste and needs.
- **Interactive Chatbot Experience**: Engage with Cooking Assistant through a friendly chat interface to refine your preferences, ask for recipe suggestions, and even get cooking tips.
- **Seamless Integration**: Easy to integrate with various social media and messaging platforms for access anytime, anywhere.

## Technology Stack

- **AI and Machine Learning**: Utilizes state-of-the-art machine learning models for accurate visual recognition of ingredients.
- **Natural Language Processing (NLP)**: Empowers the chatbot to understand and process user requests efficiently.
- **Web Technologies**: Built using FARMD framework (Fastapi, React, MongoDB, Docker), ensuring a smooth and responsive user interface.

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/LawrenceLinn/CookingAssistant.git
   cd cooking-assistant
   ```

2. **Run with docker**
   ```bash
   docker compose -f docker-compose.test.yml up -d --build
   ```

## Usage

After setting up the project, interact with the Cooking Assistant through its chat interface. Simply upload a photo of your fridge's contents, and let the assistant know of any specific dietary preferences or restrictions. The chatbot will then provide you with a list of ingredient-optimized, personalized recipes to choose from.
