const API_BASE = 'http://127.0.0.1:8001/api';

export interface DocumentMeta {
  source: string;
  text_type: string;
  word_count: number;
  char_count: number;
  created_at: string;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  metadata: DocumentMeta;
}

export interface WordFrequency {
  word: string;
  count: number;
}

export interface LemmaFrequency {
  lemma: string;
  count: number;
}

export interface ConcordanceItem {
  left: string;
  keyword: string;
  right: string;
  document: string;
}

export const api = {
  async getDocuments(): Promise<{ documents: any[]; total: number }> {
    const res = await fetch(`${API_BASE}/corpus`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async loadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/corpus/load`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to load file');
    return res.json();
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/corpus/${docId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  async getDocument(docId: string): Promise<Document> {
    const res = await fetch(`${API_BASE}/corpus/${docId}`);
    if (!res.ok) throw new Error('Failed to fetch document');
    return res.json();
  },

  async getWordFrequencies(limit: number = 50): Promise<{ frequencies: WordFrequency[] }> {
    const res = await fetch(`${API_BASE}/stats/wordforms?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch word frequencies');
    return res.json();
  },

  async getLemmaFrequencies(limit: number = 50): Promise<{ frequencies: LemmaFrequency[] }> {
    const res = await fetch(`${API_BASE}/stats/lemmas?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch lemma frequencies');
    return res.json();
  },

  async getPOSStatistics(): Promise<any> {
    const res = await fetch(`${API_BASE}/stats/pos`);
    if (!res.ok) throw new Error('Failed to fetch POS statistics');
    return res.json();
  },

  async getGrammarStatistics(): Promise<any> {
    const res = await fetch(`${API_BASE}/stats/grammars`);
    if (!res.ok) throw new Error('Failed to fetch grammar statistics');
    return res.json();
  },

  async getOverview(): Promise<any> {
    const res = await fetch(`${API_BASE}/stats/overview`);
    if (!res.ok) throw new Error('Failed to fetch overview');
    return res.json();
  },

  async search(query: string): Promise<any> {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to search');
    return res.json();
  },

  async updateDocument(docId: string, content: string): Promise<Document> {
    const res = await fetch(`${API_BASE}/corpus/${docId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error('Failed to update document');
    return res.json();
  },

  async getConcordance(query: string, context: number = 5): Promise<any> {
    const res = await fetch(`${API_BASE}/concordance?q=${encodeURIComponent(query)}&context=${context}`);
    if (!res.ok) throw new Error('Failed to get concordance');
    return res.json();
  },

  async getHelp(): Promise<any> {
    const res = await fetch(`${API_BASE}/help`);
    if (!res.ok) throw new Error('Failed to fetch help');
    return res.json();
  },

  async getTerms(): Promise<any> {
    const res = await fetch(`${API_BASE}/help/terms`);
    if (!res.ok) throw new Error('Failed to fetch terms');
    return res.json();
  },

  async healthCheck(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('API not available');
    return res.json();
  },
};
