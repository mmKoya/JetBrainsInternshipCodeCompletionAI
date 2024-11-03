import json
import os
from Metrics import CodeCompletionEvaluator


if __name__ == "__main__":
    input_dir = "CodeCompletionInference"
    evaluation_dir = "Evaluation"

    models = os.listdir(input_dir)
    evaluator = CodeCompletionEvaluator()
    for model in models:
        tasks = os.listdir(os.path.join(input_dir, model))

        evaluation_dict = {}
        for task in tasks:
            with open(os.path.join(input_dir, model, task, 'generated_blocks.json'), 'r') as file:
                generated_blocks = json.load(file)
            with open(os.path.join(input_dir, model, task, 'generated_middles.json'), 'r') as file:
                generated_middles = json.load(file)
            with open(os.path.join(input_dir, model, task, 'true_middles.json'), 'r') as file:
                true_middles = json.load(file)

            if task[-2:] == '-1':
                evaluation = evaluator.evaluate_multi(generated_middles, true_middles, generated_blocks)
            else:
                evaluation = evaluator.evaluate_multi(generated_middles, true_middles)

            evaluation_dict[task] = evaluation

        with open(os.path.join(evaluation_dir, f"{model}.json"), 'w') as file:
            json.dump(evaluation_dict, file, indent=4)
