import { AuthProvider } from './context/AuthContext';
import { Site } from './layouts/Site';
import './styles/index.css';
export default function App() {
  return (
    <AuthProvider>
      <Site />
    </AuthProvider>
  );
}
