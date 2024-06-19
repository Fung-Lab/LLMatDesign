formation_energy_example = """
# Your task is to: get the formation energy of Co2TiO4
# here is a solution:
def solution(agent, start_from=1):
    # General Plan: I need to check if the formation energy of Co2TiO4 is reported in the document. 
    # If it is not reported, I need to query Materials Project API to get the formation energy.
    # If Co2TiO4 is not found in Materials Project, I need to generate the crystal structure and
    # use DFT calculations to get the formation energy.
    if start_from <= 1:
        print("[Step 1] query the document to get the formation energy of Co2TiO4")
        answer = agent.query_document('what is the formation energy of Co2TiO4')
        # use literal_eval to convert the returned answer to a list.
        answer_to_check = literal_eval(answer)
        # expectation: the returned answer should be length of 2. 
        assert len(answer_to_check) == 2, f'Error in [Step 1]: The returned answer should be length of 2. {agent.report()}'
        # expectation: the first element of the returned answer should be boolean.
        assert isinstance(answer_to_check[0], bool), f'Error in [Step 1]: The first element of the returned answer should be boolean. {agent.report()}'
        if answer_to_check[0]:
            agent.is_success = True
            return answer_to_check[1]
    
    if start_from <= 2:
        print("[Step 2] query Materials Project API to get the formation energy of Co2TiO4")
        answer = agent.query_materials_project('Co2TiO4', 'formation_energy_per_atom')
        # do not use literal_eval here because the returned answer is a list.
        # expectation: the returned answer should be length of 2. 
        assert len(answer) == 2, f'Error in [Step 2]: The returned answer should be length of 2. {agent.report()}'
        # expectation: the first element of the returned answer should be boolean.
        assert isinstance(answer[0], bool), f'Error in [Step 2]: The first element of the returned answer should be boolean. {agent.report()}'
        if answer[0]:
            agent.is_success = True
            return answer[1]

    if start_from <= 3:
        print("[Step 3] generate the crystal structure of Co2TiO4")
        cif_file_path = agent.generate_crystal('Co2TiO4')
        # expectation: the returned cif_file_path should exist.
        assert os.path.exists(cif_file_path), f'Error in [Step 3]: The returned cif_file_path should exist. {agent.report()}'
        agent.is_success = True

    if start_from <= 4:
        print("[Step 4] use DFT calculations to get the formation energy of Co2TiO4")
        formation_energy = agent.dft_calculation(cif_file_path, type="formation_energy")
        # expectation: the returned formation_energy should be a float.
        assert isinstance(formation_energy, float), f'Error in [Step 4]: The returned formation_energy should be a float. {agent.report()}'
        agent.is_success = True
        return formation_energy
"""

discovery_example = """
# Your task is to: use Co2TiO4 to discover a new material that has a formation energy of -3.5 eV/atom
# here is a solution:
def solution(agent, start_from=1):
    # General Plan: I will first query Materials Project API to get the crystal structure and formation energy of Co2TiO4.
    # If Co2TiO4 is not found in Materials Project, I need to first generate a crystal structure.
    # Then, I will use the `agent.ask_expert()` method to get suggestions on how to modify the current structure
    # for a new material with the target formation energy.
    if start_from <= 1:
        print("[Step 1] query Materials Project API to get the structure and formation energy of Co2TiO4")
        if_structure, structure = agent.query_materials_project('Co2TiO4', 'structure')
        if_formation_energy, formation_energy = agent.query_materials_project('Co2TiO4', 'formation_energy_per_atom')
        if if_structure and if_formation_energy:
            # structure and formation energy of Co2TiO4 are found
            start_from = 3

    if start_from <= 2:
        print("[Step 2] generate the crystal structure of Co2TiO4")
        cif_file_path = agent.generate_crystal('Co2TiO4')
        # expectation: the returned cif_file_path should exist.
        assert os.path.exists(cif_file_path), f'Error in [Step 3]: The returned cif_file_path should exist. {agent.report()}'
        structure = ase.io.read(cif_file_path)
    
    if start_from <= 3:
        print("[Step 3] ask the expert for suggestions on how to modify the structure")
        number_of_iterations = 10
        suggestions_list = ["NIL"]
        structures_list = [structure]
        formation_energies_list = [formation_energy]

        for i in range(number_of_iterations):
            print(f"Modification iteration: {i+1}")
            # get the past modifications as a string
            past_modifications_str = agent.get_past_modifications(suggestions_list, structures_list, formation_energies_list)
            # get a suggestion from the expert
            suggestion = agent.ask_expert(structures_list[-1], past_modifications_str, property_type='formation_energy', target_property_value=-3.5)
            print(f"Suggestion: {suggestion}")
            # perform the suggested modification
            new_structure, new_formation_energy = agent.perform_modification(structures_list[-1], suggestion)
            print(f"New formation energy: {new_formation_energy}")
            # add to lists
            suggestions_list.append(suggestion)
            structures_list.append(new_structure)
            formation_energies_list.append(new_formation_energy)
            # check if the target formation energy is reached
            if agent.is_within_threshold(new_formation_energy, -3.5):
                print(f"Found a new material with the target formation energy: {new_formation_energy}")
                return True, structures_list, formation_energies_list
        return False, structures_list, formation_energies_list
"""
