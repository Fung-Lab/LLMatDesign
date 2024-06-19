import os
import copy
import logging
from typing import Tuple, List
from time import time

import ase
import ase.io
from ase import Atoms
from ase.optimize import FIRE
from ase.constraints import ExpCellFilter
from ase.io.trajectory import Trajectory

from matdeeplearn.common.ase_utils import MDLCalculator

logging.basicConfig(level=logging.INFO)

class StructureOptimizer:
    """
    This class provides functionality to optimize the structure of an Atoms object using a specified calculator.
    """
    def __init__(self,
                 calculator,
                 relax_cell: bool = False,
                 ):
        """
        Initialize the StructureOptimizer.

        Parameters:
        - calculator (Calculator): A calculator object for performing energy and force calculations.
        - relax_cell (bool): If True, the cell will be relaxed in addition to positions during the optimization process.
        """
        self.calculator = calculator
        self.relax_cell = relax_cell
        
    def optimize(self, atoms: Atoms, logfile=None, write_traj_name=None) -> Tuple[Atoms, float]:
        """
        This method optimizes the structure of the given Atoms object using the specified calculator.
        If `relax_cell` is True, the cell will be relaxed. Trajectory information can be written to a file.

        Parameters:
        - atoms: An Atoms object representing the structure to be optimized.
        - logfile: File to write optimization log information.
        - write_traj_name: File to write trajectory of the optimization.

        Returns:
        - atoms: The optimized Atoms object.
        - time_per_step: The average time taken per optimization step.
        """
        atoms.calc = self.calculator       
        if self.relax_cell:
            atoms = ExpCellFilter(atoms)

        optimizer = FIRE(atoms, logfile=logfile)
        
        if write_traj_name is not None:
            traj = Trajectory(write_traj_name + '.traj', 'w', atoms)
            optimizer.attach(traj.write, interval=1)

        start_time = time()
        optimizer.run(fmax=0.001, steps=500)
        end_time = time()
        num_steps = optimizer.get_number_of_steps()
        
        if isinstance(atoms, ExpCellFilter):
            atoms = atoms.atoms
        time_per_step = (end_time - start_time) / num_steps if num_steps != 0 else 0
        return atoms, time_per_step
    
    
if __name__ == '__main__':
    
    device = 'cuda:0'
    
    # config for calculator
    calculator_config = './configs/optimize/torchmdnet.yml'
    calculator = MDLCalculator(calculator_config, rank=device)
    
    # You need to turn structures into a list of Atoms objects
    # MDLCalculator has a data_to_atoms_list that can convert a Data object to a list of Atoms objects
    original_atoms: List[Atoms] = [ase.io.read("structures/zmatrix/2.cif")]
    optimized_atoms: List[Atoms] = []
    
    optim = StructureOptimizer(calculator, relax_cell=True)
    start = time()
    times = []

    print(f"Optimizing {len(original_atoms)} structures...")
        
    for idx, atoms in enumerate(original_atoms):
        atoms.set_calculator(calculator)
        to_optim = copy.deepcopy(atoms)
        optimized, time_per_step = optim.optimize(to_optim)
        times.append(time_per_step)
        optimized_atoms.append(optimized)
        if (idx + 1) % 20 == 0:
            logging.info(f"Completed optimizing {idx + 1} structures.")
    end = time()

    print(f"Total time taken: {end - start} seconds")