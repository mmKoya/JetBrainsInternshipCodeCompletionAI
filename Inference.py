from huggingface_hub import login
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList
import torch
from tqdm import tqdm
import os
import random
import json


login("YOUR_HUGGINGFACE_API_TOKEN")


def prepare_datasets(datasets, prefix_token, middle_token, suffix_token):
    prepared_datasets = []
    for dataset in datasets:
        name = dataset[0]
        samples = dataset[1]
        input_texts = [f'{prefix_token}{sample[0]}{suffix_token}{sample[2]}{middle_token}' for sample in samples]
        prefixes = [sample[0] for sample in samples]
        middles = [sample[1] for sample in samples]
        suffixes = [sample[2] for sample in samples]
        prepared_datasets.append((name, input_texts, prefixes, middles, suffixes))
    return prepared_datasets


def dataset_inference(input_texts: List[str], tokenizer, model, max_new_tokens=256):
    output_texts = []

    for input_text in tqdm(input_texts, desc="Processing inputs"):
        input_encoding = tokenizer(input_text, return_tensors="pt").to(model.device)
        prompt_len = input_encoding["input_ids"].shape[-1]

        output_encoding = model.generate(**input_encoding, max_new_tokens=max_new_tokens, eos_token_id=terminator_ids, pad_token_id=0)

        output_text = tokenizer.decode(output_encoding[0][prompt_len:], skip_special_tokens=True)
        output_texts.append(output_text)

    return output_texts


if __name__ == '__main__':
    random.seed(42)

    datasets_path = "Datasets"
    dataset_files = [f for f in os.listdir(datasets_path) if f.endswith('.json')]
    dataset_files = sorted(dataset_files)

    datasets = []
    for dataset_file in dataset_files:
        with open(os.path.join(datasets_path, dataset_file), 'r') as file:
            name = dataset_file.split('.')[0]
            dataset = json.load(file)
            dataset_sample = random.sample(dataset, 50)
            datasets.append((name, dataset_sample))

    model_configs = {
        "tiny_starcoder_py": ("bigcode", ["<fim_prefix>", "<fim_middle>", "<fim_suffix>", "<file_sep>"]),
        "starcoder2-3b": ("bigcode", ["<fim_prefix>", "<fim_middle>", "<fim_suffix>", "<file_sep>"]),
        "starcoder2-7b": ("bigcode", ["<fim_prefix>", "<fim_middle>", "<fim_suffix>", "<file_sep>"]),
        "codegemma-2b": ("google", ["<|fim_prefix|>", "<|fim_middle|>", "<|fim_suffix|>", '<|file_separator|>']),
        "codegemma-7b": ("google", ["<|fim_prefix|>", "<|fim_middle|>", "<|fim_suffix|>", '<|file_separator|>'])
    }

    for name, config in model_configs.items():
        prepared_datasets = prepare_datasets(datasets, *(config[1][0:3]))

        outputs_path = f'CodeCompletionInference/{name}'

        terminators = config[1]
        checkpoint = f"{config[0]}/{name}"
        tokenizer = AutoTokenizer.from_pretrained(checkpoint, clean_up_tokenization_spaces=True, additional_special_tokens=terminators)
        model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.float16, device_map="auto")

        terminator_ids = tokenizer.convert_tokens_to_ids(terminators)
        terminator_ids.append(tokenizer.eos_token_id)

        for dataset in prepared_datasets:
            name = dataset[0]

            os.makedirs(os.path.join(outputs_path, name), exist_ok=True)

            input_texts = dataset[1]

            max_new_tokens = 200

            generated_output_texts = dataset_inference(input_texts, tokenizer, model, max_new_tokens)

            with open(os.path.join(outputs_path, name, "true_middles.json"), 'w') as file:
                json.dump(dataset[3], file, indent=4)

            with open(os.path.join(outputs_path, name, "generated_middles.json"), 'w') as file:
                json.dump(generated_output_texts, file, indent=4)

            with open(os.path.join(outputs_path, name, "generated_blocks.json"), 'w') as file:
                json.dump([prefix + middle + suffix for prefix, middle, suffix in zip(dataset[2], generated_output_texts, dataset[4])], file, indent=4)

