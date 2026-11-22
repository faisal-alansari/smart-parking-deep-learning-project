# Model C candidates (Step 4)

Measured on the owner's Mac (Apple M4 Max), Python 3.14, local weights at pinned revisions, 4 CPU threads. Parameters are counted from the loaded models. Memory is the growth in the process's peak resident memory on CPU: after loading, and after running the 60 dev commands (on MPS the weights sit in GPU memory, which this does not count). SmolLM2 and FLAN-T5 weights are read lazily from `.safetensors`, so their memory after load looks small: peak memory is the fair comparison. Time is per command on the 60 dev commands after 3 warm-up commands, including the candidate's own steps (mean / 95th percentile); loading is not included. Nothing is fine-tuned.

| candidate | weights | parameters | licence | disk (MB) | memory after load (MB) | peak memory (MB) | CPU ms / p95 | MPS ms / p95 |
|---|---|---|---|---|---|---|---|---|
| smollm2 | HuggingFaceTB/SmolLM2-135M-Instruct | 134.5M (134.5M) | apache-2.0 | 260 | 56 | 370 | 2026 / 2172 | 279 / 401 |
| flan-t5 | google/flan-t5-small | 77.0M (77.0M) | apache-2.0 | 297 | 60 | 322 | 207 / 389 | 250 / 475 |
| gliner-minilm | urchade/gliner_small-v2.1 + microsoft/deberta-v3-small + sentence-transformers/all-MiniLM-L6-v2 | 152.6M + 22.7M (175.4M) | apache-2.0, mit | 672 | 1313 | 1359 | 34 / 37 | 21 / 34 |
| checked | urchade/gliner_small-v2.1 + microsoft/deberta-v3-small + sentence-transformers/all-MiniLM-L6-v2 + HuggingFaceTB/SmolLM2-135M-Instruct | 152.6M + 22.7M + 134.5M (309.9M) | apache-2.0, mit | 932 | 1360 | 1677 | 1005 / 2169 | 152 / 369 |
