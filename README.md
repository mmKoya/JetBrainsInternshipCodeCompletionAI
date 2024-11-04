# JetBrainsInternshipCodeCompletionAI

# Project Goal

The objective of this project is to systematically create and evaluate a dataset for code completion tasks. The approach involves extracting meaningful code segments from Python files and evaluating AI-driven code completion for various parameter combinations.

## Process Overview

### 1. Code Parsing
The initial phase focuses on identifying and extracting complete functions and classes from Python source files, using the Abstract Syntax Tree (AST) library. Source files belong to the current project as well as random scripts from previous projects that are biased toward mathematical concepts and numpy syntax. Extracted code blocks represent fundamental units for analysis. To facilitate this, I developed the script [`CodeParser.py`](CodeParser.py), which:
- Removes comments and blank lines for cleaner analysis.
- Extracts code blocks (functions and classes) for structured dataset creation.

### 2. Dataset Creation
For each code block, specific segments such as function arguments, assignments, and conditions were isolated to represent "missing parts"—the code elements the AI should predict. To allow flexible testing, these code blocks are framed by preceding and following lines, known as prefix and suffix.

Using [`DatasetCreator.py`](DatasetCreator.py), I generated separate datasets for various combinations of:
- **Missing Part Types** (e.g., arguments, assignments, conditions)
- **Missing Part Size** (e.g., number of arguments, number of characters)
- **Context Size** (e.g., 1-5 lines above and below missing part, full context of a function or class)

Each parameter combination results in a unique dataset, enabling systematic analysis across different configurations.

Initially, this process produced over 10,000 examples across many parameter combinations. Due to computational constraints, the project was scaled back. Ultimately, 50 examples were randomly sampled from each of 7 parameter-specific datasets. Additional datasets were sampled with same parameters but the middle part was randomly split as to mimic AI completion after manually writing the beginning of the missing part. In total 700 examples were created. The following are the final datasets I came up with:

| Dataset ID | Code Block Type | Missing Part Type                        | Missing Part Size                                    | Context Size |
|----------------------------------------------|------------------------------------------------|--------------------------|------------|------|
| 1 | Class | Lines | 5 Lines | Full Context |
| 2 | Function | Function Arguments | Any | Full Context |
| 3 | Function | Assignments | Any | Full Context |
| 4 | Function | Assignments | Any | 3 Lines |
| 5 | Function | Conditions | Any | Full Context |
| 6 | Function | Conditions | Any | 3 Lines |
| 7 | Function | Lines | 3 Lines | Full Context |
| 8 | Class | Lines with Random Split | 5 Lines | Full Context |
| 9 | Function | Function Arguments with Random Split | Any | Full Context |
| 10 | Function | Assignments with Random Split | Any | Full Context |
| 11 | Function | Assignments with Random Split | Any | 3 Lines |
| 12 | Function | Conditions with Random Split | Any | Full Context |
| 13 | Function | Conditions with Random Split | Any | 3 Lines |
| 14 | Function | Lines with Random Split | 3 Lines | Full Context |


### 3. Dataset Sampling and Model Selection


While I initially intended to test StarCoder2 15B, resource limitations led me to evaluate five smaller models instead:
- `tiny_starcoder_py`
- `starcoder2-3b`
- `starcoder2-7b`
- `codegemma-2b`
- `codegemma-7b`

These models were compatible with local computational resources.

### 4. Inference and Evaluation
The [`Inference.py`](Inference.py) script prepares the datasets for model inference, saving the generated outputs for evaluation. The results are then evaluated using [`Evaluation.py`](Evaluation.py), which relies on metrics defined in [`Metrics.py`](Metrics.py). The following evaluation metrics are implemented:
- **Exact Match**
- **Character F-score (chrF)**
- **BLEU**
- **ROUGE**
- **METEOR**
- **BERT Score**
- **Syntax Validity** (if applicable)

## Results
The following tables depict metrics achieved by each model.

