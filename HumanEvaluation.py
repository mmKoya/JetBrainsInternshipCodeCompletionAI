import json
import os
import random
from Metrics import CodeCompletionEvaluator


input_dir = "CodeCompletionInference"
output_dir = "HumanEvaluation"
models = os.listdir(input_dir)

N = 50
random.seed(420)
indices = random.sample(range(700), N)
evaluator = CodeCompletionEvaluator()

samples = []
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
    samples.append((sample_generated_blocks, sample_generated_middles, sample_true_middles, evaluation))

print(samples)

hl_scores = [[] for _ in range(len(models))]
for i in range(N):
    print(i)
    orders = random.sample(range(len(models)), len(models))

    for order in orders:
        gen_mid, true_mid = samples[order][1][i], samples[order][2][i]

        print("-------------------------------------------------------------------------")
        print(true_mid)
        print("-------------------------------------------------------------------------")
        print(gen_mid)

        while True:
            user_input = input()
            try:
                user_input = int(user_input)
                break
            except ValueError:
                pass

        hl_scores[order].append(user_input)

for i in range(len(models)):
    evaluation = samples[i][3]
    evaluation["HumanEval"] = sum(hl_scores[i])/N

    output_dict = {
        "scores": evaluation,
        "examples": [{"generated_block": samples[i][0][index][0],
                      "generated_middle": samples[i][1][index],
                      "true_middle": samples[i][2][index],
                      "score": hl_scores[i][index]} for index in range(N)],
    }

    with open(os.path.join(output_dir, f"{models[i]}.json"), "w") as file:
        json.dump(output_dict, file, indent=4)



