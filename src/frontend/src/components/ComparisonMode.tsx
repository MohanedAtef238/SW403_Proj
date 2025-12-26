import { QueryResult, RAGStrategy } from '../types';
import { Clock, Zap, Coins } from 'lucide-react';

interface ComparisonModeProps {
  results: QueryResult[];
  isLoading: boolean;
}

const strategyNames: Record<RAGStrategy, string> = {
  P1: 'Baseline',
  P2: 'cAST Chunking',
  P3: 'Context-Enriched',
  P4: 'GraphRAG',
  hybrid: 'Hybrid'
};

function ComparisonCard({ result, isLoading }: { result: QueryResult | null; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="flex-1 bg-gray-900 border border-gray-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-800 rounded w-1/2"></div>
          <div className="h-4 bg-gray-800 rounded w-3/4"></div>
          <div className="h-4 bg-gray-800 rounded w-full"></div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex-1 bg-gray-900 border border-gray-800 rounded-lg p-6">
        <div className="text-center text-gray-500">No result</div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <div className="bg-gray-800 px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">{strategyNames[result.strategy]}</h3>
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {result.metrics.retrievalTime.toFixed(0)}ms
          </div>
          <div className="flex items-center gap-1">
            <Zap className="w-3 h-3" />
            {result.metrics.totalTokens}
          </div>
          <div className="flex items-center gap-1">
            <Coins className="w-3 h-3" />
            ${result.metrics.estimatedCost.toFixed(4)}
          </div>
        </div>
      </div>

      <div className="p-4">
        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Answer</div>
          <p className="text-sm text-gray-300 leading-relaxed line-clamp-6">{result.answer}</p>
        </div>

        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Retrieved Context</div>
          <div className="text-sm text-gray-400">
            {result.context.length} snippets
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Reasoning Steps</div>
          <div className="text-sm text-gray-400">
            {result.reasoning.length} steps
          </div>
        </div>
      </div>
    </div>
  );
}

export function ComparisonMode({ results, isLoading }: ComparisonModeProps) {
  const strategies: RAGStrategy[] = ['P1', 'P2', 'P3', 'P4'];

  return (
    <div className="bg-gray-950 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white mb-2">Strategy Comparison</h2>
        <p className="text-sm text-gray-400">Side-by-side analysis of all RAG strategies</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {strategies.map((strategy) => {
          const result = results.find((r) => r.strategy === strategy) || null;
          return (
            <ComparisonCard
              key={strategy}
              result={result}
              isLoading={isLoading}
            />
          );
        })}
      </div>
    </div>
  );
}
