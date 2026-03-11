import { useState, useEffect } from 'react';
import { api } from '../api/client';

function StatisticsPanel() {
  const [overview, setOverview] = useState<any>(null);
  const [wordFreq, setWordFreq] = useState<any>(null);
  const [lemmaFreq, setLemmaFreq] = useState<any>(null);
  const [posStats, setPosStats] = useState<any>(null);
  const [grammarStats, setGrammarStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeStat, setActiveStat] = useState<'overview' | 'wordforms' | 'lemmas' | 'pos' | 'grammars'>('overview');
  const [loadTime, setLoadTime] = useState<number | null>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const startTime = performance.now();
      const [overviewData, wordData, lemmaData, posData, grammarData] = await Promise.all([
        api.getOverview(),
        api.getWordFrequencies(30),
        api.getLemmaFrequencies(30),
        api.getPOSStatistics(),
        api.getGrammarStatistics(),
      ]);
      setLoadTime(performance.now() - startTime);
      console.log('Statistics load time:', loadTime, 'ms');
      setOverview(overviewData);
      setWordFreq(wordData);
      setLemmaFreq(lemmaData);
      setPosStats(posData);
      setGrammarStats(grammarData);
    } catch (err) {
      setError('Не удалось загрузить статистику');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка статистики...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="panel">
      <h2>Статистика корпуса</h2>
      {loadTime !== null && <p className="time-info">Время загрузки: {loadTime.toFixed(0)} мс</p>}

      <div className="stat-tabs">
        <button
          className={activeStat === 'overview' ? 'active' : ''}
          onClick={() => setActiveStat('overview')}
        >
          Обзор
        </button>
        <button
          className={activeStat === 'wordforms' ? 'active' : ''}
          onClick={() => setActiveStat('wordforms')}
        >
          Словоформы
        </button>
        <button
          className={activeStat === 'lemmas' ? 'active' : ''}
          onClick={() => setActiveStat('lemmas')}
        >
          Леммы
        </button>
        <button
          className={activeStat === 'pos' ? 'active' : ''}
          onClick={() => setActiveStat('pos')}
        >
          Части речи
        </button>
        <button
          className={activeStat === 'grammars' ? 'active' : ''}
          onClick={() => setActiveStat('grammars')}
        >
          Грамматика
        </button>
      </div>

      {activeStat === 'overview' && overview && (
        <div className="stat-content">
          <div className="stat-cards">
            <div className="stat-card">
              <div className="stat-value">{overview.total_documents}</div>
              <div className="stat-label">Документов</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.total_words}</div>
              <div className="stat-label">Слов</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.unique_wordforms}</div>
              <div className="stat-label">Уникальных словоформ</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overview.unique_lemmas}</div>
              <div className="stat-label">Уникальных лемм</div>
            </div>
          </div>
        </div>
      )}

      {activeStat === 'wordforms' && wordFreq && (
        <div className="stat-content">
          <h3>Частотный словарь словоформ</h3>
          <p>Всего уникальных: {wordFreq.total_unique}</p>
          <table>
            <thead>
              <tr>
                <th>Слово</th>
                <th>Частота</th>
              </tr>
            </thead>
            <tbody>
              {wordFreq.frequencies.map((item: any, idx: number) => (
                <tr key={idx}>
                  <td>{item.word}</td>
                  <td>{item.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeStat === 'lemmas' && lemmaFreq && (
        <div className="stat-content">
          <h3>Частотный словарь лемм</h3>
          <p>Всего уникальных: {lemmaFreq.total_unique}</p>
          <table>
            <thead>
              <tr>
                <th>Лемма</th>
                <th>Частота</th>
              </tr>
            </thead>
            <tbody>
              {lemmaFreq.frequencies.map((item: any, idx: number) => (
                <tr key={idx}>
                  <td>{item.lemma}</td>
                  <td>{item.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeStat === 'pos' && posStats && (
        <div className="stat-content">
          <h3>Статистика по частям речи</h3>
          <p>Всего токенов: {posStats.total}</p>
          <table>
            <thead>
              <tr>
                <th>Часть речи</th>
                <th>Количество</th>
                <th>Процент</th>
              </tr>
            </thead>
            <tbody>
              {posStats.statistics.map((item: any, idx: number) => (
                <tr key={idx}>
                  <td>{item.pos}</td>
                  <td>{item.count}</td>
                  <td>{item.percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeStat === 'grammars' && grammarStats && (
        <div className="stat-content">
          <h3>Грамматические категории</h3>
          
          {'падежи' in grammarStats && (
            <div className="grammar-section">
              <h4>Падежи</h4>
              <p>Всего: {grammarStats.падежи?.total || 0}</p>
              <ul>
                {grammarStats.падежи?.values?.map((v: any, i: number) => (
                  <li key={i}>{v.value}: {v.count} ({v.percentage}%)</li>
                ))}
              </ul>
            </div>
          )}
          
          {'числа' in grammarStats && (
            <div className="grammar-section">
              <h4>Число</h4>
              <p>Всего: {grammarStats.числа?.total || 0}</p>
              <ul>
                {grammarStats.числа?.values?.map((v: any, i: number) => (
                  <li key={i}>{v.value}: {v.count} ({v.percentage}%)</li>
                ))}
              </ul>
            </div>
          )}
          
          {'роды' in grammarStats && (
            <div className="grammar-section">
              <h4>Род</h4>
              <p>Всего: {grammarStats.роды?.total || 0}</p>
              <ul>
                {grammarStats.роды?.values?.map((v: any, i: number) => (
                  <li key={i}>{v.value}: {v.count} ({v.percentage}%)</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StatisticsPanel;
