from typing import List
from collections import defaultdict

import nltk
import sacrebleu
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from bert_score import score as bert_score
from rouge import Rouge
import ast

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)


class CodeCompletionEvaluator:
    def __init__(self):
        self.rouge = Rouge()

    def exact_match(self, generated, expected):
        return int(generated.strip() == expected.strip())

    def bleu_score(self, generated, expected):
        generated_tokens = nltk.word_tokenize(generated)
        expected_tokens = nltk.word_tokenize(expected)
        return sentence_bleu([expected_tokens], generated_tokens)

    def rouge_score(self, generated, expected):
        scores = self.rouge.get_scores(generated, expected)[0]
        return scores['rouge-l']['f']

    def meteor_score(self, generated, expected):
        try:
            generated_tokens = nltk.word_tokenize(generated)
            expected_tokens = nltk.word_tokenize(expected)
            return meteor_score([expected_tokens], generated_tokens)
        except Exception as e:
            print(f"Error calculating METEOR score: {e}")
            return None

    def syntax_validity(self, code):
        try:
            ast.parse(code)
            return 1
        except SyntaxError:
            return 0

    def chrf_score(self, generated, expected):
        try:
            return sacrebleu.sentence_chrf(generated, [expected]).score / 100.0
        except Exception as e:
            print(f"Error calculating chrF score: {e}")
            return None

    def bert_score(self, generated, expected):
        try:
            P, R, F1 = bert_score([generated], [expected], lang='en', rescale_with_baseline=True)
            return F1.item()
        except Exception as e:
            print(f"Error calculating BERTScore: {e}")
            return None

    def evaluate(self, generated, expected, generated_block: str = None):
        results = {}
        results['exact_match'] = self.exact_match(generated, expected)
        results['chrf'] = self.chrf_score(generated, expected)
        results['bleu'] = self.bleu_score(generated, expected)
        results['rouge'] = self.rouge_score(generated, expected)
        results['meteor'] = self.meteor_score(generated, expected)
        results['bert'] = self.bert_score(generated, expected)
        if generated_block:
            results['syntax_valid'] = self.syntax_validity(generated_block)

        return results

    def evaluate_multi(self, generated: List[str], expected: List[str], generated_block: List[str] = None):
        length = len(generated)
        if length != len(expected):
            return None
        if generated_block and length != len(generated_block):
            return None

        total = defaultdict(float)
        counts = defaultdict(int)

        for i in range(length):
            if generated_block:
                for key, value in self.evaluate(generated[i], expected[i], generated_block[i]).items():
                    if value is not None:
                        total[key] += value
                        counts[key] += 1
            else:
                for key, value in self.evaluate(generated[i], expected[i]).items():
                    if value is not None:
                        total[key] += value
                        counts[key] += 1

        averaged = {key: (total[key] / counts[key]) if counts[key] > 0 else None for key in total}
        return averaged


if __name__ == "__main__":
    evaluator = CodeCompletionEvaluator()

    generated_code = ["""
def main(input):
        return input * 2
""", """
def main(input)
        return input * 2
"""]
    expected_code = ["""
def main(input):
        return input * 2
""", """
def main(input):
        return input * 2
"""]

    results = evaluator.evaluate_multi(generated_code, expected_code)
    print(results)
