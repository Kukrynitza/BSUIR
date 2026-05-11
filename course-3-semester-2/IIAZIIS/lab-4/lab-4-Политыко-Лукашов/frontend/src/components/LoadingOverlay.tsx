import './LoadingOverlay.css';

interface LoadingOverlayProps {
  message?: string;
  visible: boolean;
}

function LoadingOverlay({ message = 'Анализ...', visible }: LoadingOverlayProps) {
  if (!visible) return null;
  
  return (
    <div className="loading-overlay">
      <div className="loading-spinner"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
}

export default LoadingOverlay;
