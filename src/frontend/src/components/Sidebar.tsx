import { Info, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { RAGStrategy, QueryComplexity, RetrievalConfig, CostConfig } from '../types';

interface SidebarProps {
  strategy: RAGStrategy;
  onStrategyChange: (strategy: RAGStrategy) => void;
  complexity: QueryComplexity;
  onComplexityChange: (complexity: QueryComplexity) => void;
  retrievalConfig: RetrievalConfig;
  onRetrievalConfigChange: (config: RetrievalConfig) => void;
  costConfig: CostConfig;
  onCostConfigChange: (config: CostConfig) => void;
}

const strategies = [
  { value: 'P1' as const, label: 'P1 – Baseline (Function-Level RAG)', description: 'Simple chunking by function boundaries' },
  { value: 'P2' as const, label: 'P2 – cAST-Based Chunking', description: 'Syntax-aware code splitting using AST' },
  { value: 'P3' as const, label: 'P3 – Context-Enriched cAST', description: 'AST chunking with dependency context' },
  { value: 'P4' as const, label: 'P4 – GraphRAG', description: 'Graph-based knowledge retrieval' },
  { value: 'hybrid' as const, label: 'Hybrid – Query-Adaptive', description: 'Automatically selects strategy based on query' }
];

const complexities = [
  { value: 'simple' as const, label: 'Simple', description: 'Single function or concept' },
  { value: 'multi-step' as const, label: 'Multi-step', description: 'Flow tracing across functions' },
  { value: 'global' as const, label: 'Global / Architectural', description: 'System-wide patterns' }
];

function CollapsibleSection({ title, children, defaultOpen = true }: { title: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-gray-800">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-800/50 transition-colors"
      >
        <span className="text-sm font-semibold text-white">{title}</span>
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
      </button>
      {isOpen && <div className="px-4 py-3">{children}</div>}
    </div>
  );
}

function Tooltip({ text }: { text: string }) {
  return (
    <div className="group relative inline-block">
      <Info className="w-3 h-3 text-gray-500 cursor-help" />
      <div className="absolute left-6 top-0 w-64 bg-gray-950 border border-gray-700 rounded-lg p-2 text-xs text-gray-300 invisible group-hover:visible z-10 shadow-xl">
        {text}
      </div>
    </div>
  );
}

export function Sidebar({
  strategy,
  onStrategyChange,
  complexity,
  onComplexityChange,
  retrievalConfig,
  onRetrievalConfigChange,
  costConfig,
  onCostConfigChange
}: SidebarProps) {
  const showGraphDepth = strategy === 'P4' || strategy === 'hybrid';

  return (
    <aside className="w-80 bg-gray-900 border-r border-gray-800 overflow-y-auto">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Configuration</h2>
      </div>

      <CollapsibleSection title="RAG Strategy Selection">
        <div className="space-y-3">
          {strategies.map((s) => (
            <label
              key={s.value}
              className="flex items-start gap-3 cursor-pointer group"
            >
              <input
                type="radio"
                name="strategy"
                value={s.value}
                checked={strategy === s.value}
                onChange={(e) => onStrategyChange(e.target.value as RAGStrategy)}
                className="mt-1 w-4 h-4 text-blue-500 bg-gray-800 border-gray-700 focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-white font-medium">{s.label}</span>
                  <Tooltip text={s.description} />
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{s.description}</p>
              </div>
            </label>
          ))}
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Query Complexity (Manual Override)">
        <div className="space-y-3">
          {complexities.map((c) => (
            <label
              key={c.value}
              className="flex items-start gap-3 cursor-pointer group"
            >
              <input
                type="radio"
                name="complexity"
                value={c.value}
                checked={complexity === c.value}
                onChange={(e) => onComplexityChange(e.target.value as QueryComplexity)}
                className="mt-1 w-4 h-4 text-blue-500 bg-gray-800 border-gray-700 focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-white">{c.label}</span>
                  <Tooltip text={c.description} />
                </div>
              </div>
            </label>
          ))}
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Retrieval Controls">
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-300">Top-k</label>
              <span className="text-sm text-blue-400 font-mono">{retrievalConfig.topK}</span>
            </div>
            <input
              type="range"
              min="1"
              max="20"
              value={retrievalConfig.topK}
              onChange={(e) =>
                onRetrievalConfigChange({
                  ...retrievalConfig,
                  topK: parseInt(e.target.value)
                })
              }
              className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-300">Context Window</label>
              <span className="text-sm text-blue-400 font-mono">{retrievalConfig.contextWindow}</span>
            </div>
            <input
              type="range"
              min="2000"
              max="16000"
              step="1000"
              value={retrievalConfig.contextWindow}
              onChange={(e) =>
                onRetrievalConfigChange({
                  ...retrievalConfig,
                  contextWindow: parseInt(e.target.value)
                })
              }
              className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          {showGraphDepth && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-300">Graph Depth</label>
                <span className="text-sm text-blue-400 font-mono">{retrievalConfig.graphDepth}</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={retrievalConfig.graphDepth}
                onChange={(e) =>
                  onRetrievalConfigChange({
                    ...retrievalConfig,
                    graphDepth: parseInt(e.target.value)
                  })
                }
                className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
          )}
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Cost Controls">
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-300">Token Budget</label>
              <span className="text-sm text-blue-400 font-mono">{costConfig.tokenBudget}</span>
            </div>
            <input
              type="range"
              min="1000"
              max="10000"
              step="500"
              value={costConfig.tokenBudget}
              onChange={(e) =>
                onCostConfigChange({
                  ...costConfig,
                  tokenBudget: parseInt(e.target.value)
                })
              }
              className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-sm text-gray-300">Latency vs Accuracy Tradeoff</span>
            <input
              type="checkbox"
              checked={costConfig.latencyAccuracyTradeoff}
              onChange={(e) =>
                onCostConfigChange({
                  ...costConfig,
                  latencyAccuracyTradeoff: e.target.checked
                })
              }
              className="w-4 h-4 text-blue-500 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
            />
          </label>
        </div>
      </CollapsibleSection>
    </aside>
  );
}
