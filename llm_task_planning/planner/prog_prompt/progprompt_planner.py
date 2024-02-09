# SPDX-FileCopyrightText: Copyright (c) 2022-2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.


"""
This script evaluates plan generation using openAI LLMs
for the VirtualHome environment tasks
"""

import sys

sys.path.append("virtualhome/simulation")
sys.path.append("virtualhome/demo")
sys.path.append("virtualhome")

import argparse
import os
import os.path as osp
import random
from datetime import datetime
from llm_task_planning.llm import openai_interface

# from virtualhome.demo.utils_demo import *
from llm_task_planning.llm.openai_interface import setup_openai

import openai
import json
import time
from llm_task_planning.planner.prog_prompt.utils_execute import *
from llm_task_planning.problem.utils import parse_instantiated_predicate

def translate_plan_to_actions(plan):
    """
    Translate the plan into a list of individual actions with arguments.

    Args:
    plan -- A list containing the plan as a string.

    Returns:
    A list of action strings in the format '<action> <arg1> <arg2 (if present)>'.
    """

    # Join the plan into a single string (if it's split across multiple list elements)
    plan_str = ' '.join(plan)

    # Regular expression to find all action commands
    action_pattern = re.compile(r"\b(\w+)\('([^']+)'\s*(?:,\s*'([^']+)'|)\)")

    # Find all matches
    actions = action_pattern.findall(plan_str)

    # Format the actions into the desired string format
    formatted_actions = [f"{action} {arg1} {arg2}".strip() for action, arg1, arg2 in actions]

    return formatted_actions


