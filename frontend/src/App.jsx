import ErrorBoundary from './shared/components/ErrorBoundary.jsx';
import AppRouter from './router/index.jsx';

export default function App() {
  return (
    <ErrorBoundary>
      <AppRouter />
    </ErrorBoundary>
  );
}
