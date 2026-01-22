# TypeScript Coding Standards

## Core Philosophy
- Types are documentation that the compiler enforces
- Explicit is better than implicit - avoid `any` like the plague
- Use libraries for common patterns - don't reinvent validation or HTTP clients
- Immutability by default - `const` and `readonly` everywhere
- Discriminated unions over inheritance hierarchies

## Essential Libraries

**HTTP clients:** ky (modern fetch wrapper), axios (traditional)

**Validation:** zod (runtime type validation), valibot (lightweight alternative)

**Utilities:** ts-pattern (pattern matching), lodash-es (with proper tree-shaking), date-fns (immutable dates)

**State management:** zustand (simple), jotai (atomic), tanstack-query (server state)

**Testing:** vitest (fast jest alternative), playwright (E2E), msw (API mocking)

**Build/tooling:** vite (fast bundler), typescript-eslint, prettier

**Node.js:** effect (functional error handling), neverthrow (Result types)

## Code Quality Standards

**Always use:**
- Strict mode in tsconfig.json (`strict: true, noUncheckedIndexedAccess: true`)
- Explicit return types on functions
- Discriminated unions over enums
- `const` over `let`, never use `var`
- Type guards (`is` predicates) for narrowing
- `readonly` for arrays and object properties that shouldn't mutate
- Utility types (Pick, Omit, Partial) over manual type construction
- Zod or similar for runtime validation at boundaries (APIs, user input)
- ESLint + Prettier for consistent formatting
- `unknown` over `any` when type is truly unknown

**Never use:**
- `any` type (use `unknown` and narrow)
- Type assertions (`as`) unless absolutely necessary
- `enum` (use const objects or discriminated unions)
- Non-null assertions (`!`) without clear justification
- Optional chaining (`?.`) to mask underlying bugs
- `var` keyword
- Default exports (prefer named exports for better refactoring)

## Pattern Examples

### Bad: Untyped fetch
```ts
async function getUser(id: string) {
  const res = await fetch(`/api/users/${id}`);
  return await res.json();
}
```

### Good: Typed with validation
```ts
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  const data = await res.json();
  return UserSchema.parse(data);
}
```

---

### Bad: Using enums
```ts
enum Status {
  Pending,
  Active,
  Closed,
}
```

### Good: Discriminated union
```ts
type Status = 
  | { kind: 'pending' }
  | { kind: 'active'; startedAt: Date }
  | { kind: 'closed'; reason: string };

function handleStatus(status: Status): string {
  switch (status.kind) {
    case 'pending':
      return 'Waiting to start';
    case 'active':
      return `Started ${status.startedAt.toISOString()}`;
    case 'closed':
      return `Closed: ${status.reason}`;
  }
}
```

---

### Bad: Any type and no error handling
```ts
async function process(data: any) {
  const result = await fetch('/api/process', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return result.json();
}
```

### Good: Typed with proper error handling
```ts
interface ProcessRequest {
  items: readonly string[];
  priority: number;
}

interface ProcessResponse {
  id: string;
  status: 'queued' | 'processing';
}

async function process(data: ProcessRequest): Promise<ProcessResponse> {
  const res = await fetch('/api/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Process failed: ${error}`);
  }
  
  return (await res.json()) as ProcessResponse;
}
```

---

### Bad: Mutable arrays and objects
```ts
function addUser(users: User[], user: User) {
  users.push(user);
  return users;
}
```

### Good: Immutable with readonly
```ts
function addUser(users: readonly User[], user: User): readonly User[] {
  return [...users, user];
}
```

---

### Bad: Type assertion without validation
```ts
const user = data as User;
```

### Good: Type guard with validation
```ts
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    typeof value.id === 'string' &&
    typeof value.name === 'string'
  );
}

if (isUser(data)) {
  // data is now safely typed as User
  console.log(data.name);
}
```

---

### Bad: Optional chaining masking bugs
```ts
function getUserEmail(user: User | undefined) {
  return user?.email?.toLowerCase();
}
```

### Good: Explicit handling
```ts
function getUserEmail(user: User | undefined): string {
  if (!user) {
    throw new Error('User is required');
  }
  if (!user.email) {
    throw new Error('User email is missing');
  }
  return user.email.toLowerCase();
}
```

---

### Bad: Using `any` for unknown types
```ts
function logError(error: any) {
  console.error(error.message);
}
```

### Good: Using `unknown` with narrowing
```ts
function logError(error: unknown): void {
  if (error instanceof Error) {
    console.error(error.message);
  } else if (typeof error === 'string') {
    console.error(error);
  } else {
    console.error('Unknown error', error);
  }
}
```

---

### Bad: Manual type construction
```ts
type UserPreview = {
  id: string;
  name: string;
};
```

### Good: Utility types
```ts
type User = {
  id: string;
  name: string;
  email: string;
  age: number;
};

type UserPreview = Pick<User, 'id' | 'name'>;
type UserUpdate = Partial<Omit<User, 'id'>>;
```

---

### Pattern: Result type for error handling
```ts
type Result<T, E = Error> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

async function safeGetUser(id: string): Promise<Result<User>> {
  try {
    const user = await getUser(id);
    return { ok: true, value: user };
  } catch (error) {
    return { 
      ok: false, 
      error: error instanceof Error ? error : new Error('Unknown error')
    };
  }
}

// Usage
const result = await safeGetUser('123');
if (result.ok) {
  console.log(result.value.name);
} else {
  console.error(result.error.message);
}
```

## TypeScript Config Essentials

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "isolatedModules": true
  }
}
```

## Key Principles

- Types should make illegal states unrepresentable
- Validate at system boundaries (API responses, user input, file reads)
- Prefer type inference where obvious, explicit types at boundaries
- Use narrow types (string literals) over wide types (string)
- Make immutability the default with `readonly` and `const`
- Discriminated unions are your friend for state machines
- The type system should help you refactor fearlessly