class ProgPromptPlanner:
    def __init__(self, sim, progprompt_path="/home/liam/dev/llm_task_planning/llm_task_planning/planner/prog_prompt", examples="default", num_retries=50):
        self.sim = sim
        self.tasks = {}
        self.actions_taken = []
        self.all_prompts = []
        self.all_llm_responses = []
        self.completed_goals = []
        self.goal = []
        self.all_failures = []
        self.progprompt_path = progprompt_path
        self.examples = examples
        self.abstract_planning_time = 0
        self.sim_planning_time = 0
        self.execution_time = 0
        self.num_retries = num_retries
        self.default_args = self.get_default_args()
        openai_interface.setup_openai()
        self.goal_objects = []

    def reset_data(self):
        self.last_failure = ""
        self.all_failures = []
        self.all_prompts = []
        self.all_llm_responses = []
        self.actions_taken = []
        self.goal = []
        self.abstract_planning_time = 0
        self.sim_planning_time = 0
        self.execution_time = 0
        self.nl_goal = ""
        self.tasks = {}
        self.goal_objects = []

    def solve(self, args=None):
        if args is None:
            args = self.default_args
        for _ in range(self.num_retries):
            success = True
            sim_action_list = self.translate_actions_for_sim(self.generate_plan(args))
            for action in sim_action_list:
                sub_suc, msg = self.sim.execute_actions([action], state=self.sim.get_state())
                self.all_failures.append("" if sub_suc else msg)
                print(msg)
            for task in self.tasks:
                for pred in self.tasks[task]:
                    s, _ = self.sim.check_satisfied(None, pred)
                    success = success and s
            if success:
                return True, 0
        return False, 0

    def translate_actions_for_sim(self, actions):
        state = self.sim.get_state()

        for i in range(len(actions)):
            action, params = parse_instantiated_predicate(actions[i])

            new_action = f"{action}"
            if action == 'walk':
                new_action = f"walk_to_object"
                if any(param in state['room_names'] for param in params):
                    new_action = f"walk_to_room"
            for param in params:
                new_param = param
                if len(param.split('|')) == 1:
                    if param in self.goal_objects:
                        for obj in self.goal_objects:
                            if param in obj.lower():
                                new_param = obj
                    else:
                        for obj in self.sim.get_graph()['objects']:
                            if param in obj['objectId'].lower():
                                new_param = obj['objectId']
                new_action+=f" {new_param}"
            actions[i] = new_action
        print(actions)
        return actions

    def generate_plan(self, args):
        comm = self.sim.comm

        _, env_graph = comm.environment_graph()
        obj = list(set([node['class_name'] for node in env_graph["nodes"]]))

        # define available actions and append avaailable objects from the env
        prompt = f"from actions import turnright, turnleft, walk <obj>, grab <obj>, switchon <obj>, switchoff <obj>, open <obj>, close <obj>, slice <obj>, cut <obj>, putin <obj> <obj>, put <obj> <obj>"
        prompt += f"\n\nobjects = {obj}"

        # load train split for task examples
        with open(f"{self.progprompt_path}/data/pythonic_plans/train_complete_plan_set.json", 'r') as f:
            tmp = json.load(f)
            prompt_egs = {}
            for k, v in tmp.items():
                prompt_egs[k] = v
        # print("Loaded %d task example" % len(prompt_egs.keys()))

        ## define the prompt example task setting ##

        # default examples from the paper
        if args.prompt_task_examples == "default":
            default_examples = ["put_the_wine_glass_in_the_kitchen_cabinet",
                                "throw_away_the_lime",
                                "wash_mug",
                                "refrigerate_the_salmon",
                                "bring_me_some_fruit",
                                "wash_clothes",
                                "put_apple_in_fridge"]
            for i in range(args.prompt_num_examples):
                prompt += "\n\n" + prompt_egs[default_examples[i]]

        # random egs - change seeds
        if args.prompt_task_examples == "random":
            random.seed(args.seed)
            prompt_egs_keys = random.sample(list(prompt_egs.keys()), args.prompt_num_examples)

            for eg in prompt_egs_keys:
                prompt += "\n\n" + prompt_egs[eg]
        gen_plan = []
        for task in self.tasks:
            print(f"Generating plan for: {task}\n")
            prompt_task = "def {fxn}():".format(fxn='_'.join(task.split(' ')))
            curr_prompt = f"{prompt}\n\n{prompt_task}\n\t"
            self.all_prompts.append(curr_prompt)
            _, text = LM(curr_prompt,
                         args.gpt_version,
                         max_tokens=600,
                         stop=["def"],
                         frequency_penalty=0.15)
            self.all_llm_responses.append(text)
            gen_plan.append(text)

            # because codex has query limit per min
            if args.gpt_version == 'code-davinci-002':
                time.sleep(90)
            # setup logging
        return translate_plan_to_actions(gen_plan)

    def set_goal(self, predicates, task):
        self.tasks[task] = predicates
        goal_objects = []
        for goal in self.tasks.values():
            for pred in goal:
                rel, params = parse_instantiated_predicate(pred)
                for param in params:
                    if "character" in param:
                        continue
                    else:
                        self.goal_objects.append(param)

    def execute_plan(self, plan):
        pass

    def get_default_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--progprompt-path", type=str,
                            default="/home/liam/dev/llm_task_planning/llm_task_planning/planner/prog_prompt")
        parser.add_argument("--expt-name", type=str, default=datetime.now().strftime("%Y%m%d_%H%M%S"))

        parser.add_argument("--gpt-version", type=str, default="gpt-3.5-turbo-1106",
                            choices=['text-davinci-002', 'davinci', 'code-davinci-002', "gpt-3.5-turbo-1106"])
        parser.add_argument("--env-id", type=int, default=0)
        parser.add_argument("--test-set", type=str, default="test_unseen",
                            choices=['test_unseen', 'test_seen', 'test_unseen_ambiguous', 'env1', 'env2'])

        parser.add_argument("--prompt-task-examples", type=str, default="default",
                            choices=['default', 'random'])
        # for random task examples, choose seed
        parser.add_argument("--seed", type=int, default=0)

        ## NOTE: davinci or older GPT3 versions have a lower token length limit
        ## check token length limit for models to set prompt size:
        ## https://platform.openai.com/docs/models
        parser.add_argument("--prompt-num-examples", type=int, default=7,
                            choices=range(1, 7))
        parser.add_argument("--prompt-task-examples-ablation", type=str, default="none",
                            choices=['none', 'no_comments', "no_feedback", "no_comments_feedback"])

        parser.add_argument("--load-generated-plans", type=bool, default=False)

        args = parser.parse_args()
        return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--progprompt-path", type=str,
                        default="/home/liam/dev/llm_task_planning/llm_task_planning/planner/prog_prompt")
    parser.add_argument("--expt-name", type=str, default=datetime.now().strftime("%Y%m%d_%H%M%S"))

    parser.add_argument("--gpt-version", type=str, default="gpt-3.5-turbo-1106",
                        choices=['text-davinci-002', 'davinci', 'code-davinci-002', "gpt-3.5-turbo-1106"])
    parser.add_argument("--env-id", type=int, default=0)
    parser.add_argument("--test-set", type=str, default="test_unseen",
                        choices=['test_unseen', 'test_seen', 'test_unseen_ambiguous', 'env1', 'env2'])

    parser.add_argument("--prompt-task-examples", type=str, default="default",
                        choices=['default', 'random'])
    # for random task examples, choose seed
    parser.add_argument("--seed", type=int, default=0)

    ## NOTE: davinci or older GPT3 versions have a lower token length limit
    ## check token length limit for models to set prompt size:
    ## https://platform.openai.com/docs/models
    parser.add_argument("--prompt-num-examples", type=int, default=3,
                        choices=range(1, 7))
    parser.add_argument("--prompt-task-examples-ablation", type=str, default="none",
                        choices=['none', 'no_comments', "no_feedback", "no_comments_feedback"])

    parser.add_argument("--load-generated-plans", type=bool, default=False)

    args = parser.parse_args()
    setup_openai()

    if not osp.isdir(f"{args.progprompt_path}/results/"):
        os.makedirs(f"{args.progprompt_path}/results/")
