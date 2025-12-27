import { CheckCircle, XCircle, Activity } from 'lucide-react';
import { ReasoningStep } from '../types';

interface ReasoningTraceProps {
  steps: ReasoningStep[];
}

export function ReasoningTrace({ steps }: ReasoningTraceProps) {
  if (steps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <Activity className="w-12 h-12 mb-4 opacity-50" />
        <p className="text-center">
          No self-check results yet.<br />
          Click "Self Check" to verify the response.
        </p>
      </div>
    );
  }

  const result = steps[0];
  const similarityPercent = Math.round(result.similarityScore * 100);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="h-px flex-1 bg-gray-800"></div>
        <span className="text-xs text-gray-500 uppercase tracking-wider">Self-Check Analysis</span>
        <div className="h-px flex-1 bg-gray-800"></div>
      </div>

      {/* Combined Row: Status + Similarity */}
      <div className={`p-5 rounded-lg border ${result.isHallucinating
          ? 'bg-red-500/10 border-red-500/30'
          : 'bg-green-500/10 border-green-500/30'
        }`}>
        <div className="flex items-center gap-6">
          {/* Left 30%: Status Icon & Label */}
          <div className="flex items-center gap-3 w-[30%] shrink-0">
            {result.isHallucinating ? (
              <XCircle className="w-8 h-8 text-red-400" />
            ) : (
              <CheckCircle className="w-8 h-8 text-green-400" />
            )}
            <div>
              <h3 className={`text-sm font-semibold ${result.isHallucinating ? 'text-red-400' : 'text-green-400'
                }`}>
                {result.isHallucinating ? 'Potential Hallucination' : 'Response Verified'}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {result.isHallucinating ? 'Low similarity detected' : 'Consistent response'}
              </p>
            </div>
          </div>

          {/* Right 70%: Similarity Score */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-300">Similarity Score</span>
              <span className={`text-xl font-bold ${similarityPercent > 50 ? 'text-green-400' : 'text-red-400'
                }`}>
                {similarityPercent}%
              </span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${similarityPercent > 50 ? 'bg-green-500' : 'bg-red-500'
                  }`}
                style={{ width: `${similarityPercent}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {result.description}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
