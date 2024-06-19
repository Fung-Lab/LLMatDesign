import os
import ase
import ast

from llmatdesign.prompts.gpt import *
from llmatdesign.prompts.utils import *

def discover_bandgap(
    agent,
    chemical_formula: str,
    structure: ase.Atoms = None,
    band_gap: float = None,
    target_value: float = 1.4,
    max_iterations: int = 50
):
    # query materials project
    if structure is None:
        _, structure = agent.query_materials_project(chemical_formula, 'structure')
    if band_gap is None:
        _, band_gap = agent.query_materials_project(chemical_formula, 'band_gap')
    
    # ask the expert for suggestions
    suggestions_list = [None]
    structures_list = [structure]
    band_gaps_list = [band_gap]
    reflections_list = [None]

    for i in range(max_iterations):
        # get prompt
        prompt = format_prompt(
            base_template_bandgap,
            suggestions_list, 
            structures_list, 
            band_gaps_list,
            reflections_list,
            property_type='band_gap', 
            target_property=target_value
        )

        print(prompt)

        # get modification
        modification_str = get_action(agent.llm, prompt)
        modification = ast.literal_eval(modification_str)

        new_structure, new_band_gap = agent.perform_modification(
            structures_list[-1], 
            modification["Modification"], 
            calculation_type='band_gap'
        )

        # get post action reflection
        reflection_prompt = get_reflection_prompt(
            structures_list[-1].get_chemical_formula('metal'),
            new_structure.get_chemical_formula('metal'),
            modification_str,
            target_value,
            band_gaps_list[-1],
            new_band_gap
        )

        # self-reflection
        reflection = get_reflection(agent.llm, reflection_prompt)

        suggestions_list.append(modification_str)
        structures_list.append(new_structure)
        band_gaps_list.append(new_band_gap)
        reflections_list.append(reflection)

        if agent.is_within_threshold(new_band_gap, target_value):
            return True, suggestions_list, structures_list, band_gaps_list, reflections_list
    
    return False, suggestions_list, structures_list, band_gaps_list, reflections_list
