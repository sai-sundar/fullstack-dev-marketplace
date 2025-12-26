# Quiz Templates

Question templates for assessing developer understanding across various topics.

## Table of Contents
1. Quiz Structure
2. React Questions
3. TypeScript Questions
4. Backend/API Questions
5. Database Questions
6. Architecture Questions
7. Codebase-Specific Questions

---

## 1. Quiz Structure

### Question Difficulty Levels

```
Level 1 (Beginner): Recognition and recall
  "What is X?"
  "Where is Y located?"
  
Level 2 (Basic): Understanding
  "What does this code do?"
  "Why would you use X?"
  
Level 3 (Intermediate): Application
  "Write code to do X"
  "Fix the bug in this code"
  
Level 4 (Advanced): Analysis
  "What are the tradeoffs of X vs Y?"
  "Why might this cause problems?"
  
Level 5 (Expert): Design
  "How would you architect X?"
  "Redesign this for better performance"
```

### Quiz Format

```yaml
question:
  id: unique-id
  topic: category
  level: 1-5
  type: multiple-choice | code-reading | code-writing | explanation | bug-hunt
  question: "The question text"
  code: |
    // Optional code snippet
  options:  # For multiple choice
    - a: "Option A"
    - b: "Option B"
    - c: "Option C"
    - d: "Option D"
  correct: "b"
  explanation: "Why this is correct..."
  follow_up: "Additional question after answering"
  codebase_connection: "Where to see this in the codebase"
```

---

## 2. React Questions

### Level 1: Recognition

```yaml
- id: react-1-1
  topic: React Basics
  level: 1
  type: multiple-choice
  question: "What does JSX stand for?"
  options:
    - a: "JavaScript XML"
    - b: "JavaScript Extension"
    - c: "Java Syntax Extension"
    - d: "JSON XML Syntax"
  correct: "a"
  explanation: "JSX stands for JavaScript XML. It's a syntax extension that lets you write HTML-like code in JavaScript."
```

### Level 2: Understanding

```yaml
- id: react-2-1
  topic: React Hooks
  level: 2
  type: code-reading
  question: "What will be logged when the button is clicked?"
  code: |
    function Counter() {
      const [count, setCount] = useState(0);
      
      function handleClick() {
        setCount(count + 1);
        console.log(count);
      }
      
      return <button onClick={handleClick}>Count: {count}</button>;
    }
  options:
    - a: "1"
    - b: "0"
    - c: "undefined"
    - d: "Error"
  correct: "b"
  explanation: "console.log(count) logs 0 because state updates are asynchronous. The count variable in this closure still holds the old value."
  follow_up: "How would you log the new value?"
  codebase_connection: "See apps/web/src/hooks/ for examples of hooks in our codebase"

- id: react-2-2
  topic: React Hooks
  level: 2
  type: code-reading
  question: "How many times will the effect run?"
  code: |
    function Example() {
      const [count, setCount] = useState(0);
      
      useEffect(() => {
        console.log('Effect ran');
      });
      
      return (
        <button onClick={() => setCount(c => c + 1)}>
          Clicked {count} times
        </button>
      );
    }
  options:
    - a: "Once when component mounts"
    - b: "Every time the component renders"
    - c: "Only when count changes"
    - d: "Never"
  correct: "b"
  explanation: "Without a dependency array, useEffect runs after every render. To run only once, add an empty array []."
```

### Level 3: Application

```yaml
- id: react-3-1
  topic: Custom Hooks
  level: 3
  type: code-writing
  question: "Write a custom hook called useLocalStorage that syncs state with localStorage."
  starter_code: |
    function useLocalStorage(key, initialValue) {
      // Your code here
    }
  expected_solution: |
    function useLocalStorage(key, initialValue) {
      const [value, setValue] = useState(() => {
        const stored = localStorage.getItem(key);
        return stored ? JSON.parse(stored) : initialValue;
      });
      
      useEffect(() => {
        localStorage.setItem(key, JSON.stringify(value));
      }, [key, value]);
      
      return [value, setValue];
    }
  evaluation_criteria:
    - "Uses useState with lazy initialization"
    - "Uses useEffect to sync with localStorage"
    - "Handles JSON serialization"
    - "Returns tuple like useState"
```

