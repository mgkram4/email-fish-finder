from flask import Flask, jsonify, render_template, request

from utils.feature_extract import FeatureExtractor

app = Flask(__name__)
feature_extractor = FeatureExtractor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_email():
    try:
        email_content = request.json.get('email')
        if not email_content:
            return jsonify({'error': 'No email content provided'}), 400

        # Extract features
        features = feature_extractor.extract(email_content)
        
        # Simple rule-based classification
        is_suspicious = (
            
            features['has_suspicious_tld'] or 
            features['has_url_shortener'] or 
            features['has_multiple_from']
        )
        
        return jsonify({
            'is_phishing': is_suspicious,
            'confidence': 0.8 if is_suspicious else 0.2,
            'details': {
                'urls_found': features['url_count'],
                'suspicious_tld': features['has_suspicious_tld'],
                'url_shortener': features['has_url_shortener']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)