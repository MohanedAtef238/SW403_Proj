import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { ReasoningStep } from '../types';

interface ReasoningTraceProps {
  steps: ReasoningStep[];
}

interface StepItemProps {
  step: ReasoningStep;
}

function StepItem({ step }: StepItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 text-sm font-semibold">
            {step.step}
          </div>
          <span className="text-sm font-medium text-white">{step.description}</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
      </button>
      {isExpanded && (
        <div className="px-4 py-3 border-t border-gray-800 bg-gray-950">
          <p className="text-sm text-gray-400">{step.action}</p>
        </div>
      )}
    </div>
  );
}

export function ReasoningTrace({ steps }: ReasoningTraceProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-4">
        <div className="h-px flex-1 bg-gray-800"></div>
        <span className="text-xs text-gray-500 uppercase tracking-wider">Step-by-step Analysis</span>
        <div className="h-px flex-1 bg-gray-800"></div>
      </div>
      {steps.map((step) => (
        <StepItem key={step.step} step={step} />
      ))}
    </div>
  );
}
