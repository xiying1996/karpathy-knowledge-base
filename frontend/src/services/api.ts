import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
})

export interface Note {
  id: string
  title: string
  content: string
  path: string
  tags: string[]
  links: string[]
  created?: string
  modified?: string
}

export interface SearchResult {
  id: string
  title: string
  snippet: string
  score: number
}

export const getNotes = () => api.get<{ notes: Note[]; total: number }>('/api/notes')

export const getNote = (id: string) => api.get<Note>(`/api/notes/${id}`)

export const searchNotes = (query: string, limit = 10) =>
  api.post<{ results: SearchResult[]; query: string }>('/api/search', { query, limit })

export const ragAsk = (question: string, context_limit = 5) =>
  api.post<{ answer: string; sources: string[] }>('/api/rag/ask', { question, context_limit })

export default api
