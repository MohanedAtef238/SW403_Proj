import { FileCode, MessageSquare, GitBranch, Network } from 'lucide-react';
import { ResultTab, QueryResult } from '../types';
import { CodeSnippet } from './CodeSnippet';
import { ReasoningTrace } from './ReasoningTrace';
import { GraphView } from './GraphView';

interface ResultsPanelProps {
  result: QueryResult | null;
  isLoading: boolean;
  activeTab: ResultTab;
  onTabChange: (tab: ResultTab) => void;
}

const tabs = [
  { value: 'answer' as const, label: 'Answer', icon: MessageSquare },
  { value: 'context' as const, label: 'Retrieved Context', icon: FileCode },
  { value: 'reasoning' as const, label: 'Self Check', icon: GitBranch },
  { value: 'graph' as const, label: 'Graph View', icon: Network }
];

export function ResultsPanel({ result, isLoading, activeTab, onTabChange }: ResultsPanelProps) {

  if (isLoading) {
    return (
      <div className="flex-1 bg-gray-950 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-800 rounded w-3/4"></div>
          <div className="h-4 bg-gray-800 rounded w-1/2"></div>
          <div className="h-4 bg-gray-800 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex-1 bg-gray-950 flex items-center justify-center">
        <p className="text-gray-500 text-center">
          Run a query to see results
        </p>
      </div>
    );
  }

  const showGraphTab = result.graph && result.graph.length > 0;

  return (
    <div className="flex-1 bg-gray-950 flex flex-col">
      <div className="flex border-b border-gray-800 bg-gray-900">
        {tabs.map((tab) => {
          if (tab.value === 'graph' && !showGraphTab) return null;

          const Icon = tab.icon;
          return (
            <button
              key={tab.value}
              onClick={() => onTabChange(tab.value)}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.value
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-white'
                }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'answer' && (
          <div className="prose prose-invert max-w-none">
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{result.answer}</p>
          </div>
        )}

        {activeTab === 'context' && (
          <div className="space-y-4">
            {result.context.map((snippet) => (
              <CodeSnippet key={snippet.id} snippet={snippet} />
            ))}
          </div>
        )}

        {activeTab === 'reasoning' && (
          <ReasoningTrace steps={result.reasoning} />
        )}

        {activeTab === 'graph' && result.graph && (
          <GraphView nodes={result.graph} />
        )}
      </div>
    </div>
  );
}
