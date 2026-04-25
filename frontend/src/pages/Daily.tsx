import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Plus, BookOpen, TrendingUp, ChevronRight } from 'lucide-react'
import api from '../services/api'

interface DailyNote {
  id: string
  title: string
  created: string
}

interface StreakStats {
  current_streak: number
  longest_streak: number
  total_days: number
}

function Daily() {
  const [notes, setNotes] = useState<DailyNote[]>([])
  const [stats, setStats] = useState<StreakStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [todayNote, setTodayNote] = useState<{ id: string; created: boolean } | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [notesRes, statsRes] = await Promise.all([
        api.get('/api/daily/recent'),
        api.get('/api/daily/streak'),
      ])
      setNotes(notesRes.data.notes)
      setStats(statsRes.data)

      // 检查今天是否已有笔记
      const today = new Date().toISOString().split('T')[0]
      const hasToday = notesRes.data.notes.some((n: DailyNote) => n.id === today)
      if (hasToday) {
        setTodayNote({ id: today, created: false })
      }
    } catch (err) {
      console.error('加载每日笔记失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateToday = async () => {
    setCreating(true)
    try {
      const res = await api.post('/api/daily/create', {
        use_ai_suggestion: false,
      })
      if (res.data.success) {
        setTodayNote({
          id: res.data.note_id,
          created: res.data.created,
        })
        // 刷新列表
        loadData()
      }
    } catch (err) {
      console.error('创建笔记失败:', err)
      alert('创建失败，请重试')
    } finally {
      setCreating(false)
    }
  }

  const today = new Date().toISOString().split('T')[0]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">每日笔记</h2>

      {/* 今日笔记卡片 */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center text-gray-600 mb-2">
              <Calendar className="w-5 h-5 mr-2" />
              <span className="text-lg">{today}</span>
            </div>
            <h3 className="text-xl font-semibold">
              {todayNote ? '今日笔记已创建' : '今日笔记'}
            </h3>
          </div>
          {todayNote ? (
            <Link
              to={`/notes/${todayNote.id}`}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
            >
              <BookOpen className="w-4 h-4 mr-2" />
              查看笔记
            </Link>
          ) : (
            <button
              onClick={handleCreateToday}
              disabled={creating}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              {creating ? '创建中...' : '创建今日笔记'}
            </button>
          )}
        </div>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center text-gray-600 mb-2">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-sm">连续记录</span>
            </div>
            <p className="text-2xl font-bold">{stats.current_streak} 天</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center text-gray-600 mb-2">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-sm">最长连续</span>
            </div>
            <p className="text-2xl font-bold">{stats.longest_streak} 天</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center text-gray-600 mb-2">
              <BookOpen className="w-4 h-4 mr-1" />
              <span className="text-sm">总记录天数</span>
            </div>
            <p className="text-2xl font-bold">{stats.total_days} 天</p>
          </div>
        </div>
      )}

      {/* 历史笔记列表 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="font-semibold">历史笔记</h3>
        </div>
        {loading ? (
          <div className="p-8 text-center text-gray-500">加载中...</div>
        ) : notes.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            还没有每日笔记，点击上方按钮创建第一篇
          </div>
        ) : (
          <div className="divide-y">
            {notes.map(note => (
              <Link
                key={note.id}
                to={`/notes/${note.id}`}
                className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 text-gray-400 mr-3" />
                  <div>
                    <p className="font-medium">{note.title}</p>
                    <p className="text-sm text-gray-500">{note.created}</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Daily
