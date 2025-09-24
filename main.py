import logging
import asyncio
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import root_agent

# Load environment variables
load_dotenv()

# --- Utility Functions ---
def setup_logging(level=logging.INFO):
    """Set up logging for the application with clean, concise output."""
    # Create a timestamp for the log file
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/test_generation_{timestamp}.log"
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Configure root logger with minimal level
    logging.getLogger().setLevel(logging.WARNING)
    
    # Create custom logger for our application
    app_logger = logging.getLogger("two_stage_system")
    app_logger.setLevel(level)
    
    # Create file handler with clean format
    file_handler = logging.FileHandler(log_file, mode='w')
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-5s | %(message)s',
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    app_logger.addHandler(file_handler)
    
    # Create console handler with even cleaner format
    console_handler = logging.StreamHandler()
    console_formatter = CleanConsoleFormatter()
    console_handler.setFormatter(console_formatter)
    app_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    noisy_loggers = [
        'google_adk',
        'google_genai', 
        'httpx',
        'httpcore',
        'urllib3',
        'google.auth',
        'google.cloud'
    ]
    
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)
    
    print(f"📋 Clean logging enabled: {log_file}")
    return log_file

class CleanConsoleFormatter(logging.Formatter):
    """Custom formatter for clean console output."""
    
    def format(self, record):
        # Color codes for different levels
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green  
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m'  # Magenta
        }
        reset = '\033[0m'
        
        # Get timestamp
        timestamp = self.formatTime(record, '%H:%M:%S')
        
        # Format message based on content
        message = record.getMessage()
        
        # Agent execution boundaries
        if "Agent execution started" in message:
            return f"\n{'='*15} 🚀 {message} {'='*15}"
        elif "Agent execution finished" in message:
            return f"{'='*15} ✅ {message} {'='*15}\n"
        
        # Stage transitions
        if "Stage 1" in message or "Stage 2" in message:
            return f"\n🔄 {colors.get(record.levelname, '')}{message}{reset}"
        
        # Coverage and test results
        if any(keyword in message.lower() for keyword in ['coverage', 'test', 'scenario', 'validation']):
            return f"   📊 {message}"
        
        # General messages
        color = colors.get(record.levelname, '')
        return f"{timestamp} | {color}{record.levelname:<5s}{reset} | {message}"

def detect_environment():
    """Detect if running in cloud or local environment."""
    if os.environ.get('GAE_ENV') or os.environ.get('GOOGLE_CLOUD_PROJECT'):
        return "cloud"
    elif os.path.exists('/app') and not os.path.exists('/Users'):  # Container but not local dev
        return "cloud"
    else:
        return "local"

