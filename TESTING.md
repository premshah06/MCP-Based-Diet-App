# Diet Coach MCP - Testing Guide

This document provides comprehensive information about testing the Diet Coach MCP application.

## Test Structure

### FastAPI App Tests (`apps/diet-api/test_main.py`)
- **Health Endpoint Tests**: Verify health check functionality
- **TDEE Endpoint Tests**: Test calorie and macro calculations for different scenarios
- **Meal Plan Endpoint Tests**: Test meal plan generation with various dietary restrictions
- **Explain Endpoint Tests**: Test nutrition explanations with and without OLLAMA
- **Calculation Function Tests**: Unit tests for BMR, TDEE, and macro calculations
- **Food Filtering Tests**: Test dietary restriction filtering logic

### MCP Server Tests (`apps/diet-mcp/test_server.py`)
- **Schema Validation Tests**: Test Pydantic model validation
- **MCP Handler Tests**: Test MCP protocol implementations
- **API Request Tests**: Test external API communication
- **Tool Execution Tests**: Test all three MCP tools
- **Environment Configuration Tests**: Test configuration handling
- **Integration Tests**: End-to-end workflow testing

## Running Tests

### Quick Start
```bash
# Run all tests with coverage
make test

# Run fast tests only (exclude slow tests)
make test-fast

# Run specific component tests
make test-api
make test-mcp
```

### Using Python Test Runner
```bash
# Install dependencies and run all tests
python test_runner.py --install-deps --coverage --lint

# Run specific component
python test_runner.py --component api --coverage

# Run specific test pattern
python test_runner.py --test-pattern "test_tdee"

# Fast tests only
python test_runner.py --fast
```

### Using Pytest Directly
```bash
# FastAPI tests
cd apps/diet-api
pip install -r requirements.txt -r test_requirements.txt
pytest -v --cov=main

# MCP tests  
cd apps/diet-mcp
pip install -r requirements.txt -r test_requirements.txt
pytest -v --cov=server
```

## Test Categories

### Unit Tests
- Individual function testing
- Input validation
- Calculation accuracy
- Error handling

### Integration Tests
- API endpoint workflows
- MCP tool execution
- External service communication
- Data flow validation

### Coverage Requirements
- **FastAPI App**: Minimum 80% coverage
- **MCP Server**: Minimum 75% coverage

## Test Data

### Foods Database
Tests use a subset of the main foods database with representative items:
- Chicken Breast (animal protein)
- Firm Tofu (plant protein)
- Brown Rice (carbohydrates)
- Broccoli (vegetables)
- Olive Oil (fats)

### Sample Requests
- **Male, 30 years, 175cm, 70kg, Moderate activity, Cutting**
- **Female, 25 years, 165cm, 60kg, Active, Bulking**
- Various dietary restrictions (vegan, vegetarian, budget, lactose-free)

## Mocking Strategy

### External Dependencies
- **OLLAMA API**: Mocked for explanation endpoint tests
- **Diet API**: Mocked in MCP server tests
- **File System**: Temporary files for foods database

### Network Requests
All external HTTP requests are mocked to ensure:
- Test reliability
- Fast execution
- Predictable results
- No external dependencies

## Continuous Integration

### GitHub Actions Workflow
- Tests on Python 3.11 and 3.12
- Matrix testing for both components
- Linting with flake8
- Coverage reporting
- Integration tests with Docker

### Local CI Simulation
```bash
# Run the same checks as CI
make lint
make test
make build
make up
# Manual API testing
make down
```

## Test Fixtures

### Common Fixtures
- `test_foods_data`: Sample foods database
- `test_foods_file`: Temporary foods.json file
- `client`: FastAPI test client
- `mock_api_success`: Successful API responses

### Request Fixtures
- `sample_tdee_request`: Standard TDEE calculation
- `sample_mealplan_request`: Standard meal plan
- `sample_explain_plan_args`: Nutrition explanation

## Performance Testing

### Timing Expectations
- TDEE calculations: < 100ms
- Meal plan generation: < 500ms
- API requests: < 30s timeout
- MCP tool execution: < 60s total

### Load Testing (Optional)
```bash
# Install locust for load testing
pip install locust

# Create load test script for API endpoints
# Run with: locust -f load_test.py --host=http://localhost:8000
```

## Debugging Tests

### Verbose Output
```bash
pytest -v -s  # Show print statements
pytest --tb=long  # Detailed tracebacks
pytest --pdb  # Drop into debugger on failure
```

### Coverage Analysis
```bash
# Generate HTML coverage report
pytest --cov=main --cov-report=html
# Open htmlcov/index.html in browser
```

### Test-Specific Debugging
```bash
# Run single test
pytest test_main.py::TestTDEEEndpoint::test_calculate_tdee_male_cut -v

# Run tests matching pattern
pytest -k "tdee" -v
```

## Common Issues & Solutions

### Import Errors
- Ensure all dependencies are installed
- Check Python path includes app directories
- Verify relative imports

### API Connection Errors
- Check if services are running (`make up`)
- Verify port configurations
- Ensure network connectivity

### Coverage Issues
- Add `# pragma: no cover` for uncoverable lines
- Test error conditions and edge cases
- Mock external dependencies properly

### Async Test Issues
- Use `pytest-asyncio` plugin
- Mark async tests with `@pytest.mark.asyncio`
- Ensure proper async/await usage

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Keep tests focused and isolated

### Mock Usage
- Mock at the boundary (external calls)
- Use dependency injection where possible
- Verify mock calls with assertions
- Reset mocks between tests

### Data Management
- Use fixtures for test data
- Keep test data minimal but representative
- Clean up temporary files/resources
- Use factories for complex objects

### Assertions
- Test behavior, not implementation
- Use specific assertions over generic ones
- Test both success and failure cases
- Validate all relevant response fields

## Future Enhancements

### Potential Additions
- Property-based testing with Hypothesis
- Mutation testing with mutpy
- Performance benchmarking
- Security testing
- API contract testing

### Test Data Expansion
- More diverse food database
- Edge case user profiles
- Complex dietary restrictions
- Regional food variations

This testing framework ensures the Diet Coach MCP application is robust, reliable, and ready for production deployment.
