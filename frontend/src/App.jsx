import { useState, useEffect } from 'react';
import { useAuthStore } from './lib/store';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  const { isAuthenticated, initAuth } = useAuthStore();
  const [currentPage, setCurrentPage] = useState('chat');

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                🏥 Medical AI Agent
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentPage('chat')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentPage === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentPage === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                📊 Dashboard
              </button>
              <button
                onClick={() => useAuthStore.getState().logout()}
                className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="h-[calc(100vh-4rem)]">
        {currentPage === 'chat' ? <ChatPage /> : <DashboardPage />}
      </main>
    </div>
  );
}

export default App;
