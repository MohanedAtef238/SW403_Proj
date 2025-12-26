import { Settings, Database, X } from 'lucide-react';
import { useState, useEffect } from 'react';

interface HeaderProps {
  isHealthy: boolean | null;
  selectedDatabase: string | null;
  onDatabaseChange: (db: string | null) => void;
}

const API_BASE = 'http://127.0.0.1:8000';

export function Header({ isHealthy, selectedDatabase, onDatabaseChange }: HeaderProps) {
  const [showSettings, setShowSettings] = useState(false);
  const [databases, setDatabases] = useState<string[]>([]);
  const [loadingDbs, setLoadingDbs] = useState(false);

  useEffect(() => {
    if (showSettings) {
      setLoadingDbs(true);
      fetch(`${API_BASE}/databases`)
        .then(res => res.json())
        .then(data => {
          setDatabases(data.databases || []);
          setLoadingDbs(false);
        })
        .catch(() => setLoadingDbs(false));
    }
  }, [showSettings]);

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 relative">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Structure-Aware RAG for Code Intelligence
          </h1>
        </div>

        <div className="flex items-center gap-4">
          {/* Health Indicator */}
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${isHealthy === null
                ? 'bg-gray-500 animate-pulse'
                : isHealthy
                  ? 'bg-green-500'
                  : 'bg-red-500'
                }`}
              title={
                isHealthy === null
                  ? 'Checking API...'
                  : isHealthy
                    ? 'API Connected'
                    : 'API Disconnected'
              }
            />
            <span className="text-sm text-gray-400">
              {isHealthy === null ? 'Checking...' : isHealthy ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Selected Database Badge */}
          {selectedDatabase && (
            <div className="flex items-center gap-1.5 px-2 py-1 bg-blue-600/20 border border-blue-500/30 rounded text-xs text-blue-400">
              <Database className="w-3 h-3" />
              {selectedDatabase}
            </div>
          )}

          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Settings Dropdown */}
      {showSettings && (
        <div className="absolute right-6 top-full mt-2 w-72 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-white">Select Database</h3>
            <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="p-2 max-h-64 overflow-y-auto">
            {loadingDbs ? (
              <p className="text-sm text-gray-500 text-center py-4">Loading...</p>
            ) : databases.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No databases found</p>
            ) : (
              databases.map(db => (
                <button
                  key={db}
                  onClick={() => {
                    onDatabaseChange(selectedDatabase === db ? null : db);
                    setShowSettings(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${selectedDatabase === db
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800'
                    }`}
                >
                  <Database className="w-3.5 h-3.5 inline mr-2" />
                  {db}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </header>
  );
}