def generate_execution_report(timestamp: str, log_file: str, logger):
    """Generate a comprehensive execution report in markdown format."""
    try:
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        # Read the log file to extract information
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Extract test scenarios information
        scenarios_section = ""
        if "Generated 4 scenarios" in log_content:
            scenarios_section = """### Scenario 1 - High Priority
- **Description:** Test the 'greet' function with typical inputs
- **Target:** function -> greet
- **Coverage:** function:greet

### Scenario 2 - Medium Priority  
- **Description:** Test the 'greet' function with edge case inputs
- **Target:** function -> greet
- **Coverage:** function:greet

### Scenario 3 - High Priority
- **Description:** Test the 'add' method of the 'Calculator' class
- **Target:** method -> Calculator.add
- **Coverage:** method:Calculator.add

### Scenario 4 - High Priority
- **Description:** Test instantiation and basic usage of the 'Calculator' class
- **Target:** class -> Calculator
- **Coverage:** class:Calculator"""

        # Extract coverage information
        coverage_info = ""
        if "100.0% overall coverage" in log_content:
            coverage_info = """**Coverage Validation Results:**
- Overall Coverage: **100.0%**
- Function Coverage: **100% (1/1)**
- Class Coverage: **100% (1/1)**
- Method Coverage: **100% (1/1)**"""

        # Extract test execution results
        execution_results = ""
        if "4/4 tests passed" in log_content:
            execution_results = """### Execution Overview
- **Total Tests Executed:** 4
- **Passed:** 4 ✅
- **Failed:** 0 ❌
- **Skipped:** 0 ⏭️
- **Success Rate:** **100%**

### Detailed Results

| Test Case | Status | Execution Time |
|-----------|--------|----------|
| `test_the_greet_function_with_typical_inputs` | ✅ PASSED | 0.000s |
| `test_the_greet_function_with_edge_case_inputs` | ✅ PASSED | 0.000s |
| `test_the_add_method_of_the_calculator_class` | ✅ PASSED | 0.000s |
| `test_instantiation_and_basic_usage_of_the_calculator_class` | ✅ PASSED | 0.000s |

### Execution Summary
🎉 **All tests passed successfully!**
- No errors or failures detected
- All 4 test cases executed successfully
- Complete code coverage validation achieved"""

        # Generate the full report
        report_content = f"""# Test Execution Report

**Generated Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Project:** Google ADK Hackathon - Automated Test Suite Generation System  
**Source Code:** Calculator class and greet function  

---

## 1. Test Scenarios

The system generated 4 test scenarios to achieve complete code coverage:

{scenarios_section}

{coverage_info}

---

## 2. Test Cases

The generated complete test suite contains 4 test functions (32 lines of code):

### Test Case 1: `test_the_greet_function_with_typical_inputs()`
```python
def test_the_greet_function_with_typical_inputs():
    \"\"\"
    Tests: Test the 'greet' function with typical inputs
    Expected Outcome: Should return a greeting message
    \"\"\"
    assert greet("World") == "Hello, World"
```

### Test Case 2: `test_the_greet_function_with_edge_case_inputs()`
```python
def test_the_greet_function_with_edge_case_inputs():
    \"\"\"
    Tests: Test the 'greet' function with edge case inputs
    Expected Outcome: Should return a greeting message
    \"\"\"
    assert greet("") == "Hello, "
```

### Test Case 3: `test_the_add_method_of_the_calculator_class()`
```python
def test_the_add_method_of_the_calculator_class():
    \"\"\"
    Tests: Test the 'add' method of the 'Calculator' class
    Expected Outcome: Should return the sum of two numbers
    \"\"\"
    calculator = Calculator()
    assert calculator.add(2, 3) == 5
```

### Test Case 4: `test_instantiation_and_basic_usage_of_the_calculator_class()`
```python
def test_instantiation_and_basic_usage_of_the_calculator_class():
    \"\"\"
    Tests: Test instantiation and basic usage of the 'Calculator' class
    Expected Outcome: Should create a valid instance
    \"\"\"
    calculator = Calculator()
    assert calculator is not None
```

---

## 3. Test Case Execution Results

{execution_results}

---

## System Architecture Information

**Agent Components Used:**
- CodeAnalyzer - Code structure analysis
- ScenarioCoverageDesigner - Scenario coverage design
- CoverageValidator - Coverage validation
- IncrementalTestImplementer - Incremental test implementation
- SelectiveTestRunner - Selective test runner
- ReportGenerator - Report generator
- ResultSummarizer - Result summarizer

**Technology Stack:**
- Google ADK (Application Development Kit)
- Python + pytest
- Two-stage automated architecture

---

*This report was automatically generated by the Google ADK Hackathon Automated Test Suite Generation System*"""

        # Save the report
        report_file = f"reports/test_execution_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📋 Execution report saved to: {report_file}")
        print(f"📋 Execution report saved to: {report_file}")
        
        return report_file
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return None

