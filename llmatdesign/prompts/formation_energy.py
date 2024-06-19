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