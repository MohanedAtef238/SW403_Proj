import { Settings, Database } from 'lucide-react';

interface HeaderProps {
  selectedCodebase: string;
  onCodebaseChange: (codebase: string) => void;
}

const codebases = [
  'ecommerce-platform',
  'auth-service',
  'data-pipeline',
  'frontend-app'
];

export function Header({ selectedCodebase, onCodebaseChange }: HeaderProps) {
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Structure-Aware RAG for Code Intelligence
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            AST Chunking vs GraphRAG vs Query-Adaptive Retrieval
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-gray-400" />
            <select
              value={selectedCodebase}
              onChange={(e) => onCodebaseChange(e.target.value)}
              className="bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
            >
              {codebases.map((codebase) => (
                <option key={codebase} value={codebase}>
                  {codebase}
                </option>
              ))}
            </select>
          </div>

          <button
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
