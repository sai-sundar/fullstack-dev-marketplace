# Teaching Patterns

Effective pedagogical approaches for teaching software development concepts.

## Table of Contents
1. The Socratic Method
2. Scaffolding Techniques
3. Active Learning Strategies
4. Feedback and Assessment
5. Adapting to Learning Styles
6. Common Misconceptions by Topic

---

## 1. The Socratic Method

### Principle
Guide learners to discover answers through carefully crafted questions rather than direct instruction.

### Why It Works
- Engages active thinking (not passive listening)
- Builds problem-solving skills
- Creates deeper understanding
- Learner remembers self-discovered knowledge better

### Question Progression

```
Level 1: Observation
"What do you see in this code?"
"What files are in this directory?"

Level 2: Pattern Recognition  
"What do these three files have in common?"
"Where else have you seen this pattern?"

Level 3: Inference
"Why do you think it's structured this way?"
"What problem might this solve?"

Level 4: Application
"How would you add a similar feature?"
"What would break if we removed this?"

Level 5: Evaluation
"Is this the best approach? What alternatives exist?"
"What are the tradeoffs?"
```

### Example Dialogue

**Teaching: Why we use TypeScript**

```
Teacher: "Look at this JavaScript function. What could go wrong?"

function processUser(user) {
  return user.name.toUpperCase();
}

Learner: "If user is null, it would crash?"

Teacher: "Good! What else?"

Learner: "If user doesn't have a name property?"

Teacher: "Exactly. Now look at this TypeScript version:"

function processUser(user: User): string {
  return user.name.toUpperCase();
}

Teacher: "How does this help with the problems you identified?"

Learner: "The type tells us user must have a name..."

Teacher: "And when would we find out if someone passed wrong data?"

Learner: "At compile time, not runtime!"

Teacher: "That's the key insight. Why is that valuable?"
```

---

## 2. Scaffolding Techniques

### Principle
Provide temporary support that's gradually removed as competence increases.

### Techniques

**1. Worked Examples → Faded Examples → Independent Practice**

```
Stage 1: Worked Example (Full solution shown)
"Here's how to create an API endpoint:

router.post('/cv/upload', authenticate, async (req, res) => {
  const { file } = req.body;
  const cv = await cvService.upload(req.user.id, file);
  res.json({ success: true, data: cv });
});

Notice:
- authenticate middleware checks auth
- We use the service layer, not direct DB access
- Response follows our standard format"

Stage 2: Faded Example (Partial solution)
"Now create the delete endpoint. I'll start:

router.delete('/cv/:id', authenticate, async (req, res) => {
  // Your turn: 
  // 1. Get the ID from params
  // 2. Call the service to delete
  // 3. Return success response
});

Stage 3: Independent Practice
"Create the update endpoint on your own. 
What will you need to handle?"
```

**2. Concept Mapping**

Build visual connections:

```
                    ┌─────────────┐
                    │   Request   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Router    │  ← "What happens here?"
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼─────┐    ┌──────▼──────┐   ┌──────▼──────┐
   │ Middleware│    │  Controller │   │  Validator  │
   └───────────┘    └──────┬──────┘   └─────────────┘
                           │
                    ┌──────▼──────┐
                    │   Service   │  ← "Why this layer?"
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Database   │
                    └─────────────┘
```

**3. Chunking Complex Topics**

Break down overwhelming concepts:

```
Learning React (wrong approach):
"React is a JavaScript library for building UIs using components, 
which are functions that return JSX, and you manage state with hooks..."

Learning React (chunked approach):
Session 1: "What is a component? Just a function that returns HTML-like code."
Session 2: "Components can receive data. We call these 'props'."
Session 3: "Components can remember things. We call this 'state'."
Session 4: "Let's combine what we know to build something."
```

---

## 3. Active Learning Strategies

### 1. Predict-Observe-Explain

```
Teacher: "Before I run this code, predict what will happen:"

const [count, setCount] = useState(0);

function handleClick() {
  setCount(count + 1);
  setCount(count + 1);
  console.log(count);
}

Learner: "count will be 2, and log 2?"

Teacher: [runs code] "Observe: count is 1, log shows 0. Why?"

Learner: "Oh... the state updates are batched?"

Teacher: "Close! Explain more - what is `count` inside handleClick?"
```

### 2. Rubber Duck Teaching

Have learner explain concepts as if teaching someone else:

```
Teacher: "Pretend I'm a new developer who's never seen React. 
         Explain useState to me."

Learner: "So useState is like... a way to remember things..."

Teacher: "Remember things? Can't I just use a variable?"

Learner: "No because... when the component re-renders..."

[Learner discovers gaps in their own understanding]
```

### 3. Code Tracing

Manually trace execution:

```
Teacher: "Let's trace this code step by step. What's the value of each variable?"

async function example() {
  console.log('A');           // Step 1: prints ___
  
  await delay(100);           // Step 2: what happens?
  
  console.log('B');           // Step 3: prints ___
}

example();
console.log('C');             // Step 4: prints ___

// Final output order: ___
```

### 4. Deliberate Errors

Introduce bugs for learners to find:

```
Teacher: "This code has 3 bugs. Find them:"

async function saveCV(cv: CV) {
  const { data, error } = await supabase
    .from('cv')                    // Bug 1: table name
    .insert({
      id: cv.id,                   // Bug 2: shouldn't set id
      userId: cv.user_id,          // Bug 3: case mismatch
    });
    
  return data;                     // Bug 4: not handling error
}
```

