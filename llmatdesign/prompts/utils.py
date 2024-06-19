from llmatdesign.utils import extract_python_code

def get_past_modifications(
    suggestions_list, 
    structures_list, 
    properties_list, 
    reflections_list
):
    history = ""
    if suggestions_list[-1] is None:
        return None
    else:
        history += "You may also want to make use of the past modifications below:\n"

    # enumerate
    for i, (suggestion, structure, property_value, reflection) in enumerate(
            zip(suggestions_list[1:], structures_list[1:], properties_list[1:], 
                reflections_list[1:])):
        l = (f"{i+1}. Modification: {suggestion}. "
             f"Post-modification reflection: {reflection}.\n")
        history += l

    return history

def format_prompt(
    prompt_template, 
    suggestions_list, 
    structures_list, 
    properties_list, 
    reflections_list, 
    property_type, 
    target_property
):
    past_modifications = get_past_modifications(
        suggestions_list, 
        structures_list, 
        properties_list, 
        reflections_list
    )

    prompt = prompt_template.replace(
        "<chemical_formula>", 
        structures_list[-1].get_chemical_formula('metal')
    )
    prompt = prompt.replace("<band_gap>", f"{properties_list[-1]:.2f}")

    if past_modifications is not None:
        prompt += past_modifications

    return prompt

def format_historyless_prompt(
    prompt_template, 
    suggestions_list, 
    structures_list,
    properties_list, 
    reflections_list,
    property_type, 
    target_property
):
    prompt = prompt_template.replace(
        "<chemical_formula>", 
        structures_list[-1].get_chemical_formula('metal')
    )
    prompt = prompt.replace("<band_gap>", f"{properties_list[-1]:.2f}")

    return prompt

def get_reflection_prompt(
    previous_chemical_formula, 
    current_chemical_formula, 
    modification, 
    target_value, 
    previous_value, 
    current_value
):
    base = (
        f"After completing the following modification on the material "
        f"{previous_chemical_formula}, we obtained {current_chemical_formula} "
        f"the band gap value changed from {previous_value:.2f} eV to "
        f"{current_value:.2f} eV. Please write a post-action reflection on "
        f"the modification in a short sentence on how successful the modification "
        f"was in achieving the target band gap value of {target_value} eV and why so:\n"
        f"<modification>"
    )

    base = base.replace("<previous_chemical_formula>", previous_chemical_formula)
    base = base.replace("<current_chemical_formula>", current_chemical_formula)
    base = base.replace("<previous_value>", str(previous_value))
    base = base.replace("<current_value>", str(current_value))
    base = base.replace("<target_value>", str(target_value))
    base = base.replace("<modification>", str(modification))

    return base

def get_action(llm, prompt):
    count = 0
    while True:
        llm_response = llm.ask(prompt)
        code = extract_python_code(llm_response)
        code = code.strip()

        if code.startswith("{") and code.endswith("}"):
            return code
        
        count += 1
        if count > 5:
            raise ValueError("Failed to get the action code string.")
        
def get_reflection(llm, prompt):
    return llm.ask(prompt)