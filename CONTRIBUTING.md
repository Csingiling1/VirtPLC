# Contributing to VirtPLC

Thank you for your interest in contributing to VirtPLC! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what's best for the project and community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (for local development)
- **Git** for version control
- Language-specific tools:
  - **Java 17+** and **Maven** (for backend)
  - **Node.js 18+** and **npm/bun** (for frontend)
  - **Python 3.11+** (for AI service)
  - **Go 1.21+** (for collector)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/VirtPLC.git
   cd VirtPLC
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Csingiling1/VirtPLC.git
   ```

3. **Start development environment**
   ```bash
   # Copy environment configuration
   cp .env.example .env
   
   # Start all services
   ./deploy.sh dev
   ```

4. **Verify setup**
   ```bash
   # Check all services are running
   docker-compose ps
   
   # Access services:
   # Frontend: http://localhost:3000
   # Backend API: http://localhost:8080
   # Node-RED: http://localhost:1880
   ```

## Development Workflow

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent production fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

### Workflow Steps

1. **Create a feature branch**
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, maintainable code
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Keep your branch updated**
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Go to GitHub and create a PR from your fork
   - Fill out the PR template completely
   - Link related issues

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(backend): add device management API endpoint

Implements CRUD operations for device management including
validation and error handling.

Closes #123
```

```
fix(collector): handle MQTT reconnection properly

Previously, the collector would crash on MQTT disconnect.
Now it implements exponential backoff retry logic.

Fixes #456
```

## Coding Standards

### General Principles

1. **Write Clean Code**
   - Keep functions small and focused
   - Use meaningful variable and function names
   - Avoid deep nesting (max 3 levels)
   - Follow SOLID principles

2. **Documentation**
   - Add comments for complex logic
   - Document public APIs and interfaces
   - Update README files when adding features

3. **Error Handling**
   - Always handle errors explicitly
   - Provide meaningful error messages
   - Log errors with appropriate context

### Language-Specific Standards

#### Java (Backend)

```java
/**
 * Retrieves device data within the specified time range.
 *
 * @param deviceId the unique device identifier
 * @param startTime the start of the time range
 * @param endTime the end of the time range
 * @return list of device data points
 * @throws DeviceNotFoundException if device doesn't exist
 */
public List<DeviceData> getDeviceData(
    String deviceId, 
    Instant startTime, 
    Instant endTime
) {
    // Implementation
}
```