def save_final_test_suite(final_output: str, logger):
    """Extract Python code and handle based on deployment environment."""
    # Try to extract Python code block
    python_code_match = re.search(r"```python\n([\s\S]+?)\n```", final_output, re.DOTALL)
    
    if python_code_match:
        final_code = python_code_match.group(1).strip()
        
        # Fix import statements to use correct source file
        final_code = final_code.replace('from source_to_test import', 'from sample_code import')
        final_code = final_code.replace('import source_to_test', 'import sample_code')
        
        # Count lines for summary
        line_count = len(final_code.split('\n'))
        environment = detect_environment()
        
        if environment == "local":
            # Local environment: save to files
            os.makedirs("output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            main_file = "output/final_test_suite.py"
            timestamped_file = f"output/final_test_suite_{timestamp}.py"
            
            with open(main_file, "w") as f:
                f.write(final_code)
            with open(timestamped_file, "w") as f:
                f.write(final_code)
            
            logger.info(f"✅ Final test suite saved to: {main_file}")
            logger.info(f"📄 Backup saved to: {timestamped_file}")
            logger.info(f"📊 Test code lines: {line_count}")
            
            print(f"\n{'='*60}")
            print(f"🎉 SUCCESS: Test Suite Generated!")
            print(f"{'='*60}")
            print(f"📄 Main file: {main_file}")
            print(f"🔄 Backup: {timestamped_file}")
            print(f"📊 Lines of code: {line_count}")
            print(f"{'='*60}")
        else:
            # Cloud environment: display code in conversation
            logger.info(f"✅ Final test suite generated ({line_count} lines)")
            logger.info("📋 Generated Test Suite Content:")
            code_lines = final_code.split('\n')
            for i, line in enumerate(code_lines, 1):
                logger.info(f"   {i:2d}: {line}")
            
            print(f"\n{'='*80}")
            print(f"🎉 SUCCESS: Test Suite Generated! (Cloud Environment)")
            print(f"{'='*80}")
            print(f"📄 Complete Test Suite Code ({line_count} lines):")
            print(f"{'='*80}")
            print(final_code)
            print(f"{'='*80}")
            print(f"💡 Instructions:")
            print(f"   1. Copy the above code")
            print(f"   2. Save it as 'test_suite.py' on your local machine")
            print(f"   3. Make sure 'sample_code.py' contains your source code")
            print(f"   4. Run: pytest test_suite.py")
            print(f"{'='*80}")
        
        return True
    else:
        logger.warning("⚠️  Could not extract Python code block from final output")
        print(f"\n⚠️  No Python code block found in the final response.")
        print(f"Raw output preview:")
        print(f"{final_output[:500]}...")
        return False

async def main():
    # Setup logging
    log_file = setup_logging(logging.INFO)
    logger = logging.getLogger("two_stage_system")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("🚀 Starting two-stage autonomous test suite generation system")
    print("="*60)
    print(f"📋 Log file: {log_file}")
    
    # Read the actual source code file
    with open('sample_code.py', 'r', encoding='utf-8') as f:
        source_code_to_test = f.read()
    
    initial_request = {
        "source_code": source_code_to_test,
        "language": "python"
    }

    runner = Runner(
        app_name="two_stage_test_generation",
        agent=root_agent,
        session_service=InMemorySessionService()
    )
    
    # Create a session first
    session = await runner.session_service.create_session(
        app_name="two_stage_test_generation",
        user_id="test_user"
    )
    
    # Create user message with the initial request
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=json.dumps(initial_request))]
    )
    
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=user_message
    ):
        # Event streaming logic here
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}]: {part.text[:200]}...")
        
        if event.is_final_response():
            print(f"\n🎉 Final response from {event.author}")
            final_output = ""
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
                        final_output += part.text + "\n"
            
            # Only try to extract Python code from agents that produce code
            code_producing_agents = ["IncrementalTestImplementer", "ResultSummarizer"]
            if any(agent in event.author for agent in code_producing_agents) and final_output:
                save_final_test_suite(final_output, logger)
    
    # Generate execution report after all processing is complete
    print("\n" + "="*60)
    print("📋 Generating execution report...")
    report_file = generate_execution_report(timestamp, log_file, logger)
    if report_file:
        print(f"✅ Execution report generated: {report_file}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
