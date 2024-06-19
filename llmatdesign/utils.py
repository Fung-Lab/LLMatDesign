import re
import io
import sys
import traceback

def extract_answers(text, markers):
    answers = []
    for i, marker in enumerate(markers):
        if i < len(markers) - 1:
            next_marker = markers[i + 1]
            pattern = fr"{re.escape(marker)}\s*([\s\S]*?)\n*{re.escape(next_marker)}"
        else:
            pattern = fr"{re.escape(marker)}\s*([\s\S]*)"
        
        answer = re.search(pattern, text)
        if answer:
            answer = answer.group(1).strip()
            answers.append(answer)
        else:
            answers.append('Not found')
        
    return answers

def get_error_step(error_message):
    pattern = r'\[Step (\d+)\]'
    match = re.search(pattern, error_message)
    if match:
        return int(match.group(1))

    return None
    
def get_first_digit(input_string):
    pattern = r'\d'
    match = re.search(pattern, input_string)
    if match:
        return int(match.group())

    return None

# this function modifies the header of the solution to load the variables from the breakpoint
def modify_header(checkpoint):
    if not checkpoint:
        return 'def solution(agent, start_from=1):'
    load_checkpoint = ''
    skip_vars = ['agent', 'start_from']
    for k,v in checkpoint.items():
        if k not in skip_vars:
            if type(v) == str:
                load_checkpoint += f', {k}="{v}"'
            else:
                load_checkpoint += f', {k}={v}'
    header = f'def solution(agent, start_from{load_checkpoint}):'
    return header

# this function captures the assertion error message and stores the local variables inside the solution at the breakpoint.
def capture_output(func, agent, step=1):
    # Store the original standard output and standard error
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Redirect the standard output and error to in-memory file-like objects
    temp_stdout = io.StringIO()
    temp_stderr = io.StringIO()
    sys.stdout = temp_stdout
    sys.stderr = temp_stderr

    checkpoint = None
    # Run the function and capture exceptions
    try:
        func(agent, start_from=step)
    except Exception as e:
        traceback.print_exc()
        checkpoint = sys.exc_info()[2].tb_next.tb_frame.f_locals

    # Restore the original standard output and error
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    # Get the output and error messages as strings
    output_string = temp_stdout.getvalue()
    error_string = temp_stderr.getvalue()

    print(output_string)
    print(error_string)
    return error_string, checkpoint, output_string + error_string

def get_function_string(s):
    l = s.split('\n')

    start_idx = None
    end_idx = None

    for i, line in enumerate(l):
        if line.startswith('def solution(agent'):
            start_idx = i
        elif isinstance(start_idx, int) and start_idx is not None:
            if not line.startswith(' ') and line != '':
                end_idx = i
                break
    
    if start_idx is not None and end_idx is not None:
        return '\n'.join(l[start_idx:end_idx]).strip()
    elif start_idx is not None and end_idx is None:
        return '\n'.join(l[start_idx:]).strip()
    
    return s

def extract_python_code(text):
    pattern = r'```python\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return text
    
def add_solution_func_definition(text):
    solution_func = '''
    def solution(agent, start_from=1):
        <solution>
    '''.strip().replace('<solution>', text) if not text.startswith('def solution(agent, start_from=1):') else text
    return solution_func
