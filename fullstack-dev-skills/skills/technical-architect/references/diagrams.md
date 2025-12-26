# Architecture Diagrams

Mermaid diagram patterns for system design documentation.

## Table of Contents
1. System Context Diagram
2. Component Diagram
3. Sequence Diagrams
4. Entity Relationship Diagram
5. Data Flow Diagram
6. Deployment Diagram

---

## 1. System Context Diagram

Shows the system and its external actors/systems.

```mermaid
graph TB
    subgraph External
        User[👤 User]
        Admin[👤 Admin]
        OAuth[OAuth Providers<br/>Google, GitHub]
        Email[Email Service<br/>SendGrid]
    end

    subgraph "MyApp System"
        App[MyApp]
    end

    User -->|Uses| App
    Admin -->|Manages| App
    App -->|Authenticates via| OAuth
    App -->|Sends emails via| Email
```

---

## 2. Component Diagram

Shows internal components and their relationships.

```mermaid
graph TB
    subgraph "Frontend (React)"
        UI[UI Components]
        Hooks[React Hooks]
        Store[State Management]
        APIClient[API Client]
    end

    subgraph "Backend (Node.js)"
        Routes[API Routes]
        Controllers[Controllers]
        Services[Services]
        Middleware[Middleware<br/>Auth, Validation]
    end

    subgraph "Data Layer"
        Supabase[(Supabase<br/>PostgreSQL)]
        Storage[Supabase Storage]
    end

    UI --> Hooks
    Hooks --> Store
    Hooks --> APIClient
    APIClient -->|HTTP| Routes
    Routes --> Middleware
    Middleware --> Controllers
    Controllers --> Services
    Services --> Supabase
    Services --> Storage
```

### Detailed Frontend Components

```mermaid
graph LR
    subgraph Pages
        Home[Home Page]
        Dashboard[Dashboard]
        Profile[Profile]
    end

    subgraph Features
        Auth[Auth Module]
        Posts[Posts Module]
        Comments[Comments Module]
    end

    subgraph Shared
        UI[UI Components]
        Hooks[Custom Hooks]
        Utils[Utilities]
    end

    Pages --> Features
    Features --> Shared
```

### Detailed Backend Components

```mermaid
graph LR
    subgraph Routes
        AuthRoutes[/auth/*]
        PostRoutes[/posts/*]
        UserRoutes[/users/*]
    end

    subgraph Middleware
        AuthMW[Auth Middleware]
        ValidateMW[Validation]
        RateLimitMW[Rate Limiting]
    end

    subgraph Services
        AuthService[AuthService]
        PostService[PostService]
        UserService[UserService]
    end

    AuthRoutes --> AuthMW
    PostRoutes --> AuthMW
    PostRoutes --> ValidateMW
    AuthMW --> AuthService
    ValidateMW --> PostService
    UserRoutes --> UserService
```

---

## 3. Sequence Diagrams

### User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant S as Supabase Auth

    U->>F: Enter credentials
    F->>S: signInWithPassword()
    S-->>F: JWT + Refresh Token
    F->>F: Store tokens in memory
    F->>B: API request + Bearer token
    B->>S: Verify JWT
    S-->>B: User data
    B-->>F: Protected resource
    F-->>U: Display data
```

### Create Post Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database

    U->>F: Submit post form
    F->>F: Validate with Zod
    F->>B: POST /api/posts
    B->>B: Validate request
    B->>B: Check auth token
    B->>DB: INSERT post
    DB-->>B: New post record
    B-->>F: 201 Created + post
    F->>F: Update cache
    F-->>U: Show success
```

### Error Handling Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend

    U->>F: Invalid action
    F->>B: API request
    B->>B: Validation fails
    B-->>F: 400 + error details
    F->>F: Parse error response
    F-->>U: Show field errors
```

---

## 4. Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ POSTS : writes
    USERS ||--o{ COMMENTS : writes
    USERS ||--o{ LIKES : gives
    USERS ||--o{ FOLLOWS : follows
    USERS ||--o{ FOLLOWS : followed_by
    POSTS ||--o{ COMMENTS : has
    POSTS ||--o{ LIKES : receives
    POSTS }o--o{ TAGS : tagged_with

    USERS {
        uuid id PK
        string email UK
        string username UK
        string display_name
        string avatar_url
        timestamp created_at
    }

    POSTS {
        uuid id PK
        string title
        string slug UK
        text content
        boolean published
        uuid author_id FK
        timestamp created_at
        timestamp updated_at
    }

    COMMENTS {
        uuid id PK
        text content
        uuid post_id FK
        uuid author_id FK
        uuid parent_id FK
        timestamp created_at
    }

    TAGS {
        uuid id PK
        string name UK
        string slug UK
    }

    LIKES {
        uuid user_id PK,FK
        uuid post_id PK,FK
        timestamp created_at
    }

    FOLLOWS {
        uuid follower_id PK,FK
        uuid following_id PK,FK
        timestamp created_at
    }
```