### Level 4: Analysis

```yaml
- id: react-4-1
  topic: Performance
  level: 4
  type: explanation
  question: "This component re-renders too often. Identify the problems and explain how to fix them."
  code: |
    function UserList({ users }) {
      const [search, setSearch] = useState('');
      
      const filteredUsers = users.filter(u => 
        u.name.toLowerCase().includes(search.toLowerCase())
      );
      
      const handleSearch = (e) => {
        setSearch(e.target.value);
      };
      
      return (
        <div>
          <input onChange={handleSearch} value={search} />
          {filteredUsers.map(user => (
            <UserCard 
              key={user.id} 
              user={user} 
              onClick={() => console.log(user.id)}
            />
          ))}
        </div>
      );
    }
  expected_points:
    - "filteredUsers recalculates on every render → useMemo"
    - "handleSearch recreates on every render → useCallback"
    - "onClick creates new function per item → useCallback or extract"
    - "UserCard might need React.memo if expensive"
```

---

## 3. TypeScript Questions

### Level 1: Recognition

```yaml
- id: ts-1-1
  topic: TypeScript Basics
  level: 1
  type: multiple-choice
  question: "What TypeScript type represents a value that could be a string or null?"
  options:
    - a: "string?"
    - b: "string | null"
    - c: "Optional<string>"
    - d: "Nullable<string>"
  correct: "b"
  explanation: "The union type 'string | null' means the value can be either a string or null."
```

### Level 2: Understanding

```yaml
- id: ts-2-1
  topic: Type Inference
  level: 2
  type: code-reading
  question: "What is the inferred type of 'result'?"
  code: |
    function getValue(condition: boolean) {
      if (condition) {
        return { status: 'success', data: [1, 2, 3] };
      }
      return { status: 'error', message: 'Failed' };
    }
    
    const result = getValue(true);
  options:
    - a: "{ status: string, data: number[] }"
    - b: "{ status: 'success', data: number[] } | { status: 'error', message: string }"
    - c: "{ status: string, data?: number[], message?: string }"
    - d: "unknown"
  correct: "b"
  explanation: "TypeScript infers a union type from the two possible return values. It also infers literal types for 'status'."
  follow_up: "How would you narrow this type to access 'data' safely?"
```

### Level 3: Application

```yaml
- id: ts-3-1
  topic: Generics
  level: 3
  type: code-writing
  question: "Write a generic function 'firstElement' that returns the first element of an array with proper typing."
  starter_code: |
    function firstElement(/* your params */) {
      // Your code
    }
    
    // Should work like:
    const num = firstElement([1, 2, 3]); // type: number
    const str = firstElement(['a', 'b']); // type: string
  expected_solution: |
    function firstElement<T>(arr: T[]): T | undefined {
      return arr[0];
    }
  evaluation_criteria:
    - "Uses generic type parameter"
    - "Returns T | undefined (array could be empty)"
    - "Array is typed as T[]"
```

### Level 4: Analysis

```yaml
- id: ts-4-1
  topic: Type Design
  level: 4
  type: explanation
  question: "Critique this type design. What could go wrong?"
  code: |
    interface APIResponse {
      success: boolean;
      data: any;
      error: string;
    }
    
    function handleResponse(response: APIResponse) {
      if (response.success) {
        console.log(response.data.name);
      } else {
        console.log(response.error);
      }
    }
  expected_points:
    - "'any' defeats TypeScript - data should be generic"
    - "success true + error present is invalid state"
    - "Use discriminated union instead"
    - |
      Better design:
      type APIResponse<T> = 
        | { success: true; data: T }
        | { success: false; error: string }
```

---

## 4. Backend/API Questions

### Level 2: Understanding

