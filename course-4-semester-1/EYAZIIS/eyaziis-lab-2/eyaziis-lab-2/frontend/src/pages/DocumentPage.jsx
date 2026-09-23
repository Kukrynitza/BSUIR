import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api.js'

const METHOD_LABELS = {
  short_words: 'Коротких слов',
  frequent_words: 'Частотных слов',
  neural_network: 'Нейросетевой',
}

export default function DocumentPage() {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.document(id).then(setDocument).catch((err) => setError(err.message))
  }, [id])

  if (error) return <div className="notice error">{error}</div>
  if (!document) return <div className="card">Загрузка документа...</div>

  const results = document.result_json || {}
  const methods = Object.entries(results).filter(([, data]) => data && data.language)

  return (
    <>
      <div className="card">
        <h2>{document.title}</h2>
        <div className="meta">
          <span>Идентификатор: {document.id}</span>
          <span>Дата: {document.created_at}</span>
          <span>Длина: {document.doc_len} слов</span>
          {document.source_file && <span>Файл: {document.source_file}</span>}
          <span>
            Источник:{' '}
            <span className={`source-badge ${document.source_kind === 'etalon' ? 'source-etalon' : 'source-upload'}`}>
              {document.source_kind === 'etalon' ? 'эталон (qrels.json)' : 'загруженный PDF'}
            </span>
          </span>
        </div>
        <p>
          Определённый язык:{' '}
          <span className={`language-badge ${document.detected_language === 'немецкий' ? 'lang-german' : 'lang-russian'}`}>
            {document.detected_language}
          </span>
        </p>
      </div>

      <div className="card">
        <h2>Результаты идентификации</h2>
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
                <td>{data.language}</td>
                <td className="num">{Number(data.confidence || 0).toFixed(3)}</td>
                <td className="num">{data.oop == null ? '—' : Number(data.oop).toFixed(0)}</td>
                <td className="num">{data.elapsed_ms ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted">Время метода включает предобработку текста (токенизация и лемматизация). Нейросеть считает свои N-граммы отдельно.</p>
      </div>

      <div className="card">
        <h2>Текст документа</h2>
        <div className="doc-text">{document.body}</div>
      </div>

      <div className="no-print">
        <Link to="/documents">← К списку документов</Link>
      </div>
    </>
  )
}
