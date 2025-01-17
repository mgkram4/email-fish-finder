import email
from email import policy
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class EmailParser:
    def __init__(self):
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
    
    def parse(self, email_content):
        """Parse email content and extract relevant features."""
        # Parse email message
        if isinstance(email_content, str):
            msg = email.message_from_string(email_content, policy=policy.default)
        else:
            msg = email.message_from_bytes(email_content, policy=policy.default)
        
        # Extract features
        features = {
            'headers': self._extract_headers(msg),
            'text': self._extract_text(msg),
            'urls': self._extract_urls(msg),
            'attachments': self._extract_attachments(msg),
            'metadata': self._extract_metadata(msg)
        }
        
        return features
    
    def _extract_headers(self, msg):
        """Extract and analyze email headers."""
        headers = {
            'from': str(msg['from']),
            'to': str(msg['to']),
            'subject': str(msg['subject']),
            'date': str(msg['date']),
            'reply-to': str(msg.get('reply-to', '')),
            'return-path': str(msg.get('return-path', '')),
            'message-id': str(msg.get('message-id', '')),
            'x-mailer': str(msg.get('x-mailer', '')),
            'received': self._parse_received_headers(msg)
        }
        
        return headers
    
    def _parse_received_headers(self, msg):
        """Parse and analyze Received headers for email routing information."""
        received_headers = msg.get_all('received', [])
        parsed_received = []
        
        for header in received_headers:
            parsed_received.append({
                'from': self._extract_received_from(header),
                'by': self._extract_received_by(header),
                'timestamp': self._extract_received_timestamp(header)
            })
        
        return parsed_received
    
    def _extract_text(self, msg):
        """Extract text content from email body."""
        text_content = []
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    text_content.append(part.get_content())
                elif part.get_content_type() == 'text/html':
                    soup = BeautifulSoup(part.get_content(), 'html.parser')
                    text_content.append(soup.get_text())
        else:
            if msg.get_content_type() == 'text/plain':
                text_content.append(msg.get_content())
            elif msg.get_content_type() == 'text/html':
                soup = BeautifulSoup(msg.get_content(), 'html.parser')
                text_content.append(soup.get_text())
        
        return '\n'.join(text_content)
    
    def _extract_urls(self, msg):
        """Extract and analyze URLs from email content."""
        urls = set()
        
        # Extract from text content
        text_content = self._extract_text(msg)
        urls.update(self.url_pattern.findall(text_content))
        
        # Extract from HTML content
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    soup = BeautifulSoup(part.get_content(), 'html.parser')
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if href:
                            urls.add(href)
        
        return list(urls)
    
    def _extract_attachments(self, msg):
        """Extract information about email attachments."""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        'filename': filename,
                        'content_type': part.get_content_type(),
                        'size': len(part.get_payload())
                    })
        
        return attachments
    
    def _extract_metadata(self, msg):
        """Extract additional metadata from email."""
        metadata = {
            'content_type': msg.get_content_type(),
            'charset': msg.get_content_charset(),
            'content_transfer_encoding': msg.get('Content-Transfer-Encoding', ''),
            'spf': msg.get('Received-SPF', ''),
            'dkim': msg.get('DKIM-Signature', ''),
            'authentication_results': msg.get('Authentication-Results', '')
        }
        
        return metadata
    
    def _extract_received_from(self, header):
        """Extract 'from' information from Received header."""
        from_match = re.search(r'from\s+([^\s]+)', header)
        return from_match.group(1) if from_match else ''
    
    def _extract_received_by(self, header):
        """Extract 'by' information from Received header."""
        by_match = re.search(r'by\s+([^\s]+)', header)
        return by_match.group(1) if by_match else ''
    
    def _extract_received_timestamp(self, header):
        """Extract timestamp from Received header."""
        timestamp_match = re.search(r';(.+)$', header)
        return timestamp_match.group(1).strip() if timestamp_match else ''