---

## 5. Data Flow Diagram

### Read Flow (List Posts)

```mermaid
flowchart LR
    subgraph Frontend
        A[User visits /posts] --> B[usePosts hook]
        B --> C[React Query]
        C --> D[API Client]
    end

    subgraph Backend
        E[GET /api/posts] --> F[Auth Middleware]
        F --> G[PostController]
        G --> H[PostService]
    end

    subgraph Database
        I[(Supabase)] --> J[RLS Check]
        J --> K[Return rows]
    end

    D -->|HTTP GET| E
    H -->|Query| I
    K -->|JSON| G
    G -->|Response| D
    D -->|Cache| C
    C -->|Render| B
```

### Write Flow (Create Post)

```mermaid
flowchart LR
    subgraph Frontend
        A[User submits form] --> B[Zod validation]
        B --> C[useMutation]
        C --> D[API Client]
    end

    subgraph Backend
        E[POST /api/posts] --> F[Validate body]
        F --> G[Auth check]
        G --> H[PostService.create]
    end

    subgraph Database
        I[(Supabase)] --> J[RLS Check]
        J --> K[INSERT row]
        K --> L[Return new row]
    end

    D -->|HTTP POST| E
    H -->|Insert| I
    L -->|JSON| H
    H -->|201 Created| D
    D -->|Invalidate cache| C
```

---

## 6. Deployment Diagram

### Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        Dev[Developer]
        IDE[VS Code]
        Terminal[Terminal]
    end

    subgraph "Local Services"
        FrontendDev[Vite Dev Server<br/>:5173]
        BackendDev[Node.js<br/>:3001]
    end

    subgraph "Cloud Services"
        SupabaseDev[Supabase<br/>Development Project]
    end

    Dev --> IDE
    IDE --> Terminal
    Terminal --> FrontendDev
    Terminal --> BackendDev
    FrontendDev --> BackendDev
    BackendDev --> SupabaseDev
```

### Production Environment

```mermaid
graph TB
    subgraph "Users"
        Browser[Browser]
    end

    subgraph "CDN / Edge"
        CDN[Vercel Edge<br/>or Cloudflare]
    end

    subgraph "Frontend Hosting"
        Vercel[Vercel<br/>Static + SSR]
    end

    subgraph "Backend Hosting"
        Railway[Railway<br/>or Render]
        Container[Docker Container]
    end

    subgraph "Database"
        SupabaseProd[Supabase<br/>Production Project]
        Storage[Supabase Storage]
    end

    Browser --> CDN
    CDN --> Vercel
    Vercel --> Railway
    Railway --> Container
    Container --> SupabaseProd
    Container --> Storage
```

### CI/CD Pipeline

```mermaid
flowchart LR
    subgraph "Source"
        GH[GitHub Repository]
    end

    subgraph "CI"
        Actions[GitHub Actions]
        Lint[Lint]
        Test[Test]
        Build[Build]
    end

    subgraph "CD"
        DeployFE[Deploy Frontend<br/>Vercel]
        DeployBE[Deploy Backend<br/>Railway]
        Migrate[Run Migrations<br/>Supabase]
    end

    GH -->|Push| Actions
    Actions --> Lint
    Lint --> Test
    Test --> Build
    Build --> DeployFE
    Build --> DeployBE
    DeployBE --> Migrate
```

---

## Diagram Guidelines

### When to Use Each Type

| Diagram Type | Use When |
|-------------|----------|
| System Context | Starting architecture discussion |
| Component | Explaining internal structure |
| Sequence | Documenting API flows |
| ERD | Designing database schema |
| Data Flow | Explaining request lifecycle |
| Deployment | Planning infrastructure |

### Best Practices

1. **Keep diagrams focused** - One concept per diagram
2. **Use consistent naming** - Same names across diagrams
3. **Add labels** - Explain connections with verb labels
4. **Update with code** - Diagrams should reflect reality
5. **Store in repo** - `docs/diagrams/` directory

### Mermaid in Markdown

````markdown
```mermaid
graph TD
    A[Start] --> B[End]
```
````

Renders in GitHub, GitLab, Notion, and most documentation tools.
