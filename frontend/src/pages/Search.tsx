import { useState } from 'react'
import { Search } from 'lucide-react'
import { searchNotes } from '../services/api'

function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    try {
      const res = await searchNotes(query)
      setResults(res.data.results)
    } catch (err) {
      console.error(err)
    }
    setSearching(false)
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
      {results.length > 0 ? (
        <div className="space-y-4">
          {results.map(result => (
            <div key={result.id} className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-semibold">{result.title}</h3>
              <p className="text-gray-600 mt-2 text-sm">{result.snippet}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-center py-8">输入问题开始搜索</p>
      )}
    </div>
  )
}

export default SearchPage
