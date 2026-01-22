# Go Coding Standards

## Core Philosophy
- Clear is better than clever - Go favors explicitness
- Errors are values, not exceptions - handle them explicitly
- Composition over inheritance - interfaces and embedding
- Concurrency is built-in, use it when it makes sense
- Standard library first - it's exceptionally well-designed
- Simplicity scales - don't reach for complexity prematurely

## Essential Libraries

**CLI tools:** cobra (command structure), viper (configuration), survey (interactive prompts), pterm (beautiful terminal output), urfave/cli (lightweight alternative)

**HTTP/APIs:** net/http (stdlib often enough), chi (lightweight router), fiber (fast framework), gorilla/mux (traditional router)

**Validation:** go-playground/validator (struct validation), ozzo-validation (fluent validation)

**Testing:** testify (assertions and mocks), gomock (mock generation), httptest (stdlib HTTP testing)

**Database:** sqlx (stdlib extensions), pgx (PostgreSQL), ent (ORM), goose/migrate (migrations)

**JSON/serialization:** encoding/json (stdlib), jsoniter (faster), easyjson (code generation)

**Logging:** slog (stdlib since 1.21), zap (structured, fast), zerolog (zero-allocation)

**Utilities:** lo (lodash for Go), samber/do (dependency injection), spf13/cast (type conversion)

**Errors:** pkg/errors (stack traces), cockroachdb/errors (comprehensive), errgroup (concurrent errors)

## Code Quality Standards

**Always use:**
- `gofmt` or `goimports` for formatting (non-negotiable)
- Error handling on every error return - no naked returns ignored
- Context.Context as first parameter for anything that might be cancelled
- Interfaces defined by consumer, not producer
- Struct embedding over inheritance
- Table-driven tests for comprehensive coverage
- golangci-lint for static analysis
- Meaningful variable names - short in small scopes, descriptive in larger ones
- Early returns to reduce nesting
- `defer` for cleanup (files, locks, connections)

**Never do:**
- Ignore errors with `_` without comment explaining why
- Use `panic` for normal error handling (only for programmer errors)
- Export without necessity (start with lowercase, promote when needed)
- Create goroutines without knowing how they'll end
- Use empty interface `interface{}` (use `any` in Go 1.18+)
- Mutate function parameters (Go passes by value, be explicit)
- Use `init()` functions except for package-level registration

## Cobra CLI Specific Guidance

### Project Structure
```
mycli/
├── cmd/
│   ├── root.go       # Root command and global flags
│   ├── serve.go      # Subcommand: serve
│   ├── migrate.go    # Subcommand: migrate
│   └── version.go    # Subcommand: version
├── internal/
│   ├── config/       # Configuration loading (Viper)
│   ├── service/      # Business logic
│   └── database/     # Data access
├── main.go           # Entrypoint
└── go.mod
```

### Root Command Pattern
```go
// cmd/root.go
package cmd

import (
    "fmt"
    "os"
    
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var (
    cfgFile string
    verbose bool
)

var rootCmd = &cobra.Command{
    Use:   "mycli",
    Short: "A brief description of your application",
    Long: `A longer description that spans multiple lines and likely contains
examples and usage of using your application.`,
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func init() {
    cobra.OnInitialize(initConfig)
    
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.mycli.yaml)")
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")
    
    // Bind to viper
    viper.BindPFlag("verbose", rootCmd.PersistentFlags().Lookup("verbose"))
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        home, err := os.UserHomeDir()
        cobra.CheckErr(err)
        
        viper.AddConfigPath(home)
        viper.SetConfigType("yaml")
        viper.SetConfigName(".mycli")
    }
    
    viper.AutomaticEnv()
    
    if err := viper.ReadInConfig(); err == nil && verbose {
        fmt.Fprintln(os.Stderr, "Using config file:", viper.ConfigFileUsed())
    }
}
```

