import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, FileText, Tag } from 'lucide-react'
import { getNotes } from '../services/api'

interface Note {
  id: string
  title: string
  path: string
  tags?: string[]
}

function Home() {
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getNotes().then(res => {
      setNotes(res.data.notes)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-12 text-gray-500">加载中...</div>
  }

  const totalTags = new Set(notes.flatMap(n => n.tags || [])).size

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">我的笔记</h2>
      <div className="grid gap-4 md:grid-cols-3 mb-8">
        <div className="bg-white p-4 rounded-lg shadow flex items-center">
          <FileText className="w-8 h-8 text-blue-600 mr-3" />
          <div>
            <p className="text-2xl font-bold">{notes.length}</p>
            <p className="text-sm text-gray-500">笔记总数</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow flex items-center">
          <BookOpen className="w-8 h-8 text-green-600 mr-3" />
          <div>
            <p className="text-2xl font-bold">{notes.filter(n => n.path.includes('demo')).length}</p>
            <p className="text-sm text-gray-500">演示笔记</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow flex items-center">
          <Tag className="w-8 h-8 text-purple-600 mr-3" />
          <div>
            <p className="text-2xl font-bold">{totalTags}</p>
            <p className="text-sm text-gray-500">标签总数</p>
          </div>
        </div>
      </div>
      {notes.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <BookOpen className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">暂无笔记</p>
          <p className="text-gray-400 text-sm mt-2">在 Obsidian Vault 中添加笔记后会自动同步</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {notes.map(note => (
            <Link key={note.id} to={`/notes/${note.id}`} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition block">
              <h3 className="font-semibold text-gray-900">{note.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{note.path}</p>
              {note.tags && note.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {note.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default Home
