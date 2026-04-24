import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { BookOpen, Search, MessageCircle } from 'lucide-react'
import Home from './pages/Home'
import SearchPage from './pages/Search'
import Chat from './pages/Chat'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold text-gray-900">Karpathy Knowledge Base</h1>
              <div className="flex space-x-6">
                <Link to="/" className="flex items-center text-gray-600 hover:text-gray-900">
                  <BookOpen className="w-4 h-4 mr-1" />
                  笔记
                </Link>
                <Link to="/search" className="flex items-center text-gray-600 hover:text-gray-900">
                  <Search className="w-4 h-4 mr-1" />
                  搜索
                </Link>
                <Link to="/chat" className="flex items-center text-gray-600 hover:text-gray-900">
                  <MessageCircle className="w-4 h-4 mr-1" />
                  AI 问答
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/chat" element={<Chat />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
