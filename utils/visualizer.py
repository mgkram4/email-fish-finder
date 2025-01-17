import base64
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class ResultVisualizer:
    def __init__(self):
        self.setup_style()
    
    def setup_style(self):
        """Set up plotting style."""
        # Use a built-in matplotlib style instead of seaborn directly
        plt.style.use('default')
        # Apply seaborn defaults after importing
        sns.set_theme()
        # Set figure parameters
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['figure.dpi'] = 100
    
    def generate_dashboard_data(self, metrics):
        """Generate visualization data for the dashboard."""
        visualizations = {
            'confusion_matrix': self._plot_confusion_matrix(metrics['confusion_matrix']),
            'feature_importance': self._plot_feature_importance(metrics.get('feature_importance', [])),
            'detection_trend': self._plot_detection_trend(metrics.get('detection_history', [])),
            'accuracy_metrics': self._plot_accuracy_metrics(metrics)
        }
        
        return visualizations
    
    def _plot_confusion_matrix(self, conf_matrix):
        """Plot confusion matrix as heatmap."""
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            conf_matrix,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Legitimate', 'Phishing'],
            yticklabels=['Legitimate', 'Phishing']
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        return self._fig_to_base64()
    
    def _plot_feature_importance(self, feature_importance):
        """Plot feature importance bar chart."""
        if not feature_importance:
            return None
            
        plt.figure(figsize=(10, 6))
        df = pd.DataFrame(feature_importance).sort_values('importance', ascending=True)
        
        sns.barplot(
            data=df.tail(10),  # Show top 10 features
            y='feature',
            x='importance',
            palette='Blues_r'
        )
        plt.title('Top 10 Important Features')
        plt.xlabel('Importance Score')
        plt.ylabel('Feature')
        
        return self._fig_to_base64()
    
    def _plot_detection_trend(self, history):
        """Plot detection trend over time."""
        if not history:
            return None
            
        plt.figure(figsize=(12, 6))
        df = pd.DataFrame(history)
        
        # Plot accuracy trend
        plt.plot(df['date'], df['accuracy'], marker='o', label='Accuracy')
        plt.plot(df['date'], df['precision'], marker='s', label='Precision')
        plt.plot(df['date'], df['recall'], marker='^', label='Recall')
        
        plt.title('Detection Performance Trend')
        plt.xlabel('Date')
        plt.ylabel('Score')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        return self._fig_to_base64()
    
    def _plot_accuracy_metrics(self, metrics):
        """Plot accuracy metrics as a radar chart."""
        categories = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [
            metrics.get('accuracy', 0),
            metrics.get('precision', 0),
            metrics.get('recall', 0),
            metrics.get('f1', 0)
        ]
        
        # Create the radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # complete the loop
        angles = np.concatenate((angles, [angles[0]]))  # complete the loop
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_thetagrids(angles[:-1] * 180/np.pi, categories)
        plt.title('Performance Metrics')
        
        return self._fig_to_base64()
    
    def _fig_to_base64(self):
        """Convert matplotlib figure to base64 string."""
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode()
    
    def generate_report(self, metrics, output_file='phishing_detection_report.pdf'):
        """Generate a PDF report with all visualizations."""
        plt.figure(figsize=(12, 15))
        
        # Create a multi-page report
        plt.subplot(3, 1, 1)
        self._plot_confusion_matrix(metrics['confusion_matrix'])
        
        plt.subplot(3, 1, 2)
        self._plot_feature_importance(metrics.get('feature_importance', []))
        
        plt.subplot(3, 1, 3)
        self._plot_detection_trend(metrics.get('detection_history', []))
        
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
    
    def plot_real_time_metrics(self, metrics_queue):
        """Plot real-time metrics using animation."""
        plt.ion()  # Turn on interactive mode
        fig, ax = plt.subplots()
        
        while True:
            if not metrics_queue.empty():
                metrics = metrics_queue.get()
                
                ax.clear()
                ax.plot(metrics['timestamps'], metrics['accuracy'], label='Accuracy')
                ax.plot(metrics['timestamps'], metrics['precision'], label='Precision')
                ax.plot(metrics['timestamps'], metrics['recall'], label='Recall')
                
                ax.set_title('Real-time Detection Performance')
                ax.set_xlabel('Time')
                ax.set_ylabel('Score')
                ax.legend()
                ax.grid(True)
                
                plt.pause(1)  # Update every second