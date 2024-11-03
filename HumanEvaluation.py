import json
import os
import random
from Metrics import CodeCompletionEvaluator


input_dir = "CodeCompletionInference"
output_dir = "HumanEvaluation"
models = os.listdir(input_dir)

random.seed(420)
indices = random.sample(range(700), 50)
evaluator = CodeCompletionEvaluator()

for model in models:
    datasets = sorted(os.listdir(os.path.join(input_dir, model)))

    generated_blocks = []
    generated_middles = []
    true_middles = []
    for dataset in datasets:
        with open(os.path.join(input_dir, model, dataset, "generated_blocks.json"), 'r') as file:
            generated_blocks += json.load(file)
        with open(os.path.join(input_dir, model, dataset, "generated_middles.json"), 'r') as file:
            generated_middles += json.load(file)
        with open(os.path.join(input_dir, model, dataset, "true_middles.json"), 'r') as file:
            true_middles += json.load(file)

    sample_generated_blocks = [generated_blocks[index] for index in indices]
    sample_generated_middles = [generated_middles[index] for index in indices]
    sample_true_middles = [true_middles[index] for index in indices]

    evaluation = evaluator.evaluate_multi(sample_generated_middles, sample_true_middles)

    hl_scores = []
    for gen_mid, true_mid in zip(sample_generated_middles, sample_true_middles):
        print("-------------------------------------------------------------------------")
        print(true_mid)
        print("-------------------------------------------------------------------------")
        print(gen_mid)
        hl_scores.append(int(input()))
        print(len(hl_scores), sum(hl_scores) / len(hl_scores))

    evaluation["HumanEval"] = sum(hl_scores) / len(hl_scores)
    with open(os.path.join(output_dir, f"{model}.json"), "w") as file:
        json.dump(evaluation, file, indent=4)



