import { useState, useEffect } from 'react'
import { BookOpen } from 'lucide-react'
import { getNotes } from '../services/api'

interface Note {
  id: string
  title: string
  path: string
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

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">我的笔记</h2>
      {notes.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <BookOpen className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">暂无笔记</p>
          <p className="text-gray-400 text-sm mt-2">在 Obsidian Vault 中添加笔记后会自动同步</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {notes.map(note => (
            <div key={note.id} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition">
              <h3 className="font-semibold text-gray-900">{note.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{note.path}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Home
