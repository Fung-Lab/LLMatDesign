anchoring_dft_example = """
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
        print("[Step 3] generate the crystal structure of Co2TiO4 and anchor the DFT calculation if possible")
        # anchoring_property is a dictionary that contains the anchoring property of the material if it is found in the document.
        anchoring_property = agent.get_anchoring_property_from_document('Co2TiO4')
        # generate initial crystal structure
        cif_file_path = agent.generate_crystal('Co2TiO4')
        if not anchoring_property:
            # since no properties are found in the document, anchoring of DFT calculation is not possible.
            # proceed to the actual DFT calculation.
            print("Anchoring of DFT calculation is not possible.")
        else:
            # anchoring of DFT calculation is possible.
            property, target_value = list(anchoring_property.items())[0]
            print(f"Anchoring of DFT calculation is possible for {property} with target value {target_value}")
            # anchoring loop: run the DFT calculation for the property and check if the calculated value is within the threshold of the target value.
            # if the calculated property is within the threshold of the target value, then the DFT calculation is anchored.
            # if not, then we generate a new crystal structure with the previous crystal as a negative example and repeat the process.
            n_attempts = 5
            for _attempt in range(n_attempts):
                print(f"Anchoring attempt {_attempt+1}/{n_attempts}")
                # use DFT calculations to get the property
                calculated_value = agent.dft_calculation(cif_file_path, type=property)
                # expectation: the returned calculated_value should be a float.
                assert isinstance(calculated_value, float), f'Error in [Step 3]: The returned calculated_value should be a float. {agent.report()}'
                if agent.is_within_threshold(calculated_value, target_value):
                    print(f"Anchoring successful for {property} with target value {target_value}. Calculated value: {calculated_value}.")
                    break
                else:
                    print(f"Anchoring failed for {property} with target value {target_value}. Calculated value: {calculated_value}.")
                    # regenerate the crystal structure
                    cif_file_path = agent.generate_crystal('Co2TiO4', negative_example=cif_file_path)

        # expectation: the cif_file_path should exist.
        assert os.path.exists(cif_file_path), f'Error in [Step 3]: The returned cif_file_path should exist. {agent.report()}'

    if start_from <= 4:
        print("[Step 4] use DFT calculations to get the formation energy of Co2TiO4")
        formation_energy = agent.dft_calculation(cif_file_path, type="formation_energy")
        # expectation: the returned formation_energy should be a float.
        assert isinstance(formation_energy, float), f'Error in [Step 4]: The returned formation_energy should be a float. {agent.report()}'
        agent.is_success = True
        return formation_energy
"""