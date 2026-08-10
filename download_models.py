#!/usr/bin/env python3
import re

from huggingface_hub import HfApi, hf_hub_download
from llmo.config import LLM_MODELS

def parse_hf_repo(spec):
    if ":" in spec:
        repo_id, quant = spec.rsplit(":", 1)
    else:
        repo_id, quant = spec, "Q4_K_M"

    return repo_id, quant


def find_gguf_files(api, repo_id, quant):
    files = api.list_repo_files(repo_id=repo_id)

    quant_upper = quant.upper()

    matches = [
        filename
        for filename in files
        if filename.lower().endswith(".gguf")
        and quant_upper in filename.upper()
        and "MMPROJ" not in filename.upper()
        and "EAGLE" not in filename.upper()
    ]

    if not matches:
        raise RuntimeError(
            f"No GGUF matching {quant!r} found in {repo_id}"
        )

    # If the repo contains split GGUFs, prefer those over a duplicate
    # merged GGUF.  Example:
    #
    # model-q4_k_m-00001-of-00002.gguf
    # model-q4_k_m-00002-of-00002.gguf
    # model-q4_k_m.gguf
    #
    # We need one representation, not both.
    split_re = re.compile(
        r"-\d{5}-of-\d{5}\.gguf$",
        re.IGNORECASE,
    )

    split_matches = [
        filename for filename in matches
        if split_re.search(filename)
    ]

    if split_matches:
        return sorted(split_matches)

    return matches


def main():
    api = HfApi()

    print(f"Checking/downloading {len(LLM_MODELS)} models...\n")

    for i, model in enumerate(LLM_MODELS, 1):
        repo_id, quant = parse_hf_repo(model["hf_repo"])

        print(
            f"[{i}/{len(LLM_MODELS)}] {model['name']}\n"
            f"    repo:  {repo_id}\n"
            f"    quant: {quant}"
        )

        files = find_gguf_files(api, repo_id, quant)

        for filename in files:
            print(f"    file:  {filename}")

            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
            )

            print(f"    cached: {path}")

        print()

    print("All models are downloaded and present in the Hugging Face cache.")


if __name__ == "__main__":
    main()