### tiny_starcoder_py
| Dataset ID | Exact Match |     CHRF     |     BLEU     |     ROUGE    |    METEOR    |     BERT     | Syntax Valid |
|------------|-------------|--------------|--------------|--------------|--------------|--------------|--------------|
|      1     |      0.00   | 0.4796       | 0.1931       | 0.3792       | 0.4281       | 0.3868       |     0.20     |
|      2     |      0.00   | 0.2835       | 0.0600       | 0.1284       | 0.2578       | -0.1509      |     0.26     |
|      3     |      0.02   | 0.2646       | 0.0797       | 0.1748       | 0.2967       | -0.1621      |     0.40     |
|      4     |      0.02   | 0.2322       | 0.0347       | 0.1026       | 0.2052       | -0.1471      |      -       |
|      5     |      0.14   | 0.4177       | 0.1170       | 0.3208       | 0.3742       | 0.0615       |     0.50     |
|      6     |      0.04   | 0.2887       | 0.0374       | 0.1817       | 0.2237       | -0.2276      |      -       |
|      7     |      0.00   | 0.3819       | 0.1022       | 0.2756       | 0.3356       | 0.3048       |     0.28     |
|      8     |      0.00   | 0.4333       | 0.1359       | 0.3137       | 0.3833       | 0.3506       |     0.30     |
|      9     |      0.00   | 0.2219       | 0.0585       | 0.0779       | 0.2201       | -0.2644      |     0.28     |
|     10     |      0.00   | 0.3451       | 0.1106       | 0.1757       | 0.3755       | -0.0647      |     0.36     |
|     11     |      0.00   | 0.3306       | 0.0909       | 0.1613       | 0.3748       | -0.0260      |      -       |
|     12     |      0.10   | 0.3084       | 0.0872       | 0.2549       | 0.3358       | -0.1150      |     0.30     |
|     13     |      0.00   | 0.2165       | 0.0183       | 0.1320       | 0.2285       | -0.2836      |      -       |
|     14     |      0.02   | 0.3933       | 0.1267       | 0.2900       | 0.3824       | 0.3279       |     0.34     |

### starcoder2-3b
| Dataset ID | Exact Match |     CHRF     |     BLEU     |     ROUGE    |    METEOR    |      BERT     | Syntax Valid |
|------------|-------------|--------------|--------------|--------------|--------------|---------------|--------------|
| 1          |     0.14    | 0.6766       | 0.4729       | 0.6218       | 0.6494       | 0.6560        |     0.68     |
| 2          |     0.40    | 0.7166       | 0.3166       | 0.6034       | 0.5859       | 0.5174        |     0.86     |
| 3          |     0.56    | 0.7576       | 0.3534       | 0.6864       | 0.6864       | 0.6754        |     0.92     |
| 4          |     0.28    | 0.5056       | 0.2123       | 0.3708       | 0.4449       | 0.3189        |      N/A     |
| 5          |     0.58    | 0.7952       | 0.3199       | 0.7325       | 0.6578       | 0.7160        |     0.92     |
| 6          |     0.30    | 0.5682       | 0.1781       | 0.4456       | 0.4159       | 0.2927        |      N/A     |
| 7          |     0.14    | 0.5849       | 0.3649       | 0.5557       | 0.5401       | 0.5344        |     0.84     |
| 8          |     0.16    | 0.7077       | 0.5272       | 0.6369       | 0.6747       | 0.6677        |     0.84     |
| 9          |     0.56    | 0.6783       | 0.2502       | 0.6335       | 0.5967       | 0.5174        |     0.78     |
| 10         |     0.44    | 0.7186       | 0.5652       | 0.6396       | 0.7458       | 0.5805        |     0.88     |
| 11         |     0.20    | 0.5981       | 0.3061       | 0.4704       | 0.5548       | 0.4719        |      N/A     |
| 12         |     0.72    | 0.8491       | 0.3310       | 0.8285       | 0.7666       | 0.7814        |     0.88     |
| 13         |     0.32    | 0.5380       | 0.2272       | 0.4966       | 0.4999       | 0.3207        |      N/A     |
| 14         |     0.26    | 0.6682       | 0.4671       | 0.6125       | 0.6396       | 0.6364        |     0.82     |

