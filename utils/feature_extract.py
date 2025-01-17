import re
from urllib.parse import urlparse


class FeatureExtractor:
    def __init__(self):
        # Core suspicious indicators
        self.suspicious_tlds = {'tk', 'ml', 'ga', 'cf', 'gq', 'xyz'}
        self.url_shorteners = {'bit.ly', 'tinyurl.com', 't.co', 'goo.gl'}
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def extract(self, email_content):
        """Extract core features from email content."""
        # Split into headers and body
        headers = {}
        body = email_content
        
        # Basic header extraction
        if '\n\n' in email_content:
            header_text, body = email_content.split('\n\n', 1)
            for line in header_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.lower().strip()] = value.strip()

        # Extract URLs
        urls = self.url_pattern.findall(email_content)
        
        features = {
            'text': body,
            'urls': urls,
            'url_count': len(urls),
            'has_suspicious_tld': 0,
            'has_url_shortener': 0,
            'has_multiple_from': 1 if headers.get('from', '').count('@') > 1 else 0
        }

        # Check URLs for suspicious patterns
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                tld = domain.split('.')[-1] if '.' in domain else ''
                
                if tld in self.suspicious_tlds:
                    features['has_suspicious_tld'] = 1
                if domain in self.url_shorteners:
                    features['has_url_shortener'] = 1
            except:
                continue

        return features