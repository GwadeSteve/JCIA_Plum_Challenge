import { BrowserRouter as Router } from 'react-router-dom';
  import { render } from '@testing-library/react';
  import App from './App';

  jest.mock('react-fast-marquee', () => {
    return {
      __esModule: true,
      default: ({ children }) => <div>{children}</div>,
    };
  });
  
  test('renders learn react link', () => {
      render(
          <Router>
              <App />
          </Router>
      );
  });
  