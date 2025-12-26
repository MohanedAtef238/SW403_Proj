import { GraphNode } from '../types';

interface GraphViewProps {
  nodes: GraphNode[];
}

const nodeColors = {
  function: 'bg-blue-500/20 border-blue-500 text-blue-400',
  class: 'bg-purple-500/20 border-purple-500 text-purple-400',
  file: 'bg-green-500/20 border-green-500 text-green-400',
  module: 'bg-yellow-500/20 border-yellow-500 text-yellow-400'
};

export function GraphView({ nodes }: GraphViewProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-8">
      <div className="flex flex-col items-center space-y-8">
        {nodes.map((node, index) => (
          <div key={node.id} className="relative">
            <div
              className={`px-6 py-4 rounded-lg border-2 ${nodeColors[node.type]} font-mono text-sm font-medium backdrop-blur-sm`}
            >
              <div className="text-center">
                <div className="text-xs opacity-60 mb-1">{node.type}</div>
                <div>{node.label}</div>
              </div>
            </div>

            {index < nodes.length - 1 && (
              <div className="absolute left-1/2 -bottom-8 w-0.5 h-8 bg-gray-700 transform -translate-x-1/2">
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2">
                  <div className="w-2 h-2 bg-gray-700 rounded-full"></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-8 pt-6 border-t border-gray-800">
        <div className="flex items-center gap-6 justify-center flex-wrap">
          {Object.entries(nodeColors).map(([type, colors]) => (
            <div key={type} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded ${colors}`}></div>
              <span className="text-xs text-gray-400 capitalize">{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