### Subcommand Pattern
```go
// cmd/serve.go
package cmd

import (
    "context"
    "fmt"
    "os"
    "os/signal"
    "syscall"
    
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Start the server",
    Long:  `Start the HTTP server and begin handling requests.`,
    RunE: func(cmd *cobra.Command, args []string) error {
        return runServe(cmd.Context())
    },
}

func init() {
    rootCmd.AddCommand(serveCmd)
    
    serveCmd.Flags().IntP("port", "p", 8080, "Port to listen on")
    serveCmd.Flags().String("host", "0.0.0.0", "Host to bind to")
    
    viper.BindPFlag("server.port", serveCmd.Flags().Lookup("port"))
    viper.BindPFlag("server.host", serveCmd.Flags().Lookup("host"))
}

func runServe(ctx context.Context) error {
    // Setup signal handling for graceful shutdown
    ctx, cancel := signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)
    defer cancel()
    
    port := viper.GetInt("server.port")
    host := viper.GetString("server.host")
    
    fmt.Printf("Starting server on %s:%d\n", host, port)
    
    // Your server logic here
    // Use ctx for graceful shutdown
    
    return nil
}
```

### Interactive Prompts with Survey
```go
package cmd

import (
    "github.com/AlecAivazis/survey/v2"
    "github.com/spf13/cobra"
)

var initCmd = &cobra.Command{
    Use:   "init",
    Short: "Initialize a new project",
    RunE: func(cmd *cobra.Command, args []string) error {
        return runInit()
    },
}

func init() {
    rootCmd.AddCommand(initCmd)
}

type ProjectConfig struct {
    Name     string
    Type     string
    Features []string
}

func runInit() error {
    config := &ProjectConfig{}
    
    questions := []*survey.Question{
        {
            Name: "name",
            Prompt: &survey.Input{
                Message: "Project name:",
                Default: "my-project",
            },
            Validate: survey.Required,
        },
        {
            Name: "type",
            Prompt: &survey.Select{
                Message: "Project type:",
                Options: []string{"api", "cli", "web"},
                Default: "api",
            },
        },
        {
            Name: "features",
            Prompt: &survey.MultiSelect{
                Message: "Select features:",
                Options: []string{"database", "auth", "logging", "metrics"},
            },
        },
    }
    
    if err := survey.Ask(questions, config); err != nil {
        return err
    }
    
    // Create project with config
    return createProject(config)
}

func createProject(config *ProjectConfig) error {
    // Implementation
    return nil
}
```

### Beautiful Output with pterm
```go
package cmd

import (
    "time"
    
    "github.com/pterm/pterm"
    "github.com/spf13/cobra"
)

var deployCmd = &cobra.Command{
    Use:   "deploy",
    Short: "Deploy the application",
    RunE: func(cmd *cobra.Command, args []string) error {
        return runDeploy()
    },
}

func init() {
    rootCmd.AddCommand(deployCmd)
}

func runDeploy() error {
    // Header
    pterm.DefaultHeader.WithFullWidth().Println("Deploying Application")
    
    // Spinner for long-running tasks
    spinner, _ := pterm.DefaultSpinner.Start("Building application...")
    time.Sleep(2 * time.Second)
    spinner.Success("Build complete!")
    
    // Progress bar
    pterm.DefaultSection.Println("Uploading artifacts")
    progressbar, _ := pterm.DefaultProgressbar.WithTotal(100).Start()
    for i := 0; i < 100; i++ {
        progressbar.Increment()
        time.Sleep(10 * time.Millisecond)
    }
    
    // Table for results
    pterm.DefaultTable.WithHasHeader().WithData(pterm.TableData{
        {"Service", "Status", "URL"},
        {"API", "✓ Running", "https://api.example.com"},
        {"Web", "✓ Running", "https://example.com"},
    }).Render()
    
    // Success message
    pterm.Success.Println("Deployment successful!")
    
    return nil
}
```

### Configuration with Viper Best Practices
```go
// internal/config/config.go
package config

import (
    "fmt"
    "strings"
    
    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Log      LogConfig
}

type ServerConfig struct {
    Host string
    Port int
}

type DatabaseConfig struct {
    URL          string
    MaxConns     int
    MaxIdleConns int
}

type LogConfig struct {
    Level  string
    Format string
}

func Load() (*Config, error) {
    // Environment variables
    viper.SetEnvPrefix("MYAPP")
    viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
    viper.AutomaticEnv()
    
    // Defaults
    viper.SetDefault("server.host", "0.0.0.0")
    viper.SetDefault("server.port", 8080)
    viper.SetDefault("database.maxconns", 25)
    viper.SetDefault("database.maxidleconns", 5)
    viper.SetDefault("log.level", "info")
    viper.SetDefault("log.format", "json")
    
    var config Config
    if err := viper.Unmarshal(&config); err != nil {
        return nil, fmt.Errorf("failed to unmarshal config: %w", err)
    }
    
    return &config, nil
}
```