### starcoder2-7b
| Dataset ID | Exact Match |     CHRF     |     BLEU     |     ROUGE    |    METEOR    |      BERT     | Syntax Valid |
|------------|-------------|--------------|--------------|--------------|--------------|---------------|--------------|
| 1          |     0.22    | 0.6709       | 0.4707       | 0.6122       | 0.6317       | 0.6647        |     0.80     |
| 2          |     0.58    | 0.8151       | 0.3725       | 0.6929       | 0.6691       | 0.7187        |     0.94     |
| 3          |     0.62    | 0.7589       | 0.3676       | 0.7024       | 0.6807       | 0.7045        |     0.96     |
| 4          |     0.32    | 0.5727       | 0.2072       | 0.4323       | 0.4937       | 0.4754        |      N/A     |
| 5          |     0.64    | 0.8248       | 0.3671       | 0.7814       | 0.7102       | 0.7805        |     0.98     |
| 6          |     0.26    | 0.5334       | 0.2050       | 0.3833       | 0.4043       | 0.2635        |      N/A     |
| 7          |     0.16    | 0.6157       | 0.4292       | 0.5754       | 0.5857       | 0.5972        |     0.82     |
| 8          |     0.24    | 0.7622       | 0.5934       | 0.6964       | 0.7339       | 0.7563        |     0.86     |
| 9          |     0.64    | 0.7834       | 0.2570       | 0.7086       | 0.6577       | 0.7082        |     0.88     |
| 10         |     0.46    | 0.7318       | 0.5567       | 0.6229       | 0.7690       | 0.6405        |     0.92     |
| 11         |     0.26    | 0.5975       | 0.3880       | 0.4644       | 0.5907       | 0.4633        |      N/A     |
| 12         |     0.72    | 0.8500       | 0.3346       | 0.8278       | 0.7524       | 0.8120        |     0.94     |
| 13         |     0.42    | 0.6176       | 0.2618       | 0.5728       | 0.5474       | 0.5110        |      N/A     |
| 14         |     0.26    | 0.6915       | 0.4908       | 0.6157       | 0.6700       | 0.6416        |     0.84     |

### codegemma-2b
| Dataset ID | Exact Match |     CHRF     |     BLEU     |     ROUGE    |    METEOR    |      BERT     | Syntax Valid |
|------------|-------------|--------------|--------------|--------------|---------------|----------------|--------------|
|      1     |     0.14    |  0.5467      |  0.3569      |  0.5210      |   0.5204      |   0.5015       |     0.94     |
|      2     |     0.54    |  0.7878      |  0.4147      |  0.6809      |   0.6391      |   0.6834       |     0.98     |
|      3     |     0.54    |  0.7487      |  0.2892      |  0.6566      |   0.6348      |   0.6784       |     1.00     |
|      4     |     0.24    |  0.4812      |  0.1708      |  0.3562      |   0.4167      |   0.2978       |     -        |
|      5     |     0.60    |  0.8072      |  0.3422      |  0.7468      |   0.6902      |   0.7710       |     1.00     |
|      6     |     0.24    |  0.5392      |  0.1567      |  0.4067      |   0.3924      |   0.3594       |     -        |
|      7     |     0.08    |  0.5546      |  0.3638      |  0.5230      |   0.5269      |   0.4035       |     0.90     |
|      8     |     0.14    |  0.5723      |  0.4139      |  0.5262      |   0.5560      |   0.5257       |     0.90     |
|      9     |     0.76    |  0.8360      |  0.3127      |  0.8048      |   0.7031      |   0.8181       |     0.98     |
|     10     |     0.58    |  0.7960      |  0.6366      |  0.7262      |   0.8006      |   0.7417       |     0.98     |
|     11     |     0.26    |  0.5639      |  0.3284      |  0.4472      |   0.5918      |   0.4230       |     -        |
|     12     |     0.76    |  0.8702      |  0.3797      |  0.8647      |   0.7825      |   0.8503       |     0.98     |
|     13     |     0.32    |  0.5222      |  0.1791      |  0.5056      |   0.4671      |   0.3889       |     -        |
|     14     |     0.22    |  0.5938      |  0.3727      |  0.5549      |   0.5804      |   0.5472       |     0.90     |

