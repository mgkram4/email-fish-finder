import nltk

def download_nltk_data():
    """Download required NLTK data packages."""
    resources = [
        'punkt',
        'stopwords',
        'averaged_perceptron_tagger',
        'wordnet',
        'omw-1.4'
    ]
    
    for resource in resources:
        print(f"Downloading {resource}...")
        nltk.download(resource)
        print(f"Downloaded {resource} successfully!")

if __name__ == "__main__":
    print("Starting NLTK resource download...")
    download_nltk_data()
    print("\nAll NLTK resources have been downloaded successfully!")