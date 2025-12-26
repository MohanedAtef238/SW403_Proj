import { Play, Loader2 } from 'lucide-react';

interface QueryInputProps {
  query: string;
  onQueryChange: (query: string) => void;
  onRunQuery: () => void;
  isLoading: boolean;
}

export function QueryInput({ query, onQueryChange, onRunQuery, isLoading }: QueryInputProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onRunQuery();
    }
  };

  return (
    <div className="bg-gray-900 border-b border-gray-800 p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Ask a question about the codebase
          </label>
          <textarea
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="How does authentication flow from the API gateway to the database?"
            className="w-full h-24 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Running Query...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Run Query
            </>
          )}
        </button>
      </form>
    </div>
  );
}
