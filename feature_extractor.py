def _extract_header_features(self, email_content):
    """Extract features from email headers."""
    features = {
        'has_subject': 0,
        'has_reply_to': 0,
        'has_multiple_from': 0,
        'has_multiple_to': 0
    }
    
    # Split email into headers and body
    headers = {}
    header_lines = [line for line in email_content.split('\n') if ':' in line]
    
    for line in header_lines:
        try:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            headers[key] = value
        except ValueError:
            continue
    
    # Check for common headers
    features['has_subject'] = 1 if 'subject' in headers else 0
    features['has_reply_to'] = 1 if 'reply-to' in headers else 0
    
    # Check for multiple addresses
    if 'from' in headers:
        features['has_multiple_from'] = 1 if headers['from'].count('@') > 1 else 0
    if 'to' in headers:
        features['has_multiple_to'] = 1 if headers['to'].count('@') > 1 else 0
    
    return features 