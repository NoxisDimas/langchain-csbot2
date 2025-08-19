import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface KnowledgeBase {
  id: string;
  name: string;
  description: string | null;
  schema_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  is_processed: boolean;
  created_at: string;
  updated_at: string;
}

interface SearchResult {
  id: string;
  chunk_text: string;
  metadata: any;
  chunk_index: number;
  filename: string;
  file_type: string;
  similarity: number;
}

interface Stats {
  vectorstore: {
    collection: string;
    total_vectors: number;
  }
}

const API_BASE = (import.meta as any).env?.VITE_API_URL ? `${(import.meta as any).env.VITE_API_URL}/api/rag` : '/api/rag';

export const RAGUpload: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<string>('default');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [newKnowledgeBase, setNewKnowledgeBase] = useState({ name: '', description: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'search' | 'manage' | 'stats'>('upload');

  // Load initial data
  useEffect(() => {
    loadKnowledgeBases();
    loadDocuments();
    loadStats();
  }, []);

  const loadKnowledgeBases = async () => {
    try {
      const response = await axios.get(`${API_BASE}/knowledge-bases`);
      setKnowledgeBases(response.data);
    } catch (error) {
      console.error('Error loading knowledge bases:', error);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files ? Array.from(event.target.files) : [];
    if (files.length > 0) {
      setSelectedFiles(files);
      setUploadMessage('');
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setUploadMessage('Please select at least one file');
      return;
    }

    setUploading(true);
    setUploadMessage('');

    try {
      const uploads = selectedFiles.map(async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('knowledge_base', selectedKnowledgeBase);
        return axios.post(`${API_BASE}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      });

      const results = await Promise.allSettled(uploads);
      const successCount = results.filter(r => r.status === 'fulfilled').length;
      const failCount = results.length - successCount;
      setUploadMessage(`✅ Uploaded ${successCount} file(s)` + (failCount ? `, ❌ failed ${failCount}` : ''));
      setSelectedFiles([]);

      // Reload documents and stats
      loadDocuments();
      loadStats();

      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      setUploadMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const createKnowledgeBase = async () => {
    if (!newKnowledgeBase.name.trim()) {
      alert('Please enter a knowledge base name');
      return;
    }

    try {
      await axios.post(`${API_BASE}/knowledge-bases`, newKnowledgeBase);
      setNewKnowledgeBase({ name: '', description: '' });
      loadKnowledgeBases();
      loadStats();
      alert('Knowledge base created successfully!');
    } catch (error: any) {
      alert(`Error creating knowledge base: ${error.response?.data?.detail || error.message}`);
    }
  };

  const deleteKnowledgeBase = async (name: string) => {
    if (!confirm(`Are you sure you want to delete knowledge base "${name}"?`)) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/knowledge-bases/${name}`);
      loadKnowledgeBases();
      loadStats();
      alert('Knowledge base deleted successfully!');
    } catch (error: any) {
      alert(`Error deleting knowledge base: ${error.response?.data?.detail || error.message}`);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/documents/${documentId}`);
      loadDocuments();
      loadStats();
      alert('Document deleted successfully!');
    } catch (error: any) {
      alert(`Error deleting document: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      alert('Please enter a search query');
      return;
    }

    setSearching(true);
    try {
      const response = await axios.post(`${API_BASE}/search`, {
        query: searchQuery,
        knowledge_base: selectedKnowledgeBase === 'default' ? null : selectedKnowledgeBase,
        limit: 5
      });
      setSearchResults(response.data);
    } catch (error: any) {
      alert(`Search error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSearching(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div style={{ maxWidth: 1200, margin: '40px auto', fontFamily: 'system-ui', padding: '0 20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        RAG Knowledge Base Management
      </h1>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', marginBottom: '20px', borderBottom: '2px solid #eee' }}>
        {[
          { key: 'upload', label: 'Upload Files' },
          { key: 'search', label: 'Search' },
          { key: 'manage', label: 'Manage' },
          { key: 'stats', label: 'Statistics' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: activeTab === tab.key ? '#007bff' : 'transparent',
              color: activeTab === tab.key ? 'white' : '#333',
              cursor: 'pointer',
              borderBottom: activeTab === tab.key ? '2px solid #007bff' : 'none',
              marginRight: '10px'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div>
          <h2>Upload Documents</h2>
          
          {/* Knowledge Base Selection */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Knowledge Base:
            </label>
            <select
              value={selectedKnowledgeBase}
              onChange={(e) => setSelectedKnowledgeBase(e.target.value)}
              style={{ padding: '8px', width: '300px', borderRadius: '4px', border: '1px solid #ddd' }}
            >
              {knowledgeBases.map(kb => (
                <option key={kb.id} value={kb.name}>{kb.name}</option>
              ))}
            </select>
          </div>

          {/* File Upload */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Select File(s):
            </label>
            <input
              id="file-input"
              type="file"
              onChange={handleFileSelect}
              multiple
              accept=".pdf,.txt,.md,.csv,.xlsx,.xls,.docx,.doc,.json,.xml,.html"
              style={{ padding: '8px', width: '300px' }}
            />
            {selectedFiles.length > 0 && (
              <div style={{ marginTop: '10px', color: '#666' }}>
                Selected: {selectedFiles.length} file(s)
                <ul style={{ marginTop: 6 }}>
                  {selectedFiles.slice(0, 5).map((f) => (
                    <li key={f.name}>
                      {f.name} ({formatFileSize(f.size)})
                    </li>
                  ))}
                  {selectedFiles.length > 5 && <li>and {selectedFiles.length - 5} more...</li>}
                </ul>
              </div>
            )}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={uploading || selectedFiles.length === 0}
            style={{
              padding: '12px 24px',
              background: uploading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: uploading ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
          >
            {uploading ? 'Uploading...' : 'Upload File(s)'}
          </button>

          {/* Upload Message */}
          {uploadMessage && (
            <div style={{ 
              marginTop: '15px', 
              padding: '10px', 
              borderRadius: '4px',
              background: uploadMessage.includes('✅') ? '#d4edda' : '#f8d7da',
              color: uploadMessage.includes('✅') ? '#155724' : '#721c24',
              border: `1px solid ${uploadMessage.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`
            }}>
              {uploadMessage}
            </div>
          )}

          {/* Supported File Types */}
          <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '4px' }}>
            <h4>Supported File Types:</h4>
            <p>PDF, TXT, Markdown, CSV, Excel (XLSX/XLS), Word (DOCX/DOC), JSON, XML, HTML</p>
          </div>
        </div>
      )}

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div>
          <h2>Search Documents</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter your search query..."
              style={{ 
                padding: '12px', 
                width: '400px', 
                borderRadius: '4px', 
                border: '1px solid #ddd',
                marginRight: '10px'
              }}
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              style={{
                padding: '12px 24px',
                background: searching ? '#ccc' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: searching ? 'not-allowed' : 'pointer'
              }}
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div>
              <h3>Search Results ({searchResults.length})</h3>
              {searchResults.map((result, index) => (
                <div key={result.id} style={{ 
                  marginBottom: '15px', 
                  padding: '15px', 
                  border: '1px solid #ddd', 
                  borderRadius: '4px',
                  background: '#f9f9f9'
                }}>
                  <div style={{ marginBottom: '10px' }}>
                    <strong>File:</strong> {result.filename} ({result.file_type})
                    <br />
                    <strong>Similarity:</strong> {(result.similarity * 100).toFixed(2)}%
                    <br />
                    <strong>Chunk Index:</strong> {result.chunk_index}
                  </div>
                  <div style={{ 
                    padding: '10px', 
                    background: 'white', 
                    borderRadius: '4px',
                    border: '1px solid #eee'
                  }}>
                    {result.chunk_text}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Manage Tab */}
      {activeTab === 'manage' && (
        <div>
          <h2>Manage Knowledge Base</h2>
          
          {/* Create New Knowledge Base */}
          <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '4px' }}>
            <h3>Create New Knowledge Base</h3>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'end' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
                <input
                  type="text"
                  value={newKnowledgeBase.name}
                  onChange={(e) => setNewKnowledgeBase({...newKnowledgeBase, name: e.target.value})}
                  placeholder="Enter knowledge base name"
                  style={{ padding: '8px', width: '200px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px' }}>Description:</label>
                <input
                  type="text"
                  value={newKnowledgeBase.description}
                  onChange={(e) => setNewKnowledgeBase({...newKnowledgeBase, description: e.target.value})}
                  placeholder="Enter description (optional)"
                  style={{ padding: '8px', width: '300px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
              <button
                onClick={createKnowledgeBase}
                style={{
                  padding: '8px 16px',
                  background: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Create
              </button>
            </div>
          </div>

          {/* Knowledge Bases List */}
          <div style={{ marginBottom: '30px' }}>
            <h3>Knowledge Bases</h3>
            {knowledgeBases.map(kb => (
              <div key={kb.id} style={{ 
                padding: '15px', 
                border: '1px solid #ddd', 
                borderRadius: '4px',
                marginBottom: '10px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <strong>{kb.name}</strong>
                  {kb.description && <div style={{ color: '#666', fontSize: '14px' }}>{kb.description}</div>}
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    Schema: {kb.schema_name} | Created: {new Date(kb.created_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={() => deleteKnowledgeBase(kb.name)}
                  style={{
                    padding: '6px 12px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>

          {/* Documents List */}
          <div>
            <h3>Documents</h3>
            
            {documents.map(doc => (
              <div key={doc.id} style={{ 
                padding: '15px', 
                border: '1px solid #ddd', 
                borderRadius: '4px',
                marginBottom: '10px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <strong>{doc.filename}</strong>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    Type: {doc.file_type} | Size: {formatFileSize(doc.file_size)} | 
                    Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={() => deleteDocument(doc.id)}
                  style={{
                    padding: '6px 12px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div>
          <h2>Vectorstore Statistics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
            <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'center' }}>
              <h3>Collection</h3>
              <div style={{ fontSize: '1.2em', color: '#007bff' }}>{stats.vectorstore.collection}</div>
            </div>
            <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'center' }}>
              <h3>Total Vectors</h3>
              <div style={{ fontSize: '2em', color: '#28a745' }}>{stats.vectorstore.total_vectors}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};