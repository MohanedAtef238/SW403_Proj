export type RAGStrategy = 'P1' | 'P2' | 'P3' | 'P4' | 'hybrid';

export type QueryComplexity = 'simple' | 'multi-step' | 'global';

export type ResultTab = 'answer' | 'context' | 'reasoning' | 'graph';

export interface RetrievalConfig {
  topK: number;
  contextWindow: number;
  graphDepth: number;
}

export interface CostConfig {
  tokenBudget: number;
  latencyAccuracyTradeoff: boolean;
}

export interface QueryResult {
  strategy: RAGStrategy;
  answer: string;
  context: CodeSnippet[];
  reasoning: ReasoningStep[];
  graph?: GraphNode[];
  metrics: Metrics;
}

export interface CodeSnippet {
  id: string;
  content: string;
  filePath: string;
  language: string;
  startLine: number;
  endLine: number;
}

export interface ReasoningStep {
  similarityScore: number;
  description: string;
  isHallucinating: boolean;
}

export interface Metrics {
  retrievalTime: number;
  totalTokens: number;
  estimatedCost: number;
  relevanceScore: number;
  detectedComplexity: QueryComplexity;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'function' | 'class' | 'file' | 'module';
  connections: string[];
}
