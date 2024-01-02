import time
import numpy as np

from llm_task_planning.planner.contingent_ff.contingent_ff import ContingentFF
from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables

sim = VirtualHomeSimEnv(0)

planner = ContingentFF("salmon_to_fridge.pddl", sim, ["kitchen"])
planner.solve()