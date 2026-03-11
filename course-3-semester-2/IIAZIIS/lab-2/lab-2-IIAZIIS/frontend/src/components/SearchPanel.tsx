import { useState } from 'react';
import { api, ConcordanceItem } from '../api/client';

function SearchPanel() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [concordance, setConcordance] = useState<ConcordanceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchType, setSearchType] = useState<'search' | 'concordance'>('search');
  const [concordanceTime, setConcordanceTime] = useState<number | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError('');
      
      if (searchType === 'search') {
        const startTime = performance.now();
        const results = await api.search(query);
        setSearchTime(performance.now() - startTime);
        console.log('Search results:', results);
        setSearchResults(results.results || []);
      } else {
        const startTime = performance.now();
        const results = await api.getConcordance(query);
        const elapsed = performance.now() - startTime;
        setConcordanceTime(elapsed);
        console.log('Concordance results:', results);
        setConcordance(results.concordance || []);
      }
    } catch (err) {
      setError('Ошибка поиска');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="panel">
      <h2>Поиск по корпусу</h2>

      <div className="search-type-tabs">
        <button
          className={searchType === 'search' ? 'active' : ''}
          onClick={() => setSearchType('search')}
        >
          Простой поиск
        </button>
        <button
          className={searchType === 'concordance' ? 'active' : ''}
          onClick={() => setSearchType('concordance')}
        >
          Конкорданс
        </button>
      </div>

      <div className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Введите слово для поиска..."
          className="search-input"
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {searchType === 'search' && (
        <div className="search-results">
          <h3>Результаты поиска ({searchResults.length}){searchTime !== null && <span className="time-info"> — {searchTime.toFixed(0)} мс</span>}</h3>
          {searchResults.length === 0 ? (
            <p>Введите запрос и нажмите "Найти"</p>
          ) : (
            <ul className="results-list">
              {searchResults.map((result, idx) => (
                <li key={idx} className="result-item">
                  <div className="result-doc">{result.document_title}</div>
                  <div className="result-context">{result.context}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {searchType === 'concordance' && (
        <div className="concordance-results">
          <h3>Конкорданс ({concordance.length}){concordanceTime !== null && <span className="time-info"> — {concordanceTime.toFixed(0)} мс</span>}</h3>
          {concordance.length === 0 ? (
            <p>Введите слово и нажмите "Найти"</p>
          ) : (
            <div className="kwic-list">
              {concordance.map((item, idx) => (
                <div key={idx} className="kwic-item">
                  <span className="kwic-left">{item.left}</span>
                  <span className="kwic-keyword">{item.keyword}</span>
                  <span className="kwic-right">{item.right}</span>
                  <span className="kwic-doc">[{item.document}]</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchPanel;
