import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('🚨 React Error Boundary caught an error:', error);
    console.error('🚨 Error Info:', errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>🚨 Something went wrong</h2>
          <p>The extension encountered an error. Please check the console for details.</p>
          <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', marginTop: '10px' }}>
            <summary>Error Details</summary>
            <br />
            <strong>Error:</strong> {this.state.error && this.state.error.toString()}
            <br />
            <strong>Stack Trace:</strong>
            <br />
            {this.state.errorInfo.componentStack}
          </details>
          <button 
            onClick={() => window.location.reload()} 
            style={{ marginTop: '10px', padding: '5px 10px' }}
          >
            Reload Extension
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;