import json
import os
from collections import defaultdict


if __name__ == "__main__":
    input_dir = "Evaluation"
    evaluation_dir = "AverageEvaluation"

    models = os.listdir(input_dir)
    for model in models:

        with open(os.path.join(input_dir, model), "r") as file:
            results = json.load(file)
            total = defaultdict(float)
            counts = defaultdict(int)

            for result in results.values():
                for key, value in result.items():
                    if value is not None:
                        total[key] += value
                        counts[key] += 1

            averaged = {key: (total[key] / counts[key]) if counts[key] > 0 else None for key in total}

        with open(os.path.join(evaluation_dir, model), "w") as file:
            json.dump(averaged, file, indent=4)