```yaml
- id: api-2-1
  topic: Express Middleware
  level: 2
  type: code-reading
  question: "In what order do these middleware run? What gets logged?"
  code: |
    app.use((req, res, next) => {
      console.log('A');
      next();
    });
    
    app.use((req, res, next) => {
      console.log('B');
      next();
    });
    
    app.get('/test', (req, res) => {
      console.log('C');
      res.send('Done');
    });
  options:
    - a: "C, B, A"
    - b: "A, B, C"
    - c: "B, A, C"
    - d: "C only"
  correct: "b"
  explanation: "Middleware runs in order of declaration. app.use runs for all routes, then the specific route handler."
```

### Level 3: Application

```yaml
- id: api-3-1
  topic: Error Handling
  level: 3
  type: bug-hunt
  question: "This error handler doesn't work properly. Find and fix the issues."
  code: |
    app.get('/user/:id', async (req, res) => {
      const user = await db.users.findById(req.params.id);
      if (!user) {
        throw new Error('User not found');
      }
      res.json(user);
    });
    
    app.use((err, req, res, next) => {
      res.status(500).json({ error: err.message });
    });
  bugs:
    - "Async errors aren't caught - need try/catch or express-async-errors"
    - "All errors return 500 - should check error type"
    - "Error handler signature needs all 4 params to be recognized"
  fixed_code: |
    app.get('/user/:id', async (req, res, next) => {
      try {
        const user = await db.users.findById(req.params.id);
        if (!user) {
          return res.status(404).json({ error: 'User not found' });
        }
        res.json(user);
      } catch (err) {
        next(err);
      }
    });
```

---

## 5. Database Questions

### Level 2: Understanding

```yaml
- id: db-2-1
  topic: SQL Queries
  level: 2
  type: code-reading
  question: "What does this Supabase query return?"
  code: |
    const { data } = await supabase
      .from('cvs')
      .select('id, original_filename, profiles(full_name)')
      .eq('status', 'analyzed')
      .order('created_at', { ascending: false })
      .limit(10);
  answer: |
    Returns the 10 most recently analyzed CVs with:
    - id
    - original_filename  
    - The related profile's full_name (via foreign key join)
  codebase_connection: "See apps/server/src/services/cv.ts for similar queries"

- id: db-2-2
  topic: RLS Policies
  level: 2
  type: explanation
  question: "Explain what this RLS policy does and why it's important."
  code: |
    CREATE POLICY "Users can view own CVs" ON public.cvs
      FOR SELECT USING (auth.uid() = user_id);
  answer: |
    This policy ensures users can only SELECT rows where the user_id 
    column matches their authenticated user ID. Without it, any 
    authenticated user could read anyone's CVs.
```

### Level 3: Application

```yaml
- id: db-3-1
  topic: Schema Design
  level: 3
  type: code-writing
  question: |
    Design a schema for tracking job applications. 
    Each application belongs to a user, may reference a CV, 
    and tracks company, role, status, and dates.
  expected_solution: |
    CREATE TABLE public.applications (
      id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
      user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
      cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
      company_name TEXT NOT NULL,
      job_title TEXT NOT NULL,
      job_url TEXT,
      status TEXT NOT NULL DEFAULT 'applied' 
        CHECK (status IN ('applied', 'interviewing', 'offered', 'rejected', 'withdrawn')),
      applied_at TIMESTAMPTZ DEFAULT now(),
      notes TEXT,
      created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
      updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
    );
    
    CREATE INDEX idx_applications_user_id ON public.applications(user_id);
    CREATE INDEX idx_applications_status ON public.applications(status);
    
    ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "Users can CRUD own applications" ON public.applications
      FOR ALL USING (auth.uid() = user_id);
  evaluation_criteria:
    - "Proper foreign key to users"
    - "Optional foreign key to CVs"
    - "Status enum with CHECK constraint"
    - "Indexes on commonly queried columns"
    - "RLS enabled and policy defined"
```

---

## 6. Architecture Questions

### Level 4: Analysis

