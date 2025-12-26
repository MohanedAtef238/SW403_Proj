import { useState } from 'react';
import { ArrowLeftRight } from 'lucide-react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { QueryInput } from './components/QueryInput';
import { ResultsPanel } from './components/ResultsPanel';
import { MetricsPanel } from './components/MetricsPanel';
import { ComparisonMode } from './components/ComparisonMode';
import { RAGStrategy, QueryComplexity, QueryResult, RetrievalConfig, CostConfig } from './types';
import { generateMockResult } from './data/mockData';

function App() {
  const [codebase, setCodebase] = useState('ecommerce-platform');
  const [strategy, setStrategy] = useState<RAGStrategy>('hybrid');
  const [complexity, setComplexity] = useState<QueryComplexity>('multi-step');
  const [retrievalConfig, setRetrievalConfig] = useState<RetrievalConfig>({
    topK: 5,
    contextWindow: 8000,
    graphDepth: 3
  });
  const [costConfig, setCostConfig] = useState<CostConfig>({
    tokenBudget: 5000,
    latencyAccuracyTradeoff: false
  });

  const [query, setQuery] = useState('');
  const [currentResult, setCurrentResult] = useState<QueryResult | null>(null);
  const [comparisonResults, setComparisonResults] = useState<QueryResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [comparisonMode, setComparisonMode] = useState(false);

  const handleRunQuery = async () => {
    if (!query.trim()) return;

    setIsLoading(true);

    await new Promise(resolve => setTimeout(resolve, 1500));

    if (comparisonMode) {
      const strategies: RAGStrategy[] = ['P1', 'P2', 'P3', 'P4'];
      const results = strategies.map(s => generateMockResult(s));
      setComparisonResults(results);
      setCurrentResult(null);
    } else {
      const result = generateMockResult(strategy);
      setCurrentResult(result);
      setComparisonResults([]);
    }

    setIsLoading(false);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      <Header
        selectedCodebase={codebase}
        onCodebaseChange={setCodebase}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          strategy={strategy}
          onStrategyChange={setStrategy}
          complexity={complexity}
          onComplexityChange={setComplexity}
          retrievalConfig={retrievalConfig}
          onRetrievalConfigChange={setRetrievalConfig}
          costConfig={costConfig}
          onCostConfigChange={setCostConfig}
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
              {comparisonMode ? 'Comparison Results' : 'Query Results'}
            </h2>
            <button
              onClick={() => setComparisonMode(!comparisonMode)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                comparisonMode
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <ArrowLeftRight className="w-4 h-4" />
              {comparisonMode ? 'Single Mode' : 'Compare All'}
            </button>
          </div>

          {comparisonMode ? (
            <div className="flex-1 overflow-y-auto">
              <ComparisonMode
                results={comparisonResults}
                isLoading={isLoading}
              />
            </div>
          ) : (
            <>
              <ResultsPanel
                result={currentResult}
                isLoading={isLoading}
              />
              {currentResult && <MetricsPanel metrics={currentResult.metrics} />}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
