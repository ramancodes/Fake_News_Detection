from flask import Flask, request, render_template
import requests
import joblib
import pandas as pd
from sklearn.linear_model import PassiveAggressiveClassifier
from datetime import datetime
import os

# API Keys for CNN, BBC, Fox News
# NEWS_URL_CNN = f'https://saurav.tech/NewsAPI/everything/cnn.json'
# NEWS_URL_BBC = f'https://saurav.tech/NewsAPI/everything/bbc-news.json'
# NEWS_URL_FOX_NEWS = f'https://saurav.tech/NewsAPI/everything/fox-news.json'
NEWS_URL_CNN = os.getenv("NEWS_URL_CNN")
NEWS_URL_BBC = os.getenv("NEWS_URL_BBC")
NEWS_URL_FOX_NEWS = os.getenv("NEWS_URL_FOX_NEWS")

# Load the pre-trained ML model and vectorizer
model = joblib.load(open('model.joblib', 'rb'))
vectorizer = joblib.load(open('vectorizer.joblib', 'rb'))

app = Flask(__name__)

# Function to fetch news
def getData():
    all_news = []
    titles = []
    description = []

    res = requests.get(NEWS_URL_CNN)
    if res.status_code == 200:
        res_json = res.json()
        for article in res_json['articles']:
            all_news.append(article)
            titles.append(article['title'])
            description.append(article['description'])

    res = requests.get(NEWS_URL_BBC)
    if res.status_code == 200:
        res_json = res.json()
        for article in res_json['articles']:
            all_news.append(article)
            titles.append(article['title'])
            description.append(article['description'])

    res = requests.get(NEWS_URL_FOX_NEWS)
    if res.status_code == 200:
        res_json = res.json()
        for article in res_json['articles']:
            all_news.append(article)
            titles.append(article['title'])
            description.append(article['description'])

    response = {
        "titles": titles,
        "description": description,
        "all_news": all_news
    }

    return response


# function to get the related news
def search_news(query):
    API_KEY = '<news_api_key>'
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    # Define the parameters for the API request
    params = {
        'q': query,                  # Search query (headline/summary)
        'apiKey': API_KEY,           # Your NewsAPI key
        'language': 'en',            # Search news in English
        'sortBy': 'relevancy',       # Sort results by relevancy
        'pageSize': 5,               # Number of articles to fetch
    }
    
    # Send the request to NewsAPI
    response = requests.get(NEWS_API_URL, params=params)

    message = None
    matched_articles_title = []
    matched_articles_description = []
    matched_urls = []
    
    # Check if the request was successful
    if response.status_code == 200:
        response = response.json()
        articles = response['articles']
        
        # If articles are found
        if articles:
            message = f"Found {len(articles)} article matching."
            
            for article in articles:
                matched_length = len(articles)
                matched_articles_title.append(article['title'])
                matched_articles_description.append(article['description'])
                matched_urls.append(article['url'])

            return [200, message, matched_length, matched_articles_title, matched_articles_description, matched_urls]
        else:
            message = "No articles found matching."
            return [204, message]
    else:
        print(f"Error: {response.status_code} - Could not fetch news.")

def get_news_from_api():
    
    try:
        data = getData()["all_news"]
        
        # Transform the API response into the format we need
        news_items = []
        for item in data['articles']:
            news_items.append({
                'title': item['title'],
                'description': item['description'],
                'image_url': item['urlToImage'],
                'url': item['url'],
                'date': datetime.strptime(item['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            })
        return news_items
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []



@app.route('/')
def home():
    news_items = get_news_from_api()
    testimonials = [
        {
            'content': "The Fake News Detection tool utilizes cutting-edge machine learning to provide fast and reliable results. It's an invaluable resource for journalists and researchers aiming to maintain credibility in their work.",
            'image': 'https://dummyimage.com/106x106',
            'name': 'Raman Kumar',
            'role': 'DEVELOPER'
        },
    ]

    return render_template("index.html",news_items=news_items, testimonials=testimonials)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    # Fetch and train model on real-time data from CNN and BBC
    response_news = getData()
    titles, description = response_news["titles"], response_news["description"]
    data = pd.DataFrame(
        {
            'title': titles,
            'text': description,
            'label': 'REAL'
        }
    )
    # print(data)
    X = data['text']
    y = data['label']

    tf_X = vectorizer.transform(X)
    model.partial_fit(tf_X, y)

    matched_length = None
    matched_articles_title = None
    matched_articles_description = None
    matched_urls = None

    # Handle user input and prediction
    if request.method == "POST":
        news = str(request.form['news'])
        print(news)

        predict = model.predict(vectorizer.transform([news]))[0]
        print(predict)

        response = search_news(news)
        if(response[0]==200):
            print(response[1])
            print(type(response[3]))
            matched_length = response[2]
            matched_articles_title = response[3]
            matched_articles_description = response[4]
            matched_urls = response[5]
            print(matched_articles_title)
            print(matched_articles_description)
            print(matched_urls)

        else:
            print(response[1])

        return render_template(
            "prediction.html",
            prediction_text=f"News headline is -> {predict}",
            submmited_news = news,
            response_status_code = response[0],
            response = response[1],
            matched_length = matched_length,
            matched_articles_title = matched_articles_title,
            matched_articles_description = matched_articles_description,
            matched_urls = matched_urls
        )
    else:
        return render_template("prediction.html")

if __name__ == '__main__':
    app.debug = True
    app.run()
