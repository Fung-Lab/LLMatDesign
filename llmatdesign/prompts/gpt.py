base_template_bandgap = """
I have a material and its band gap value. A band gap is the distance \
between the valence band of electrons and the conduction band, \
representing the minimum energy that is required to excite an electron to the conduction band.

(<chemical_formula>, <band_gap>)

Please propose a modification to the material that results in a band gap of 1.4 eV. \
You can choose one of the four following modifications:
1. exchange: exchange two elements in the material
2. substitute: substitute one element in the material with another
3. remove: remove an element from the material
4. add: add an element to the material

Your output should be a python dictionary of the following the format: \
{Hypothesis: $HYPOTHESIS, Modification: [$TYPE, $ELEMENT_1, $ELEMENT_2]}. \
Here are the requirements:
1. $HYPOTHESIS should be your analysis and reason for choosing a modification
2. $TYPE should be the modification type; one of "exchange", "substitute", "remove", "add"
3. $ELEMENT should be the selected element type to be modified. For "exchange" and "substitute", \
    two $ELEMENT placeholders are needed. For "remove" and "add", one $ELEMENT placeholder is needed.\n
"""



