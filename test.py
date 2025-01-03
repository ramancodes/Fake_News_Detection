import requests

# Define the NewsAPI endpoint and your API key
NEWS_API_URL = "https://newsapi.org/v2/everything"
API_KEY = 'f0edf6c162b74e9db7ef89861aed265f'

# Function to search for news based on headline or summary
def search_news(query):
    # Define the parameters for the API request
    params = {
        'q': query,                  # Search query (headline/summary)
        'apiKey': API_KEY,           # Your NewsAPI key
        'language': 'en',            # Search news in English
        'sortBy': 'relevancy',       # Sort results by relevancy
        'pageSize': 5,               # Number of articles to fetch
    }
    
    try:
        # Send the request to NewsAPI
        response = requests.get(NEWS_API_URL, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Check if articles are found
            articles = data.get('articles', [])
            if articles:
                print(f"Found {len(articles)} articles matching your query:\n")
                for i, article in enumerate(articles, start=1):
                    title = article.get('title', 'No title')
                    description = article.get('description', 'No description')
                    url = article.get('url', 'No URL')
                    published_at = article.get('publishedAt', 'No date')
                    source_name = article.get('source', {}).get('name', 'Unknown source')
                    
                    print(f"Article {i}:")
                    print(f"Title: {title}")
                    print(f"Description: {description}")
                    print(f"Source: {source_name}")
                    print(f"Published at: {published_at}")
                    print(f"URL: {url}\n")
            else:
                print("No articles found matching your query.")
        else:
            print(f"Error: {response.status_code} - Could not fetch news.")
    except Exception as e:
        print(f"An error occurred: {e}")

# User provides a headline or summary
user_input = input("Enter a news headline or summary: ")

# Search for the news articles
search_news(user_input)
