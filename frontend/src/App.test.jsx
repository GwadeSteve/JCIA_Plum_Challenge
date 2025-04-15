import { BrowserRouter as Router } from 'react-router-dom';
import { render } from '@testing-library/react';
import App from './App';

jest.mock('aos', () => ({
  init: jest.fn(),
  refresh: jest.fn()
}));


test('renders app without crashing', () => {
  const { container } = render(
    <Router>
      <App />
    </Router>
  );
  
  expect(container).toBeDefined();
});