### codegemma-7b
| Dataset ID | Exact Match |     CHRF     |     BLEU     |     ROUGE    |    METEOR    |     BERT     | Syntax Valid |
|------------|-------------|--------------|--------------|--------------|--------------|--------------|--------------|
|      1     |      0.16   | 0.6413       | 0.4923       | 0.6490       | 0.6191       | 0.6617       |     1.0      |
|      2     |      0.62   | 0.8425       | 0.4630       | 0.7531       | 0.7308       | 0.7493       |     1.0      |
|      3     |      0.56   | 0.7452       | 0.3787       | 0.6543       | 0.6795       | 0.6985       |     1.0      |
|      4     |      0.32   | 0.5835       | 0.1940       | 0.4324       | 0.4867       | 0.4466       |      -       |
|      5     |      0.64   | 0.8564       | 0.3494       | 0.7918       | 0.7059       | 0.8302       |     0.98     |
|      6     |      0.34   | 0.5917       | 0.2245       | 0.4565       | 0.4407       | 0.4237       |      -       |
|      7     |      0.10   | 0.5605       | 0.3695       | 0.5484       | 0.5206       | 0.4789       |     0.96     |
|      8     |      0.18   | 0.7491       | 0.5994       | 0.7111       | 0.7224       | 0.7066       |     0.96     |
|      9     |      0.68   | 0.8148       | 0.2974       | 0.7342       | 0.6819       | 0.7394       |     0.98     |
|     10     |      0.62   | 0.8308       | 0.6568       | 0.7690       | 0.8468       | 0.7933       |     1.0      |
|     11     |      0.30   | 0.6295       | 0.3717       | 0.5019       | 0.6209       | 0.5038       |      -       |
|     12     |      0.82   | 0.9181       | 0.4247       | 0.9020       | 0.8134       | 0.9044       |     1.0      |
|     13     |      0.44   | 0.6286       | 0.3037       | 0.6089       | 0.5583       | 0.5897       |      -       |
|     14     |      0.26   | 0.6830       | 0.4998       | 0.6355       | 0.6765       | 0.6509       |     0.96     |

## Average results per model
The [`AverageEvaluation.py`](AverageEvaluation.py) script
| Model              | Exact Match | CHRF     | BLEU     | ROUGE    | METEOR   | BERT     | Syntax Valid |
|--------------------|-------------|----------|----------|----------|----------|----------|--------------|
| tiny_starcoder_py  | 0.0243      | 0.3284   | 0.0894   | 0.2121   | 0.3158   | -0.0007  | 0.322        |
| starcoder2-3b      | 0.3614      | 0.6688   | 0.3494   | 0.5953   | 0.6042   | 0.5491   | 0.842        |
| starcoder2-7b      | 0.4143      | 0.7018   | 0.3787   | 0.6206   | 0.6355   | 0.6241   | 0.894        |
| codegemma-2b       | 0.3871      | 0.6586   | 0.3370   | 0.5943   | 0.5930   | 0.5707   | 0.956        |
| codegemma-7b       | 0.4314      | 0.7197   | 0.4018   | 0.6534   | 0.6503   | 0.6555   | 0.984        |

## Human Evaluation
A subset of 50 examples was randomly sampled from original 700 and used for human evaluation as well as previous metrics. This was accomplieshed with [`HumanEvaluation.py`](HumanEvaluation.py) script. Human scoring was conducted by randomly shuffling model responses for each input, assigning each response a score from 0 to 10. The scores were then averaged and rescaled by a factor of 0.1.

| Model              | HumanEval   | Exact Match | CHRF     | BLEU     | ROUGE    | METEOR   | BERT     |
|--------------------|-------------|-------------|----------|----------|----------|----------|----------|
| tiny_starcoder_py  | 0.900       | 0.00        | 0.2767   | 0.0596   | 0.1532   | 0.2616   | -0.1121  |
| starcoder2-3b      | 0.532       | 0.34        | 0.6427   | 0.2612   | 0.5458   | 0.5204   | 0.5114   |
| starcoder2-7b      | 0.56        | 0.38        | 0.6524   | 0.2552   | 0.5842   | 0.5313   | 0.5893   |
| codegemma-2b       | 0.498       | 0.36        | 0.6013   | 0.2092   | 0.5597   | 0.4894   | 0.5261   |
| codegemma-7b       | 0.616       | 0.42        | 0.6913   | 0.2907   | 0.6398   | 0.5918   | 0.6698   |

