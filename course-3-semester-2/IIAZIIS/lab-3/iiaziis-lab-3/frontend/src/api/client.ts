const API_BASE = '/api';

export interface Document {
  id: string;
  title: string;
  content: string;
  metadata: {
    source: string;
    author: string;
    date: string;
    genre: string;
    text_type: string;
    word_count: number;
    char_count: number;
    created_at: string;
  };
}

export interface Token {
  id: number;
  document_id: string;
  sentence_id: number;
  token_index: number;
  token_text: string;
  lemma: string;
  pos: string;
  pos_name: string;
  case: string;
  case_name: string;
  number: string;
  number_name: string;
  gender: string;
  gender_name: string;
  tense: string;
  person: string;
  animacy: string;
  syntax_role: string;
  syntax_role_name: string;
  position: number;
}

export interface SyntaxRelation {
  id: number;
  sentence_id: number;
  from_token_id: number;
  to_token_id: number;
  from_token_text: string;
  to_token_text: string;
  relation_type: string;
  relation_name: string;
  description: string;
}

export interface Sentence {
  id: number;
  document_id: string;
  sentence_index: number;
  sentence_text: string;
  created_at: string;
  tokens: Token[];
  relations: SyntaxRelation[];
}

export interface AnalysisResult {
  document_id: string;
  analysis: Sentence[];
  statistics: {
    total_sentences: number;
    total_tokens: number;
    pos_distribution: Record<string, number>;
    syntax_role_distribution: Record<string, number>;
  };
  analysis_time_ms?: number;
}

export interface RelationsResult {
  document_id: string;
  relations: {
    sentence_index: number;
    sentence_text: string;
    relation: SyntaxRelation;
  }[];
}

export const api = {
  async getDocuments(): Promise<{ documents: Document[]; total: number }> {
    const res = await fetch(`${API_BASE}/documents`);
    return res.json();
  },

  async loadFile(file: File): Promise<{ document: { id: string; title: string } }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents/load`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to load file');
    return res.json();
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  async analyzeDocument(docId: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/documents/${docId}/analyze`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to analyze document');
    return res.json();
  },

  async getDocumentAnalysis(docId: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/documents/${docId}/analysis`);
    if (!res.ok) throw new Error('Failed to get analysis');
    return res.json();
  },

  async getDocumentRelations(docId: string): Promise<RelationsResult> {
    const res = await fetch(`${API_BASE}/documents/${docId}/relations`);
    if (!res.ok) throw new Error('Failed to get relations');
    return res.json();
  },

  async analyzeText(text: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/text/analyze?text=${encodeURIComponent(text)}`);
    if (!res.ok) throw new Error('Failed to analyze text');
    return res.json();
  },

  async updateToken(docId: string, sentenceId: number, tokenId: number, syntaxRole: string, syntaxRoleName: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${docId}/token`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        sentence_id: sentenceId, 
        token_id: tokenId, 
        syntax_role: syntaxRole,
        syntax_role_name: syntaxRoleName
      }),
    });
    if (!res.ok) throw new Error('Failed to update token');
  },

  async updateDocument(docId: string, content: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error('Failed to update document');
    return res.json();
  },
};
