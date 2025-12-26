import { FileCode } from 'lucide-react';
import { CodeSnippet as CodeSnippetType } from '../types';

interface CodeSnippetProps {
  snippet: CodeSnippetType;
}

export function CodeSnippet({ snippet }: CodeSnippetProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300 font-mono">{snippet.filePath}</span>
        </div>
        <span className="text-xs text-gray-500">
          Lines {snippet.startLine}-{snippet.endLine}
        </span>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm text-gray-300 font-mono leading-relaxed">
          <code>{snippet.content}</code>
        </pre>
      </div>
    </div>
  );
}