## Steps for reproduction
- First to create datasets you need to put `.py` files you want to use as source in `RandomScripts` directory. Then run [`DatasetCreator.py`](DatasetCreator.py) which will populate `Datasets` directory. Parameters are hardcoded.
- Next running [`Inference.py`](Inference.py) will load each model, generate responses for 50 examples sampled from each dataset and store them in `CodeCompletionInference` directory. Remember to set HF API token. 
- [`Evaluation.py`](Evaluation.py) loads generated responses, evaluates them relative to ground truth and stores the results in `Evaluation` directory.
- [`AverageEvaluation.py`](AverageEvaluation.py) averages results from `Evaluation` directory and saves them in `AverageEvaluation` directory.
- [`HumanEvaluation.py`](HumanEvaluation.py) samples 50 examples in total, uses them for evaluation of every model and prompts user to evaluate each example on scale from 0 to 10 after which results are saved in `HumanEvaluation` directory.

## Limitations
This project does not currently include comprehensive error handling. As a result:
- Errors are not caught or reported to the user, which may lead to unexpected crashes or silent failures.
- The code assumes ideal conditions and may not handle invalid inputs or edge cases.

Caution is advised when trying to reproduce the results. Models can quickly consume large amount of resources and cause freezes or crashes. Make sure to run the code in correct order since later scripts depend on outputs of previous.

## Conclusion

*Note: This evaluation was conducted on a smaller dataset than initially intended, so the reported scores may have a margin of error. Consequently, while the general trends are likely indicative of each model's relative performance, specific metric values could vary with a larger dataset.*

- This project evaluates the performance of several models on code generation tasks using a variety of metrics, including Exact Match, CHRF, BLEU, ROUGE, METEOR, BERTScore, and Syntax Validity. The results highlight clear distinctions in model effectiveness and syntax reliability, offering insights into their suitability for different applications in natural language code generation.

- Among the models tested, `codegemma-7b` achieved the best overall performance, consistently outperforming other models across most metrics, including Exact Match, BLEU, ROUGE, and METEOR. Its Syntax Validity score of 0.984 also indicates high reliability in generating syntactically correct code, making it an excellent choice for tasks requiring accurate and valid outputs.

- Close behind, `starcoder2-7b` exhibited strong performance, especially in CHRF, BLEU, and BERTScore metrics, achieving Syntax Validity of 0.894. This model offers a balance between precision and flexibility, although it falls slightly short of `codegemma-7b` in Exact Match and Syntax Validity.

- `codegemma-2b` and `starcoder2-3b` perform reasonably well but show limitations compared to their 7B counterparts. codegemma-2b, however, stands out in Syntax Validity with a score of 0.956, suggesting it may be suitable for applications where valid syntax is prioritized, despite lower Exact Match and BLEU scores.

- Finally, `tiny_starcoder_py` has the lowest performance across all metrics, indicating limited applicability for tasks where high accuracy, fluency, and syntactic correctness are required.



## Remarks
- Initial goal was extensive evaluation of multiple models on large number of examples. Evaluation on 20-50 examples, in my opinion, would not be informative enough.
- Source code used for code block extraction was heavily biased toward mathematical concepts and formulas, using a lot of numpy syntax. This might be a reason for lower performance than expected.
- Every model was using `float16` precision in order to allow for local execution.
- Larger models would often give correct response but fail to stop the sequence, continuing generation until `max_new_tokens` limit was reached. These results were still scored highly in HumanEval. Comparatively, `tiny_starcoder_py` would often completely miss the expected response and as a result its score on HumanEval was atrocious.
- It is also important to note that HumanEval was heavily biased since models were evaluated sequentially instead of alternatingly. 




This README provides an overview of the project’s objectives, dataset preparation methodology, and evaluation metrics. Please refer to individual scripts for implementation details.
