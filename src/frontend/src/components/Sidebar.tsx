import { Info, ChevronDown, ChevronRight, Upload } from 'lucide-react';
import { useState } from 'react';

// Simplified types for the API-supported options
export type ChunkingStrategy = 'recursive' | 'code' | 'ast' | 'graphrag';

interface SidebarProps {
  strategy: ChunkingStrategy;
  onStrategyChange: (strategy: ChunkingStrategy) => void;
  topK: number;
  onTopKChange: (k: number) => void;
  onSave: () => void;
  onUpload: (file: File) => void;
  isUploading: boolean;
}

const strategies = [
  { value: 'recursive' as const, label: 'Recursive', description: 'Simple text chunking with overlap', disabled: false },
  { value: 'code' as const, label: 'Code', description: 'Language-aware code splitting', disabled: false },
  { value: 'ast' as const, label: 'AST', description: 'Syntax-aware code splitting using AST', disabled: false },
  { value: 'graphrag' as const, label: 'GraphRAG', description: 'Graph-based knowledge retrieval', disabled: false },
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
  topK,
  onTopKChange,
  onSave,
  onUpload,
  isUploading,
}: SidebarProps) {
  return (
    <aside className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col overflow-hidden">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Configuration</h2>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        <CollapsibleSection title="Chunking Strategy">
          <div className="space-y-3">
            {strategies.map((s) => (
              <label
                key={s.value}
                className={`flex items-start gap-3 group ${s.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <input
                  type="radio"
                  name="strategy"
                  value={s.value}
                  checked={strategy === s.value}
                  disabled={s.disabled}
                  onChange={(e) => onStrategyChange(e.target.value as ChunkingStrategy)}
                  className="mt-1 w-4 h-4 text-blue-500 bg-gray-800 border-gray-700 focus:ring-blue-500 disabled:opacity-50"
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

        <CollapsibleSection title="Retrieval Settings">
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-300">Top-K Results</label>
                <span className="text-sm text-blue-400 font-mono">{topK}</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => onTopKChange(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
          </div>
        </CollapsibleSection>

        <CollapsibleSection title="Upload Codebase" defaultOpen={false}>
          <div className="space-y-3">
            <p className="text-xs text-gray-400">
              Upload a .zip file containing Python source code to index.
            </p>
            <label className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
              <Upload className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-300">
                {isUploading ? 'Indexing...' : 'Choose .zip file'}
              </span>
              <input
                type="file"
                accept=".zip"
                disabled={isUploading}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    onUpload(file);
                    e.target.value = '';
                  }
                }}
                className="hidden"
              />
            </label>
            {isUploading && (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm text-blue-400">Processing...</span>
              </div>
            )}
          </div>
        </CollapsibleSection>
      </div>

      <div className="p-4 border-t border-gray-800 bg-gray-900/50">
        <button
          onClick={onSave}
          className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-lg transition-colors shadow-lg shadow-blue-900/20 active:scale-[0.98]"
        >
          Update Settings
        </button>
      </div>
    </aside>
  );
}
