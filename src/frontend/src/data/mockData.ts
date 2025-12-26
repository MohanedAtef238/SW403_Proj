import { QueryResult, RAGStrategy, CodeSnippet, ReasoningStep, GraphNode } from '../types';

export const mockCodeSnippets: CodeSnippet[] = [
  {
    id: '1',
    content: `async function authenticateUser(credentials: Credentials) {
  const { email, password } = credentials;
  const user = await db.users.findByEmail(email);

  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    throw new UnauthorizedError('Invalid credentials');
  }

  return generateToken(user);
}`,
    filePath: 'src/auth/authenticate.ts',
    language: 'typescript',
    startLine: 45,
    endLine: 54
  },
  {
    id: '2',
    content: `export class APIGateway {
  async handleRequest(req: Request) {
    const token = extractBearerToken(req.headers);
    const user = await this.authService.verifyToken(token);

    if (!user) {
      return unauthorized();
    }

    return this.router.dispatch(req, user);
  }
}`,
    filePath: 'src/gateway/APIGateway.ts',
    language: 'typescript',
    startLine: 12,
    endLine: 22
  }
];

export const mockReasoningSteps: ReasoningStep[] = [
  {
    step: 1,
    description: 'Detected authentication flow query',
    action: 'Classified as multi-step complexity, requiring flow tracing'
  },
  {
    step: 2,
    description: 'Retrieved entry point',
    action: 'Found APIGateway.handleRequest as initial handler'
  },
  {
    step: 3,
    description: 'Traced authentication chain',
    action: 'Followed calls to authService.verifyToken → authenticateUser'
  },
  {
    step: 4,
    description: 'Identified database interaction',
    action: 'Located db.users.findByEmail in authentication layer'
  }
];

export const mockGraphNodes: GraphNode[] = [
  {
    id: 'APIGateway',
    label: 'APIGateway',
    type: 'class',
    connections: ['authService', 'router']
  },
  {
    id: 'authService',
    label: 'AuthService',
    type: 'class',
    connections: ['verifyToken', 'authenticateUser']
  },
  {
    id: 'authenticateUser',
    label: 'authenticateUser()',
    type: 'function',
    connections: ['db.users']
  },
  {
    id: 'db.users',
    label: 'Database',
    type: 'module',
    connections: []
  }
];

export function generateMockResult(strategy: RAGStrategy): QueryResult {
  const baseMetrics = {
    retrievalTime: Math.random() * 200 + 50,
    totalTokens: Math.floor(Math.random() * 2000 + 500),
    estimatedCost: Math.random() * 0.05 + 0.01,
    relevanceScore: Math.random() * 0.3 + 0.7,
    detectedComplexity: 'multi-step' as const
  };

  const answers: Record<RAGStrategy, string> = {
    P1: 'The authentication flow begins at the API gateway, which extracts the bearer token from request headers. It verifies the token and dispatches the request if valid.',
    P2: 'Authentication starts at APIGateway.handleRequest, which calls authService.verifyToken. The authenticateUser function queries the database using db.users.findByEmail and validates credentials with bcrypt.',
    P3: 'The authentication flow follows this path:\n1. APIGateway receives request\n2. Extracts bearer token from headers\n3. Calls authService.verifyToken\n4. authenticateUser retrieves user from database\n5. Validates password hash with bcrypt\n6. Returns JWT token on success\n\nThe flow includes proper error handling for invalid credentials and missing tokens.',
    P4: 'The authentication architecture forms a layered structure: API Gateway → Auth Service → Database. The gateway acts as the entry point, delegating authentication to a specialized service that interfaces with the user database. This separation of concerns allows for token verification, credential validation, and secure password hashing (bcrypt) in isolated components.',
    hybrid: 'Based on query complexity analysis, using GraphRAG approach:\n\nAuthentication flows through multiple architectural layers. The APIGateway class serves as the entry point, extracting bearer tokens and delegating to authService. The authenticateUser function implements the core logic: database lookup via db.users.findByEmail, password verification with bcrypt, and JWT generation. The flow maintains security through token validation, password hashing, and error handling for unauthorized access.'
  };

  return {
    strategy,
    answer: answers[strategy],
    context: mockCodeSnippets,
    reasoning: mockReasoningSteps,
    graph: strategy === 'P4' || strategy === 'hybrid' ? mockGraphNodes : undefined,
    metrics: baseMetrics
  };
}
