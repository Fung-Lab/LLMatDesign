query_document_prompt_template = f"""
# Context: 
# <context>

# Question:
# Given the above context, <question>?

# First answer True/False to the question if the answer can be found in the context, followed by the answer if it can be found in the context. 
You should return a Python list of length 2: 
1. the first element should be a boolean indicating whether the answer can be found in the context, 
2. the second element should be a single string containing the answer if it can be found in the context.

Sample output:
[True, "AgNO3"]
[False, ""]
[True, "80 degree celcius"]

""".strip()

query_properties_prompt_template = f"""
# Context: 
# <context>

# Question:
# Given the above context, commplete the following python class with the properties of the <question>:

class MaterialProperties:
    # please fill in the following attributes given the above context. Assign None if the information is not available.
    def __init__(self):
        # formation energy of <composition>
        self.formation_energy = None
        # band gap of <composition>
        self.band_gap = None
        # magnetic moment of <composition>
        self.magnetic_moment = None
        # spacegroup of <composition>
        self.spacegroup = None
        # energy above hull of <composition>
        self.energy_above_hull = None

# Answer to the best of your ability. If certain information is not found in the context, please leave it as None.

# Sample output:
class MaterialProperties:
    def __init__(self):
        # formation energy of AgNO3
        self.formation_energy = "-0.5 ev/atom"
        # band gap of AgNO3
        self.band_gap = "0.97 eV"
        # magnetic moment of AgNO3
        self.magnetic_moment = None
        # spacegroup of AgNO3
        self.spacegroup = "87"
        # energy above hull of AgNO3
        self.energy_above_hull = None
""".strip()

ask_expert_prompt_template = f"""
# You are a materials science agent helping with the discovery of new materials.
# You will be given a starting material to be modified and a target property to achieve.
# Make an informed choice of modification based on the given material, target property, and 
# past modifications and property values obtained after those modifications.
# Output a list of the modification done, and a string of the reason why you think this is a good modification
# to take to achieve the target property.
# Try to avoid repeating past modifications, and make sure the modification is physically meaningful.

# Starting material to be modified
<chemical_formula>

# Target property: <property_type>
<property>

# Past modifications and property values
<past_modifications>

# Availble modifications
# 1. exchange: exchange one atom with another atom
# 2. substitute: substitute one atom with another atom
# 3. add: add an atom to the material
# 4. remove: remove an atom from the material

# Additional constraints:
<additional_context>

# Example outputs:
["exchange", "O", "N"], "Oxygen (O) is a strong oxidizer, replacing it with nitrogen (N) will reduce the oxidation potential of the material"
["substitute", "Ti", "Fe"], "Iron (Fe) has a lower atomic number than Titanium (Ti), which typically corresponds to lower energy states."
["add", "O"], "By adding an oxygen (O) atom, we increase the overall negative charge of the material."
["remove", "O"], "Removing an oxygen (O) atom reduces the total energy of the compound by eliminating one of the repulsive interactions between the oxygen atoms"
"""

ask_expert_formation_energy_prompt_template = f"""
# You are a materials science agent helping with the discovery of new materials.
# You will be given a starting material to be modified. Try to achieve the lowest formation energy possible.
# Make an informed choice of modification based on the given material and 
# past modifications and property values obtained after those modifications.
# Output a list of the modification done, and a string of the reason why you think this is a good modification
# to take to achieve the the lowest formation energy.
# Try to avoid repeating past modifications, and make sure the modification is physically meaningful.

# Starting material to be modified
<chemical_formula>

# Task: modify the material to achieve the lowest formation energy (eV/atom) possible

# Past modifications and property values
<past_modifications>

# Availble modifications
# 1. exchange: exchange one atom with another atom
# 2. substitute: substitute one atom with another atom
# 3. add: add an atom to the material
# 4. remove: remove an atom from the material

# Example outputs:
["exchange", "O", "N"], "some reason here"
["substitute", "Ti", "Fe"], "some reason here"
["add", "O"], "some reason here"
["remove", "O"], "some reason here"
"""