```yaml
- id: arch-4-1
  topic: Service Layer
  level: 4
  type: explanation
  question: "Why do we use a service layer instead of putting business logic in route handlers?"
  expected_points:
    - "Separation of concerns - routes handle HTTP, services handle logic"
    - "Testability - services can be unit tested without HTTP"
    - "Reusability - same service can be used by multiple routes"
    - "Dependency injection - easier to mock dependencies"
  codebase_connection: "Compare apps/server/src/routes/cv.ts with apps/server/src/services/cv.ts"

- id: arch-4-2
  topic: Contracts Pattern
  level: 4
  type: explanation
  question: "This codebase uses a contracts/ directory with shared types. What problems does this solve?"
  expected_points:
    - "Prevents frontend-backend type drift"
    - "Single source of truth for data shapes"
    - "Compile-time errors instead of runtime bugs"
    - "API contracts are explicit and documented"
    - "Easier refactoring - change type, see all breakages"
```

### Level 5: Design

```yaml
- id: arch-5-1
  topic: System Design
  level: 5
  type: explanation
  question: |
    The CV analysis feature currently blocks the request while waiting for 
    Claude API response (up to 30 seconds). Design a better approach.
  expected_points:
    - "Use async job queue (e.g., BullMQ, Supabase Edge Functions)"
    - "Return job ID immediately, client polls for status"
    - "Or use WebSockets/Server-Sent Events for real-time updates"
    - "Store intermediate state in database"
    - "Handle failures with retry logic"
  sample_design: |
    1. POST /cv/analyze → Creates job, returns { jobId }
    2. Background worker picks up job
    3. Worker calls Claude API, updates job status
    4. Client polls GET /jobs/:id or subscribes to WebSocket
    5. Job completes → { status: 'done', result: {...} }
```

---

## 7. Codebase-Specific Questions

Generate these dynamically based on actual codebase:

```yaml
- id: codebase-1
  topic: Project Structure
  level: 1
  type: multiple-choice
  question: "Where are shared TypeScript types defined in this project?"
  options:
    - a: "apps/web/src/types/"
    - b: "apps/server/src/types/"
    - c: "contracts/types.ts"
    - d: "packages/shared/types/"
  correct: "c"
  explanation: "This codebase uses a contracts/ directory for shared types to ensure frontend and backend stay in sync."

- id: codebase-2
  topic: Data Flow
  level: 2
  type: explanation
  question: "Trace the code path when a user uploads a CV. List the files involved in order."
  expected_answer:
    - "apps/web/src/components/CVUpload.tsx - UI component"
    - "apps/web/src/api/cv.ts - API client function"
    - "apps/server/src/routes/cv.ts - Route handler"
    - "apps/server/src/services/cv.ts - Business logic"
    - "contracts/database.sql - Database schema"
    
- id: codebase-3
  topic: Custom Patterns
  level: 3
  type: code-writing
  question: "Following the patterns in this codebase, add a new endpoint to delete a CV."
  context: "Look at existing endpoints in apps/server/src/routes/cv.ts"
  expected_solution: |
    // In apps/server/src/routes/cv.ts
    router.delete('/:id', authenticate, async (req, res, next) => {
      try {
        const { id } = req.params;
        await cvService.delete(req.user.id, id);
        res.json({ success: true });
      } catch (error) {
        next(error);
      }
    });
    
    // In apps/server/src/services/cv.ts
    async delete(userId: string, cvId: string): Promise<void> {
      const { error } = await this.db
        .from('cvs')
        .delete()
        .match({ id: cvId, user_id: userId });
        
      if (error) throw new DatabaseError(error.message);
    }
```

---

## Quiz Session Flow

```
1. Start Quiz
   "Ready for a quiz on [topic]? I'll ask 5 questions, increasing in difficulty."

2. Ask Question
   [Show question, code if applicable, options if multiple choice]

3. Wait for Answer
   
4. Provide Feedback
   "Correct! [explanation]"
   OR
   "Not quite. [explanation of correct answer]"

5. Connect to Codebase
   "You can see this pattern in [file path]"

6. Follow-up (if applicable)
   "Can you explain why in your own words?"

7. Adapt Difficulty
   - 2+ wrong: "Let's try an easier one"
   - 2+ right: "Let's increase difficulty"

8. Summary
   "Quiz complete! You scored 4/5.
   Strengths: [topics]
   Review needed: [topics]"
```