## Pattern Examples

### Bad: Ignoring errors
```go
data, _ := os.ReadFile("config.json")
```

### Good: Explicit error handling
```go
data, err := os.ReadFile("config.json")
if err != nil {
    return fmt.Errorf("failed to read config: %w", err)
}
```

---

### Bad: Naked goroutine
```go
go func() {
    processData()
}()
```

### Good: Managed goroutine with context
```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

errCh := make(chan error, 1)
go func() {
    errCh <- processData(ctx)
}()

select {
case err := <-errCh:
    if err != nil {
        return fmt.Errorf("processing failed: %w", err)
    }
case <-ctx.Done():
    return ctx.Err()
}
```

---

### Bad: Global state
```go
var db *sql.DB

func init() {
    db = connectDB()
}
```

### Good: Dependency injection
```go
type Service struct {
    db *sql.DB
}

func NewService(db *sql.DB) *Service {
    return &Service{db: db}
}

func (s *Service) GetUser(ctx context.Context, id string) (*User, error) {
    // Use s.db
}
```

---

### Bad: Empty interface for everything
```go
func Process(data interface{}) error {
    // Type assertion madness
}
```

### Good: Specific types or generics (Go 1.18+)
```go
func Process[T any](data T) error {
    // Type-safe processing
}

// Or use specific interface
type Processor interface {
    Process() error
}

func ProcessItem(p Processor) error {
    return p.Process()
}
```

---

### Bad: Not using defer for cleanup
```go
f, err := os.Open("file.txt")
if err != nil {
    return err
}
data, err := io.ReadAll(f)
f.Close()
if err != nil {
    return err
}
```

### Good: Defer ensures cleanup
```go
f, err := os.Open("file.txt")
if err != nil {
    return err
}
defer f.Close()

data, err := io.ReadAll(f)
if err != nil {
    return err
}
```

---

### Pattern: Table-driven tests
```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"mixed", -2, 3, 1},
        {"zeros", 0, 0, 0},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

---

### Pattern: Context-aware operations
```go
func FetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }
    
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("do request: %w", err)
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
    }
    
    return io.ReadAll(resp.Body)
}
```

---

### Pattern: Functional options for constructors
```go
type Server struct {
    host    string
    port    int
    timeout time.Duration
}

type Option func(*Server)

func WithHost(host string) Option {
    return func(s *Server) {
        s.host = host
    }
}

func WithPort(port int) Option {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(timeout time.Duration) Option {
    return func(s *Server) {
        s.timeout = timeout
    }
}

func NewServer(opts ...Option) *Server {
    s := &Server{
        host:    "localhost",
        port:    8080,
        timeout: 30 * time.Second,
    }
    
    for _, opt := range opts {
        opt(s)
    }
    
    return s
}

// Usage
server := NewServer(
    WithHost("0.0.0.0"),
    WithPort(9000),
    WithTimeout(60 * time.Second),
)
```

## Cobra CLI Checklist

✅ Use `RunE` instead of `Run` for error handling
✅ Always bind flags to Viper for config file support
✅ Use `PersistentFlags` for flags shared across subcommands
✅ Implement graceful shutdown with signal handling
✅ Use `cobra.CheckErr()` for fatal errors in init functions
✅ Provide both short and long descriptions
✅ Use `PreRunE` for validation that should happen before command execution
✅ Add examples to command documentation
✅ Use survey for interactive prompts, not manual fmt.Scanf
✅ Use pterm or similar for beautiful, structured output
✅ Structure commands in separate files under `cmd/` package
✅ Keep business logic in `internal/` packages, not in cmd files

## Key Principles

- Go is designed for clarity - when in doubt, be more explicit
- Errors are just values - handle them like any other value
- Concurrency is a tool, not a requirement - use when it adds value
- The standard library is your friend - learn it before reaching for dependencies
- Interfaces should be small and focused - often just one or two methods
- For CLIs: configuration hierarchy should be flags > env vars > config file > defaults
- Make zero values useful - design structs that work with zero initialization when possible