**Standards:**
- Follow [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- Use Spring Boot best practices
- Maximum line length: 120 characters
- Use Lombok to reduce boilerplate
- Prefer constructor injection over field injection

#### Python (AI Service)

```python
def analyze_device_performance(
    device_id: str,
    metric: str,
    time_range: TimeRange
) -> PerformanceAnalysis:
    """
    Analyze device performance for a specific metric.

    Args:
        device_id: Unique identifier for the device
        metric: Performance metric to analyze
        time_range: Time range for analysis

    Returns:
        PerformanceAnalysis object containing results

    Raises:
        DeviceNotFoundError: If device doesn't exist
        InvalidMetricError: If metric is not supported
    """
    # Implementation
```

**Standards:**
- Follow [PEP 8](https://pep8.org/)
- Use type hints for all functions
- Maximum line length: 100 characters
- Use `black` for code formatting
- Use `pylint` for linting

#### TypeScript (Frontend)

```typescript
/**
 * Fetches device data from the API.
 *
 * @param deviceId - The device identifier
 * @param options - Query options for filtering and pagination
 * @returns Promise resolving to device data
 */
export async function fetchDeviceData(
  deviceId: string,
  options?: QueryOptions
): Promise<DeviceData[]> {
  // Implementation
}
```

**Standards:**
- Follow [Airbnb TypeScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Prefer `const` over `let`
- Use TypeScript strict mode
- Maximum line length: 100 characters

#### Go (Collector)

```go
// ProcessMessage validates and processes incoming MQTT messages.
//
// Parameters:
//   - msg: The MQTT message to process
//
// Returns:
//   - error: An error if processing fails, nil otherwise
func ProcessMessage(msg *MQTTMessage) error {
    // Implementation
}
```

**Standards:**
- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Run `golint` before committing
- Handle errors explicitly
- Use meaningful variable names

## Testing Guidelines

### Test Coverage Requirements

- **Minimum coverage**: 70% for new code
- **Critical paths**: 90%+ coverage required
- All public APIs must have tests

### Testing by Component

#### Backend (Java)

```java
@SpringBootTest
class DeviceServiceTest {
    
    @Autowired
    private DeviceService deviceService;
    
    @Test
    void testGetDevice_WhenDeviceExists_ReturnsDevice() {
        // Arrange
        String deviceId = "test-device";
        
        // Act
        Device result = deviceService.getDevice(deviceId);
        
        // Assert
        assertNotNull(result);
        assertEquals(deviceId, result.getId());
    }
}
```

**Run tests:**
```bash
cd backend
mvn test
mvn verify  # Includes integration tests
```

#### AI Service (Python)

```python
import pytest
from src.services.query_service import QueryService

class TestQueryService:
    
    @pytest.fixture
    def query_service(self):
        return QueryService()
    
    def test_process_query_valid_input(self, query_service):
        # Arrange
        query = "Show average temperature"
        
        # Act
        result = query_service.process(query)
        
        # Assert
        assert result is not None
        assert "temperature" in result
```

**Run tests:**
```bash
cd ai-service
pytest
pytest --cov=src tests/  # With coverage
```

#### Frontend (TypeScript)

```typescript
import { render, screen } from '@testing-library/react';
import { DeviceCard } from './DeviceCard';

describe('DeviceCard', () => {
  it('renders device information', () => {
    const device = { id: '1', name: 'Test Device' };
    
    render(<DeviceCard device={device} />);
    
    expect(screen.getByText('Test Device')).toBeInTheDocument();
  });
});
```

**Run tests:**
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Testing

Create end-to-end tests for critical workflows:

```bash
# Example: Test complete data pipeline
1. Simulator publishes MQTT message
2. Node-RED enriches data
3. Collector stores in TimescaleDB
4. Backend API retrieves data
5. Frontend displays data
```

## Documentation

### Required Documentation

When adding features, update:

1. **README files** - Component-specific documentation
2. **API documentation** - OpenAPI/Swagger specs
3. **Code comments** - Complex logic and algorithms
4. **User guides** - End-user documentation
5. **Architecture diagrams** - System design updates

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep documentation up-to-date with code changes

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally (`./run-tests.sh`)
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with develop

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe tests performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one maintainer approval required
3. **Testing**: Verify in staging environment
4. **Merge**: Squash and merge to develop

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Docker version: [e.g., 24.0.0]
- Component: [e.g., backend, frontend]

**Screenshots**
If applicable

**Additional Context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Problem Description**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches considered

**Additional Context**
Screenshots, examples, etc.
```

## Development Tips

### Debugging

```bash
# View logs for specific service
docker-compose logs -f backend

# Access service shell
docker-compose exec backend bash

# Run service in debug mode
docker-compose up backend --build
```

### Hot Reload

- **Frontend**: Vite dev server with HMR
- **Backend**: Spring Boot DevTools
- **AI Service**: FastAPI with `--reload`

### Common Issues

**Problem**: Services can't communicate
```bash
# Check Docker network
docker network inspect virtplc_default

# Verify service names in docker-compose.yml
docker-compose ps
```

**Problem**: Port conflicts
```bash
# Find process using port
lsof -i :8080

# Use different ports in .env file
```

## Getting Help

- **Documentation**: Check [docs/](docs/README.md)
- **Issues**: Search [existing issues](https://github.com/Csingiling1/VirtPLC/issues)
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing to VirtPLC, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to VirtPLC! 🎉
