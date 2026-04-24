import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, AlertCircle } from 'lucide-react'
import { searchNotes } from '../services/api'
import type { SearchResult } from '../services/api'

function highlightMatch(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text
  const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'))
  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase() ? <mark key={i} className="bg-yellow-200">{part}</mark> : part
  )
}

function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    setError(null)
    try {
      const res = await searchNotes(query)
      setResults(res.data.results)
      setHasSearched(true)
    } catch (err) {
      setError('搜索失败，请稍后重试')
      setResults([])
    } finally {
      setSearching(false)
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">语义搜索</h2>
      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="输入问题进行语义搜索..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={searching}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            <Search className="w-4 h-4 mr-2" />
            {searching ? '搜索中...' : '搜索'}
          </button>
        </div>
      </form>
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
          {error}
        </div>
      )}
      {results.length > 0 ? (
        <div className="space-y-4">
          {results.map(result => (
            <Link key={result.id} to={`/notes/${result.id}`} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition block">
              <h3 className="font-semibold text-gray-900">{result.title}</h3>
              <p className="text-gray-600 mt-2 text-sm">{highlightMatch(result.snippet, query)}</p>
              <p className="text-xs text-gray-400 mt-2">相关度 {Math.round(result.score * 100)}%</p>
            </Link>
          ))}
        </div>
      ) : hasSearched ? (
        <p className="text-gray-500 text-center py-8">未找到相关结果</p>
      ) : (
        <p className="text-gray-500 text-center py-8">输入问题开始搜索</p>
      )}
    </div>
  )
}

export default SearchPage
