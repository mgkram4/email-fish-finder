# Email Phishing Analyzer

A Flask-based web application that analyzes email content for potential phishing attempts using feature extraction and rule-based classification.

## Features

- Real-time email content analysis
- Detection of suspicious Top-Level Domains (TLDs)
- URL shortener identification
- Multiple sender detection
- Confidence score generation
- Detailed analysis results

## Technical Stack

- Python 3.x
- Flask
- HTML/CSS/JavaScript (frontend)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/email-phishing-analyzer.git
   cd email-phishing-analyzer
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```
   pip install flask
   ```

## Usage

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Input the email content you want to analyze

4. Review the analysis results, which include:
   - Phishing probability assessment
   - Confidence score
   - Detailed breakdown of suspicious elements

## API Endpoints

### Home Page
- **Route:** `/`
- **Method:** `GET`
- **Description:** Renders the main application interface

### Email Analysis
- **Route:** `/analyze`
- **Method:** `POST`
- **Payload:**
  ```json
  {
      "email": "Email content to analyze"
  }
  ```
- **Response:**
  ```json
  {
      "is_phishing": boolean,
      "confidence": float,
      "details": {
          "urls_found": integer,
          "suspicious_tld": boolean,
          "url_shortener": boolean
      }
  }
  ```

## Error Handling

The application includes comprehensive error handling:
- Invalid requests return a 400 status code
- Server-side errors return a 500 status code
- All errors include descriptive error messages

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your chosen license here]

## Contact

[Add your contact information here]

## Acknowledgments

- Thanks to all contributors
- [Add any other acknowledgments]