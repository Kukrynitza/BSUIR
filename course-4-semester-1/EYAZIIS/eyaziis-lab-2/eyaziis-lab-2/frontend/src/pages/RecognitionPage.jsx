import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

const METHOD_LABELS = {
  short_words: 'Коротких слов',
  frequent_words: 'Частотных слов',
  neural_network: 'Нейросетевой',
}

function languageBadge(language) {
  const german = language === 'немецкий'
  return (
    <span className={`language-badge ${german ? 'lang-german' : 'lang-russian'}`}>
      {german ? 'Немецкий' : language === 'русский' ? 'Русский' : language}
    </span>
  )
}

export default function RecognitionPage() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const run = async (event) => {
    event?.preventDefault()
    if (!file) {
      setError('Выберите PDF-файл')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const data = await api.recognize(formData)
      setResult(data)
      setMessage(`Распознан язык: ${data.detected_language}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const methods = Object.entries(result?.results || {}).filter(([, data]) => data && data.language)

  return (
    <>
      <div className="card">
        <h2>Распознавание языка PDF-документа</h2>
        <p className="muted">
          Загрузите документ формата PDF на русском или немецком языке. Система построит поисковый
          образ документа и сравнит его с профилями языков тремя методами.
        </p>
        <form className="search-bar" onSubmit={run}>
          <input type="file" accept=".pdf,application/pdf" onChange={(event) => setFile(event.target.files[0])} />
          <button type="submit" disabled={loading}>
            {loading ? 'Распознавание...' : 'Распознать'}
          </button>
        </form>
      </div>

      {error && <div className="notice error">{error}</div>}
      {message && <div className="notice success">{message}</div>}

      {result && (
        <>
          <div className="card">
            <h2>Результат</h2>
            <p>
              Детектированный язык: {languageBadge(result.detected_language)} с уверенностью{' '}
              {((result.confidence || 0) * 100).toFixed(1)}%
            </p>
            <p>Длина текста: {result.text_length} символов</p>
            <p>
              Документ сохранён:{' '}
              <Link to={`/documents/${result.document_id}`}>{result.title}</Link>
            </p>
          </div>

          <div className="card">
            <h2>Сравнение методов</h2>
            <table>
              <thead>
                <tr>
                  <th>Метод</th>
                  <th>Язык</th>
                  <th className="num">Уверенность</th>
                  <th className="num">ОоП</th>
                  <th className="num">Время, мс</th>
                </tr>
              </thead>
              <tbody>
                {methods.map(([key, data]) => (
                  <tr key={key}>
                    <td>{METHOD_LABELS[key] || key}</td>
                    <td>{languageBadge(data.language)}</td>
                    <td className="num">{Number(data.confidence || 0).toFixed(3)}</td>
                    <td className="num">{data.oop == null ? '—' : Number(data.oop).toFixed(0)}</td>
                    <td className="num">{data.elapsed_ms ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="muted">Время метода включает предобработку текста. Кэш лемм сбрасывается перед каждым методом, чтобы сравнение было честным.</p>
          </div>
        </>
      )}
    </>
  )
}
