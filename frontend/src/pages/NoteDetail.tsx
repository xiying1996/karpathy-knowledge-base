import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { ArrowLeft, Calendar, Tag, ExternalLink } from 'lucide-react'
import { getNote } from '../services/api'

interface NoteDetail {
  id: string
  title: string
  content: string
  path: string
  tags: string[]
  links: string[]
  created?: string
  modified?: string
}

function NoteDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [note, setNote] = useState<NoteDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    getNote(id)
      .then(res => setNote(res.data))
      .catch(() => setError('笔记不存在'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return <div className="text-center py-12 text-gray-500">加载中...</div>
  }
  if (error || !note) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">{error || '笔记不存在'}</p>
        <button onClick={() => navigate(-1)} className="text-blue-600 hover:underline">
          返回
        </button>
      </div>
    )
  }

  // Render [[wiki links]] as clickable links
  const renderContent = (content: string) => {
    const linkPattern = /\[\[([^\]]+)\]\]/g
    const parts: React.ReactNode[] = []
    let lastIndex = 0
    let match: RegExpExecArray | null

    while ((match = linkPattern.exec(content)) !== null) {
      if (match.index > lastIndex) {
        parts.push(
          <ReactMarkdown key={`text-${lastIndex}`}>
            {content.slice(lastIndex, match.index)}
          </ReactMarkdown>
        )
      }
      const linkedTitle = match[1]
      parts.push(
        <Link
          key={`link-${match.index}`}
          to={`/notes/${linkedTitle}`}
          className="text-blue-600 hover:underline mx-0.5"
        >
          {linkedTitle}
        </Link>
      )
      lastIndex = match.index + match[0].length
    }
    if (lastIndex < content.length) {
      parts.push(
        <ReactMarkdown key={`text-${lastIndex}`}>
          {content.slice(lastIndex)}
        </ReactMarkdown>
      )
    }
    return parts
  }

  return (
    <div>
      <button
        onClick={() => navigate(-1)}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        返回
      </button>

      <div className="bg-white rounded-lg shadow p-6">
        {/* Header */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{note.title}</h1>

        {/* Meta */}
        <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-6">
          {note.created && (
            <span className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {note.created}
            </span>
          )}
          {note.tags.length > 0 && (
            <span className="flex items-center gap-1">
              <Tag className="w-4 h-4" />
              {note.tags.map(tag => (
                <span key={tag} className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                  {tag}
                </span>
              ))}
            </span>
          )}
          <span className="text-gray-400 text-xs">{note.path}</span>
        </div>

        {/* Links */}
        {note.links.length > 0 && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500 mb-2">相关笔记</p>
            <div className="flex flex-wrap gap-2">
              {note.links.map(link => (
                <Link
                  key={link}
                  to={`/notes/${link}`}
                  className="text-sm text-blue-600 hover:underline flex items-center"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  {link}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="prose prose-blue max-w-none">
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {renderContent(note.content)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default NoteDetail
