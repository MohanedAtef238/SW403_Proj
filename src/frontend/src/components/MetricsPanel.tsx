import { Clock, Coins, Zap, Target } from 'lucide-react';
import { Metrics } from '../types';

interface MetricsPanelProps {
  metrics: Metrics | null;
}

function MetricCard({ icon: Icon, label, value, suffix = '', color = 'blue' }: {
  icon: typeof Clock;
  label: string;
  value: number | string;
  suffix?: string;
  color?: 'blue' | 'green' | 'yellow' | 'purple';
}) {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    green: 'bg-green-500/10 text-green-400 border-green-500/20',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20'
  };

  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${colorClasses[color]}`}>
      <Icon className="w-5 h-5" />
      <div className="flex-1">
        <div className="text-xs opacity-80">{label}</div>
        <div className="text-lg font-semibold font-mono">
          {value}{suffix}
        </div>
      </div>
    </div>
  );
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  if (!metrics) {
    return null;
  }

  return (
    <div className="bg-gray-900 border-t border-gray-800 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Performance Metrics</h3>
        <span className="text-xs text-gray-500 uppercase tracking-wider">Real-time</span>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={Clock}
          label="Retrieval Time"
          value={metrics.retrievalTime.toFixed(0)}
          suffix="ms"
          color="blue"
        />
        <MetricCard
          icon={Zap}
          label="Total Tokens"
          value={metrics.totalTokens.toLocaleString()}
          color="green"
        />
        <MetricCard
          icon={Coins}
          label="Estimated Cost"
          value={`$${metrics.estimatedCost.toFixed(4)}`}
          color="yellow"
        />
        <MetricCard
          icon={Target}
          label="Relevance Score"
          value={`${(metrics.relevanceScore * 100).toFixed(1)}%`}
          color="purple"
        />
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Query Complexity</span>
          <span className="text-xs text-blue-400 font-semibold uppercase tracking-wider">
            {metrics.detectedComplexity}
          </span>
        </div>
      </div>
    </div>
  );
}