---

## 4. Feedback and Assessment

### Immediate Feedback

Don't wait - correct misunderstandings immediately:

```
Learner: "So useEffect runs before the component renders?"

Teacher: "Almost! Let's check. Add console.logs:"

function Component() {
  console.log('render');
  
  useEffect(() => {
    console.log('effect');
  });
  
  return <div>Test</div>;
}

// Output shows: render, then effect
// Effect runs AFTER render
```

### Growth-Oriented Feedback

Focus on progress, not just correctness:

```
Instead of: "Wrong. The answer is X."

Say: "You're on the right track thinking about [their approach].
     The piece you're missing is [specific gap].
     What if you consider [hint]?"
```

### Mastery Checks

Before moving on, verify understanding:

```
"Before we continue, let me check your understanding:

1. In your own words, why do we use the contracts/ directory?
2. If I change a column name in database.sql, what else must I update?
3. Show me where you'd add a new API endpoint.

[All correct] Great! Let's move to the next topic.
[Gaps found] Let's revisit [specific area] first."
```

---

## 5. Adapting to Learning Styles

### Visual Learners

Use diagrams, flowcharts, code highlighting:

```
                    Request Flow
                    
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Frontend │───▶│ Backend  │───▶│ Database │
    └──────────┘    └──────────┘    └──────────┘
         │               │               │
    React + Fetch   Express +        Supabase +
    Components      Services         PostgreSQL
```

### Reading/Writing Learners

Provide written explanations, encourage note-taking:

```
"Here's a summary to save:

## API Request Lifecycle

1. **Client sends request** - fetch() or axios call
2. **Router matches path** - Express matches URL to handler
3. **Middleware runs** - Authentication, validation
4. **Controller processes** - Extracts data, calls service
5. **Service executes logic** - Business rules, DB operations
6. **Response sent** - JSON with standard format
"
```

### Kinesthetic Learners

Hands-on exercises, immediate coding:

```
"Let's learn by doing. Open apps/server/src/routes/cv.ts

Task 1: Find the upload handler (2 min)
Task 2: Trace what service it calls (2 min)  
Task 3: Add a console.log and see it trigger (3 min)
Task 4: Add a new endpoint skeleton (5 min)
"
```

### Auditory Learners

Verbal explanations, discussions:

```
"Let me walk you through this verbally:

Think of the service layer as a translator. The router speaks HTTP - 
it knows about requests and responses. The database speaks SQL - 
it knows about tables and rows. The service speaks business logic - 
it knows about 'uploading a CV' or 'analyzing a resume'.

When a request comes in, the router says 'someone wants to upload a CV'.
It asks the service, 'hey, can you handle this?' The service knows what 
uploading means - validate the file, store it, create a record. It talks 
to the database in database terms, then tells the router 'done, here's the result.'

Make sense? What questions do you have?"
```

---

## 6. Common Misconceptions by Topic

### React

| Misconception | Reality | Teaching Approach |
|--------------|---------|-------------------|
| "setState is instant" | State updates are batched and async | Show console.log immediately after setState |
| "useEffect is like componentDidMount" | Effects run after every render by default | Show effect running multiple times |
| "Props can be modified" | Props are read-only | Show error when trying to modify |

### TypeScript

| Misconception | Reality | Teaching Approach |
|--------------|---------|-------------------|
| "Types exist at runtime" | Types are erased after compilation | Show compiled JavaScript |
| "any is fine to use" | any defeats TypeScript's purpose | Show bugs that any allows |
| "Interfaces and types are the same" | Subtle differences exist | Show cases where they differ |

### Async/Await

| Misconception | Reality | Teaching Approach |
|--------------|---------|-------------------|
| "await pauses everything" | Only pauses current function | Show other code running during await |
| "async makes things faster" | async is about ordering, not speed | Benchmark to show same speed |
| "Promise.all is always better" | Can fail fast, memory issues | Show failure scenarios |

### Databases

| Misconception | Reality | Teaching Approach |
|--------------|---------|-------------------|
| "SELECT * is fine" | Performance and security issues | Show execution plans, data exposure |
| "Indexes always help" | Write overhead, space cost | Show insert slowdown with many indexes |
| "NULL means empty string" | NULL is absence of value | Show NULL != '' comparisons |

---

## Teaching Session Templates

### 15-Minute Concept Introduction

```
0:00 - Hook: "Have you ever wondered why...?" 
2:00 - Assess: "What do you already know about X?"
4:00 - Explain: Show concrete example from codebase
8:00 - Practice: Guided exercise
12:00 - Check: "Explain back to me..."
14:00 - Connect: "Next time, we'll see how this relates to..."
```

### 30-Minute Deep Dive

```
0:00 - Review: "Last time we covered..."
3:00 - Today's Goal: "By the end, you'll be able to..."
5:00 - Concept 1: Example + Questions
12:00 - Concept 2: Example + Questions  
20:00 - Hands-On: Combine concepts in exercise
27:00 - Recap: Learner summarizes
30:00 - Preview: What's next
```

### 60-Minute Workshop

```
0:00 - Icebreaker: Relevant question or puzzle
5:00 - Overview: Map of what we'll cover
10:00 - Section 1: Teach + Practice
25:00 - Section 2: Teach + Practice
40:00 - Integration: Combine sections
50:00 - Q&A: Address confusions
55:00 - Takeaways: Key points to remember
60:00 - Resources: Where to learn more
```
