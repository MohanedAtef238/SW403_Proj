import { useState, useEffect } from 'react';
import { ShieldCheck } from 'lucide-react';
import { Header } from './components/Header';
import { Sidebar, ChunkingStrategy } from './components/Sidebar';
import { QueryInput } from './components/QueryInput';
import { ResultsPanel } from './components/ResultsPanel';
import { QueryResult, ResultTab } from './types';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [strategy, setStrategy] = useState<ChunkingStrategy>('function');
  const [topK, setTopK] = useState(3);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [selectedDatabase, setSelectedDatabase] = useState<string | null>(null);

  const [query, setQuery] = useState('');
  const [currentResult, setCurrentResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isSelfChecking, setIsSelfChecking] = useState(false);
  const [activeTab, setActiveTab] = useState<ResultTab>('answer');


  useEffect(() => {
    const initialize = async () => {
      try {
        const healthRes = await fetch(`${API_BASE}/health`);
        setIsHealthy(healthRes.ok);

        const configRes = await fetch(`${API_BASE}/config`);
        if (configRes.ok) {
          const data = await configRes.json();
          if (data.chunking_strategy) setStrategy(data.chunking_strategy as ChunkingStrategy);
          if (data.retrieval_k) setTopK(data.retrieval_k);
        }
      } catch (error) {
        setIsHealthy(false);
        console.error('Initialization failed:', error);
      }
    };

    initialize();
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        setIsHealthy(res.ok);
      } catch {
        setIsHealthy(false);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleUpdateSettings = async () => {
    try {
      await fetch(`${API_BASE}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chunking_strategy: strategy,
          retrieval_k: topK
        })
      });
    } catch (error) {
      console.error('Failed to update backend config:', error);
    }
  };

  const handleRunQuery = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setActiveTab('answer');

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          strategy: strategy,
          k: topK,
          collection: selectedDatabase
        })
      });

      if (!response.ok) {
        const error = await response.json();
        console.error('Query failed:', error);
        setIsLoading(false);
        return;
      }

      const data = await response.json();

      const result: QueryResult = {
        strategy: data.strategy_used as any,
        answer: data.answer,
        context: data.retrieved_chunks.map((chunk: any, idx: number) => ({
          id: `chunk-${idx}`,
          content: chunk.content,
          filePath: chunk.source,
          language: 'python',
          startLine: chunk.start_line || 0,
          endLine: chunk.end_line || 0,
        })),
        reasoning: [],
      };

      setCurrentResult(result);
    } catch (error) {
      console.error('Query error:', error);
    }

    setIsLoading(false);
  };

  const handleSelfCheck = async () => {
    if (!currentResult || !selectedDatabase) return;

    setIsSelfChecking(true);

    try {
      const response = await fetch(`${API_BASE}/selfcheck`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          response: currentResult.answer,
          collection: selectedDatabase,
          k: topK
        })
      });

      if (!response.ok) {
        const error = await response.json();
        console.error('Self-check failed:', error);
        setIsSelfChecking(false);
        return;
      }

      const data = await response.json();

      // Update the result with self-check reasoning
      setCurrentResult({
        ...currentResult,
        reasoning: [{
          similarityScore: data.similarity_score,
          description: data.is_hallucinating
            ? 'The sampled response differs significantly from the original answer, suggesting potential hallucination.'
            : 'The sampled response is consistent with the original answer, indicating a reliable response.',
          isHallucinating: data.is_hallucinating
        }]
      });

      // Switch to the Self Check tab
      setActiveTab('reasoning');
    } catch (error) {
      console.error('Self-check error:', error);
    }

    setIsSelfChecking(false);
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/index/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        console.error('Upload failed:', error.detail);
      } else {
        const data = await response.json();
        console.log('Indexed:', data.message, 'Collection:', data.collection_name);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
    setIsUploading(false);
  };

  const canSelfCheck = currentResult && selectedDatabase && !isLoading && !isSelfChecking;

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      <Header
        isHealthy={isHealthy}
        selectedDatabase={selectedDatabase}
        onDatabaseChange={setSelectedDatabase}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          strategy={strategy}
          onStrategyChange={setStrategy}
          topK={topK}
          onTopKChange={setTopK}
          onSave={handleUpdateSettings}
          onUpload={handleUpload}
          isUploading={isUploading}
        />

        <div className="flex-1 flex flex-col overflow-hidden">
          <QueryInput
            query={query}
            onQueryChange={setQuery}
            onRunQuery={handleRunQuery}
            isLoading={isLoading}
          />

          <div className="flex items-center justify-between px-6 py-3 bg-gray-900 border-b border-gray-800">
            <h2 className="text-sm font-semibold text-white">
              Query Results
            </h2>
            <button
              onClick={handleSelfCheck}
              disabled={!canSelfCheck}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${canSelfCheck
                ? 'bg-purple-600 text-white hover:bg-purple-500'
                : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                }`}
            >
              <ShieldCheck className="w-4 h-4" />
              {isSelfChecking ? 'Checking...' : 'Self Check'}
            </button>
          </div>

          <ResultsPanel
            result={currentResult}
            isLoading={isLoading}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
