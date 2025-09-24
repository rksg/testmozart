# AGENTS.md - Coding Guidelines for AI Agents

## Code Style
- **Language**: Python 3.12+
- **Imports**: Use absolute imports (`from module import Class`), group standard library first
- **Type hints**: Required for function signatures (`def func(a: int, b: str) -> bool:`)
- **Docstrings**: Use triple quotes for classes and functions (`"""Description."""`)
- **Error handling**: Raise specific exceptions (`ValueError`, `TypeError`) with descriptive messages
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Testing**: Use pytest with descriptive test names (`test_the_method_with_condition`)

## Architecture
- **Framework**: Google ADK (Agents Developer Kit) with LlmAgent, SequentialAgent, LoopAgent
- **State management**: Shared session state across agents
- **Tools**: Custom tools in `tools/` directory with type validation
- **Agents**: Specialized agents in `agents/` with single responsibilities

## Key Patterns
- Agent instructions use `{state_variable}` placeholders for dynamic content
- Tools use Pydantic models for input validation
- Callbacks handle state transitions and data flow between agents
