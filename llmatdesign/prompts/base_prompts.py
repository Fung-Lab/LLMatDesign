basic_info = '''
# You are a materials science agent.

# literal_eval might be needed to convert the output to the correct type
# the method that needs literal_eval is [agent.query_document]
from ast import literal_eval

# Agent class represents the agent and its actions
class Agent:
    def __init__(self, document_path=None):
        self.gpt_model = gpt_model
        self.document = self.load_document(document_path)
        self.interaction_history = {'actions': [], 'observations': []}
    
    # Here are the admissible actions the agent can take:
    
    # query the document to complete the task
    def query_document(self, query):
        # need to use literal_eval on the output of this function
        ...

    # query the materials project API to complete the task
    def query_materials_project(self, composition, target_property):
        # do not use literal_eval on the output of this function
        supported_properties = [
            "material_id", "structure", "formation_energy_per_atom",
            "band_gap", "energy_above_hull", "symmetry", "elements", "composition"
        ]

        try:
            assert target_property in supported_properties
        except:
            raise ValueError(f"Invalid target property: {target_property}")
        ...
    
    # generate the crystal structure of given the composition
    def generate_crystal(self, composition, negative_example=None):
        ...

    # return True/False if the calculated value is within the threshold of the target value
    def is_within_threshold(self, calculated_value, target_value):
        ...

    # return dictionary of anchoring property of the material if it is found in the document
    def get_anchoring_property_from_document(self, composition):
      ...

    # perform DFT calculation to get the target property
    def dft_calculation(self, cif_file_path, type="formation_energy"):
        supported_calculation_types = [
            "formation_energy", "lattice_parameters", "xray_diffraction",
            "band_gap", "partial_charges", "magnetic_moments",
            "bulk_modulus", "shear_modulus"
        ] 

        try:
            assert type in supported_calculation_types
        except:
            raise ValueError(f"Invalid DFT calculation type: {type}")

    # ask the expert for suggestions on how to modify the structure to achieve the target property
    def ask_expert(self, structure, past_modification_str, property_type, target_property_value):
        ...
    
    # perform the modification on the structure
    def perform_modification(self, structure, suggestion):
        ...
'''.strip()

get_solution_prompt = f'''
{basic_info}
    
# Now complete the function solution() below to solve the task by composing the agent's methods. 
# For each step you plan to take, 1) mark with '[Step xx]', 2) give a reason why you think it is a good step to take

# Here is an example of a solution to the task:

<example>

# Here is the actual task.
# define agent
agent = Agent()

# <task>
# You should complete your solution function below:
def solution(agent, start_from=1):
'''.strip()

code_check_prompt = '''
You are given a Python code snippet define a function called solution. 

[Code]
<solution_func>

First, remove any code outside of the solution function. Then, answer the following questions.
Question 1: Are there any syntax error present in the code? Answer Yes/No.
Question 2: Fix the syntax errors and output an error-free version of the code. Only Output the revised code after [Revised code] without any other words.
'''.strip()

get_start_from_prompt = f'''
Previously, you generated some code defining a solution function as in [Previous solution]. The previous code is executed and outputs some error. Now you just revised the code as in [Revised solution]. Determine from which step these two version differs. You should only output the step number without saying any other words.

[Previous solution]
<previous_solution>

[Revised solution]
<revised_solution>
'''.strip()

feedback_fix_prompt = f'''
{basic_info}

# Here is a example of successful solution for solving a similar task:
[Successful example]

<example>

# Here is the actual task.
# define agent
agent = Agent()

# <task>
You have generated code of solution() to solve the task. However, you executed the solution() function and get an error message:
<error_msg>

Let's think step by step. Referring to the successful case and the error message, you should complete the solution function with the correct code.
def solution(agent, start_from=1):
'''.strip()


exec_error_prompt = f'''
{basic_info}

# Here is the actual task.
# define agent
agent = Agent()

# <task>

# Here is your generated code of solution() to solve the task:

<generated_code>

# However, you executed the solution() function and get an error message:
<error_msg>

Referring to the generated code and the error message, you should complete the solution function with the correct code.
def solution(agent, start_from=1):
'''

run_error_prompt = f'''
{basic_info}

# Here is a example of successful solution for solving a similar task:
[Successful example]

<example>

# Here is the actual task.
# define agent
agent = Agent()

# <task>

# Here is your generated code of solution() to solve the task:

<generated_code>

# However, you executed the solution() function and get an error message:
<error_msg>

Let's think step by step.. Referring to the successful example and the error message, you should modify the solution function with the correct code.
def solution(agent, start_from=1):
'''

reformat_code_prompt = """
Reformat the following Python code such that it is properly indented. Do not modify the content of the code.

<code>
"""

classify_task_prompt = """
Given the following task, which of the following two categories of tasks do you think it belongs to?

[TASK]
<task>

[Categories]
1. Materials property prediction
2. Materials discovery

Examples of outputs you should return:
- 1. Materials property prediction
- 2. Materials discovery
- 1. Materials property prediction
- 1. Materials property prediction
"""