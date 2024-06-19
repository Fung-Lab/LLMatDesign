from ast import literal_eval

from llmatdesign.utils import *
from llmatdesign.prompts.base_prompts import *
from llmatdesign.prompts.examples import *

class Planner:
    def __init__(
        self,
        llm,
        agent,
        dev_mode=True
    ):
        self.llm = llm
        self.agent = agent
        self.dev_mode = dev_mode

    def get_initial_plan(self, task, task_class):
        if task_class == "property":
            prompt_example = formation_energy_example
        elif task_class == "discovery":
            prompt_example = discovery_example

        # get initial plan
        prompt = get_solution_prompt.replace("<task>", task).replace("<example>", prompt_example)
        initial_response = self.llm.ask(prompt)
        initial_response = add_solution_func_definition(get_function_string(initial_response))

        # check code of initial plan
        check_code_prompt = code_check_prompt.replace("<solution_func>", initial_response)
        check_code_response = self.llm.ask(check_code_prompt)

        # format initial plan
        answers = extract_answers(check_code_response, ['[Decision]', '[Revised code]'])
        solution_func = get_function_string(answers[-1])

        return solution_func

    def exec_plan(self, plan):
        """
        exec create a function using the plan
        the function is not called
        """
        _locals = locals()
        error_msg = None

        try:
            exec(plan, globals(), _locals)
        except Exception as e:
            error_msg = str(e)
        
        return _locals, error_msg
    
    def fix_exec_error(self, plan, error_msg):
        prompt = exec_error_prompt.replace("<error_msg>", error_msg).replace("<generated_code>", plan)
        revised_response = self.llm.ask(prompt)
        revised_response = add_solution_func_definition(get_function_string(revised_response))

        # check code of revised plan
        check_code_prompt = code_check_prompt.replace("<solution_func>", revised_response)
        check_code_response = self.llm.ask(check_code_prompt)

        # format revised plan
        answers = extract_answers(check_code_response, ['[Decision]', '[Revised code]'])
        solution_func = get_function_string(answers[-1])

        return solution_func

    def call_plan(self, func, agent, step):
        """
        call the function created by the plan
        """
        # Store the original standard output and standard error
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # Redirect the standard output and error to in-memory file-like objects
        temp_stdout = io.StringIO()
        temp_stderr = io.StringIO()
        sys.stdout = temp_stdout
        sys.stderr = temp_stderr

        checkpoint = None
        func_output = None
        # Run the function and capture exceptions
        try:
            func_output = func(agent, start_from=step)
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
        return func_output, error_string, checkpoint, output_string + error_string
    
    def fix_run_error(self, plan, error_msg):
        # TO-DO: need to way to choose a right example
        example = formation_energy_example

        prompt = run_error_prompt\
                .replace("<error_msg>", error_msg)\
                .replace("<generated_code>", plan)\
                .replace("<example>", example)
        
        updated_plan = self.llm.ask(prompt)
        updated_plan = add_solution_func_definition(get_function_string(updated_plan))
        
        # check code of updated plan
        check_code_prompt = code_check_prompt.replace("<solution_func>", updated_plan)
        check_code_response = self.llm.ask(check_code_prompt)

        # format updated plan
        answers = extract_answers(check_code_response, ['[Decision]', '[Revised code]'])
        solution_func = get_function_string(answers[-1])

        return solution_func

    def get_start_from(self, prev_plan, new_plan):
        prompt = get_start_from_prompt\
            .replace("<previous_solution>", prev_plan)\
            .replace("<revised_solution>", new_plan)
        response = self.llm.ask(prompt)
        start_num = get_first_digit(response)
        return start_num

    def classify_task(self, task):
        prompt = classify_task_prompt.replace("<task>", task)
        response = self.llm.ask(prompt)

        print("Task classification: ", response)

        if '1' in response:
            return "property"
        elif '2' in response:
            return "discovery"
        else:
            raise Exception("Failed to classify the task")
    
    def run_task(self, task, n_exec_revisions=3, n_tries=5):
        # classify task
        task_class = self.classify_task(task)

        # get initial plan
        initial_plan = self.get_initial_plan(task, task_class)
        
        if self.dev_mode:
            print(initial_plan)
            return

        # execute initial plan
        exec_count = 0
        exec_plan_variables, error_msg = self.exec_plan(initial_plan)
        while error_msg is not None and exec_count < n_exec_revisions:
            initial_plan = self.fix_exec_error(initial_plan, error_msg)
            exec_plan_variables, error_msg = self.exec_plan(initial_plan)
            exec_count += 1
        
        if error_msg is not None:
            raise Exception(f"Failed to exec the plan: {error_msg}")
        
        # call the function created by exec
        start_num = 1
        for _try in range(n_tries):
            solution_func = exec_plan_variables['solution']
            func_output, error_msg, checkpoint, output_string = self.call_plan(solution_func, self.agent, start_num)
            if self.agent.is_success:
                print("Agent: ", func_output)
                break
            
            # run with error
            if error_msg is not None:
                print("run error: ", error_msg)
                updated_plan = self.fix_run_error(initial_plan, error_msg)
                start_num = self.get_start_from(initial_plan, updated_plan)
                print(f"updated plan: {updated_plan}")
                print(f"start from: {start_num}")
                
                # execute updated plan
                exec_plan_variables, error_msg = self.exec_plan(updated_plan)
                solution_func = exec_plan_variables['solution']
            # run success but not complete
            elif not self.agent.is_success:
                pass