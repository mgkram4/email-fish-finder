import os
import re

import joblib
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


class EmailClassifier:
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model_path = 'data/models/phishing_classifier.joblib'
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.initialize_nltk()
        self._initialize_model()
        
    def initialize_nltk(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
    def _initialize_model(self):
        """Initialize the model with some basic training data."""
        try:
            self.classifier, self.vectorizer = joblib.load(self.model_path)
        except FileNotFoundError:
            print("Training new model with sample data...")
            # Sample training data
            sample_emails = [
                "Dear user, your account has been suspended. Click here to verify.",
                "Urgent: Your password needs to be reset immediately.",
                "Congratulations! You've won a prize. Click to claim.",
                "Please find attached the invoice for your recent purchase.",
                "Your package has been shipped. Track it here.",
                "Meeting scheduled for tomorrow at 10 AM.",
                "Security alert: unusual login attempt detected.",
                "Your Netflix account needs verification.",
                "Bank account alert: Please confirm your identity.",
                "Hi, when is the project deadline?",
            ]
            
            # 1 for phishing, 0 for legitimate
            labels = [1, 1, 1, 0, 0, 0, 1, 1, 1, 0]
            
            # Preprocess the training data
            processed_emails = [self.preprocess_text(email) for email in sample_emails]
            
            # Fit the vectorizer and transform the training data
            X = self.vectorizer.fit_transform(processed_emails)
            
            # Train the classifier
            self.classifier.fit(X, labels)
            
            # Save the model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump((self.classifier, self.vectorizer), self.model_path)
    
    def preprocess_text(self, text):
        """Preprocess email text for classification."""
        if not isinstance(text, str):
            text = str(text)
            
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize using RegexpTokenizer (avoids punkt tokenizer)
        tokens = self.tokenizer.tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
        
        return ' '.join(tokens)
    
    def predict(self, email_features):
        """Predict if an email is phishing."""
        try:
            # Load model if not already loaded
            if not hasattr(self, 'classifier') or self.classifier is None:
                try:
                    self.classifier, self.vectorizer = joblib.load(self.model_path)
                except FileNotFoundError:
                    # If no trained model exists, return a default prediction
                    print("No trained model found. Using heuristic analysis.")
                    return self._heuristic_prediction(email_features)
            
            # Preprocess and transform features
            processed_text = self.preprocess_text(email_features['text'])
            X = self.vectorizer.transform([processed_text])
            
            # Get prediction and probability
            prediction = self.classifier.predict(X)[0]
            probability = self.classifier.predict_proba(X)[0]
            
            return prediction, max(probability)
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            # Fallback to heuristic analysis
            return self._heuristic_prediction(email_features)
    
    def _heuristic_prediction(self, email_features):
        """Perform basic heuristic analysis when ML model is unavailable."""
        score = 0
        text = email_features.get('text', '').lower()
        
        # Check for urgent language
        urgent_words = ['urgent', 'immediate', 'suspended', 'verify', 'blocked']
        if any(word in text for word in urgent_words):
            score += 0.3
            
        # Check for credential requests
        if 'password' in text or 'login' in text:
            score += 0.3
            
        # Check for threats
        if 'suspended' in text or 'terminated' in text or 'deleted' in text:
            score += 0.2
            
        # Check for suspicious URLs
        urls = email_features.get('urls', [])
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq']
        if any(url.lower().endswith(tld) for url in urls for tld in suspicious_tlds):
            score += 0.2
            
        is_phishing = score >= 0.5
        return is_phishing, score
    
    def explain_prediction(self, email_features):
        """Provide explanation for the prediction."""
        explanation = {
            'suspicious_patterns': self._identify_suspicious_patterns(email_features),
            'url_analysis': self._analyze_urls(email_features),
            'top_features': self._get_top_features(email_features)
        }
        
        return explanation
    
    def _identify_suspicious_patterns(self, email_features):
        """Identify suspicious patterns in the email."""
        patterns = []
        text = email_features.get('text', '').lower()
        
        # Check for urgent language
        if any(word in text for word in ['urgent', 'immediate', 'suspended']):
            patterns.append('Urgent or threatening language detected')
            
        # Check for credential requests
        if 'password' in text or 'login' in text:
            patterns.append('Request for sensitive information detected')
            
        # Check for common phishing phrases
        if 'verify your account' in text or 'confirm your identity' in text:
            patterns.append('Account verification request detected')
            
        # Check for pressure tactics
        if '24 hours' in text or 'limited time' in text:
            patterns.append('Time pressure tactics detected')
        
        return patterns
    
    def _analyze_urls(self, email_features):
        """Analyze URLs for suspicious patterns."""
        analysis = []
        urls = email_features.get('urls', [])
        
        for url in urls:
            url_lower = url.lower()
            
            # Check for suspicious TLDs
            if any(url_lower.endswith(tld) for tld in ['.tk', '.ml', '.ga', '.cf', '.gq']):
                analysis.append(f'Suspicious domain extension detected: {url}')
                
            # Check for URL shorteners
            if any(shortener in url_lower for shortener in ['bit.ly', 'tinyurl', 't.co']):
                analysis.append(f'URL shortener detected: {url}')
                
            # Check for HTTP instead of HTTPS
            if url_lower.startswith('http://'):
                analysis.append(f'Insecure protocol (HTTP) used: {url}')
                
            # Check for IP-based URLs
            if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                analysis.append(f'IP-based URL detected: {url}')
        
        return analysis
    
    def _get_top_features(self, email_features):
        """Get top contributing features for the prediction."""
        # This is a simplified version since we're not using the ML model yet
        features = []
        text = email_features.get('text', '').lower()
        
        feature_checks = [
            ('urgent_language', any(word in text for word in ['urgent', 'immediate', 'suspended'])),
            ('credential_request', 'password' in text or 'login' in text),
            ('threat_language', 'suspended' in text or 'terminated' in text),
            ('pressure_tactics', '24 hours' in text or 'limited time' in text)
        ]
        
        for name, present in feature_checks:
            if present:
                features.append({
                    'feature': name,
                    'importance': 0.25  # Simplified equal weighting
                })
        
        return features