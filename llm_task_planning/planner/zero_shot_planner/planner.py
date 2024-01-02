import openai
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util as st_utils
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from llm_task_planning.llm.openai_interface import setup_openai

class ZeroShotPlanner:
    def __init__(self, source, planning_lm_id, translation_lm_id, openai_key=None):
        self.source = source
        self.planning_lm_id = planning_lm_id
        self.translation_lm_id = translation_lm_id
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.MAX_STEPS = 20
        self.CUTOFF_THRESHOLD = 0.8
        self.P = 0.5
        self.BETA = 0.3

        setup_openai()

        self.generator = self._init_planning_lm()
        self.translation_lm, self.action_list_embedding, self.example_task_embedding = self._init_translation_lm()

    def _init_planning_lm(self):
        if self.source == 'huggingface':
            tokenizer = AutoTokenizer.from_pretrained(self.planning_lm_id)
            model = AutoModelForCausalLM.from_pretrained(self.planning_lm_id, pad_token_id=tokenizer.eos_token_id).to(self.device)

        def _generate(prompt, sampling_params):
            if self.source == 'openai':
                response = openai.Completion.create(engine=self.planning_lm_id, prompt=prompt, **sampling_params)
                generated_samples = [response['choices'][i]['text'] for i in range(sampling_params['n'])]
                mean_log_probs = [np.mean(response['choices'][i]['logprobs']['token_logprobs']) for i in range(sampling_params['n'])]
            elif self.source == 'huggingface':
                input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)
                prompt_len = input_ids.shape[-1]
                output_dict = model.generate(input_ids, max_length=prompt_len + sampling_params['max_tokens'], **sampling_params)
                generated_samples = tokenizer.batch_decode(output_dict.sequences[:, prompt_len:])
                token_log_probs = torch.stack(output_dict.scores, dim=1).log_softmax(-1)
                token_log_probs = torch.gather(token_log_probs, 2, output_dict.sequences[:, prompt_len:, None]).squeeze(-1).tolist()
                mean_log_probs = [np.mean(token_log_probs[i]) for i in range(len(token_log_probs))]
                generated_samples = [sample[:sample.index('\n')] if '\n' in sample else sample for sample in generated_samples]
            return [sample.strip().lower() for sample in generated_samples], mean_log_probs

        return _generate

    def _init_translation_lm(self):
        translation_lm = SentenceTransformer(self.translation_lm_id).to(self.device)

        with open('available_actions.json', 'r') as f:
            action_list = json.load(f)
        action_list_embedding = translation_lm.encode(action_list, batch_size=512, convert_to_tensor=True, device=self.device)

        with open('available_examples.json', 'r') as f:
            available_examples = json.load(f)
        example_task_list = [example.split('\n')[0] for example in available_examples]
        example_task_embedding = translation_lm.encode(example_task_list, batch_size=512, convert_to_tensor=True, device=self.device)

        return translation_lm, action_list_embedding, example_task_embedding

    def _find_most_similar(self, query_str, corpus_embedding):
        query_embedding = self.translation_lm.encode(query_str, convert_to_tensor=True, device=self.device)
        cos_scores = st_utils.pytorch_cos_sim(query_embedding, corpus_embedding)[0].detach().cpu().numpy()
        most_similar_idx = np.argmax(cos_scores)
        return most_similar_idx, cos_scores[most_similar_idx]

    def solve(self, task):
        example_idx, _ = self._find_most_similar(task, self.example_task_embedding)
        available_examples = json.load(open('available_examples.json', 'r'))
        example = available_examples[example_idx]
        curr_prompt = f'{example}\n\nTask: {task}'

        plan = []
        previous_action = None
        for step in range(1, self.MAX_STEPS + 1):
            sampling_params = {
                "max_tokens": 10,
                "temperature": 0.1,
                "top_p": 0.9,
                "num_return_sequences": 10,
                "repetition_penalty": 1.2,
                'use_cache': True,
                'output_scores': True,
                'return_dict_in_generate': True,
                'do_sample': True,
                'stop': ['\n']
            }

            samples, log_probs = self.generator(curr_prompt + f'\nStep {step}:', sampling_params)
            best_action = None
            best_overall_score = -np.inf

            for sample, log_prob in zip(samples, log_probs):
                most_similar_idx, matching_score = self._find_most_similar(sample, self.action_list_embedding)
                overall_score = matching_score + self.BETA * log_prob
                translated_action = available_examples[most_similar_idx]

                if step > 1 and translated_action == previous_action:
                    overall_score -= 0.5

                if overall_score > best_overall_score:
                    best_overall_score = overall_score
                    best_action = translated_action

            top_samples_ids = np.argsort(log_probs)[-int(self.P * len(samples)):]
            are_zero_length = all([len(samples[i]) == 0 for i in top_samples_ids])
            below_threshold = best_overall_score < self.CUTOFF_THRESHOLD

            if are_zero_length or below_threshold:
                break

            previous_action = best_action
            formatted_action = (best_action[0].upper() + best_action[1:]).replace('_', ' ')
            curr_prompt += f'\nStep {step}: {formatted_action}'
            plan.append(formatted_action)

        return plan

planner = ZeroShotPlanner(source='huggingface', planning_lm_id='gpt2-large', translation_lm_id='stsb-roberta-large', openai_key='your-api-key')
task = 'Make breakfast'
plan = planner.solve(task)
print("\nGenerated Plan:")
for step, action in enumerate(plan, 1):
    print(f"Step {step}: {action}")
