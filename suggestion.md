What this problem statement is really asking for is **not** “build a chatbot for policies.” It is asking you to build an **offline policy analysis engine** that takes an existing organizational policy, compares it against the **CIS/MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024)** and the **NIST CSF 2.0** outcomes, finds what is missing or weak, then produces a better version of the policy plus a prioritized improvement roadmap. NIST CSF 2.0 organizes cybersecurity outcomes into six Functions — Govern, Identify, Protect, Detect, Respond, Recover — and explicitly says those outcomes are **not a checklist of exact actions or wording**; they are outcomes that organizations implement in their own way. The CIS guide is useful because it maps CSF subcategories to concrete policy/template areas, but CIS also says the templates are a **baseline** and may not reflect the most recent applicable NIST revision. ([NIST Publications][1])

So in plain English, your module should answer these questions for every input policy:

1. **What parts of the policy already cover the expected CSF outcomes?**
2. **What is missing, vague, outdated, or not enforceable enough?**
3. **How should the policy text be revised?**
4. **What should the organization do next, in order, to improve?**

That “roadmap” part matters because NIST’s own CSF workflow is basically: describe the current posture, define the target posture, analyze the gaps, then build an action plan. NIST calls these Current and Target Profiles, and recommends gap analysis plus a prioritized action plan such as a POA&M or risk register. ([NIST Publications][1])

The exact thing you need to make is this:

* An input pipeline that accepts a policy file such as PDF, DOCX, or TXT.
* A local reference knowledge base derived from the CIS 2024 guide.
* A gap-analysis engine that maps policy text to relevant CSF subcategories.
* A revision engine that rewrites or augments the policy text.
* A roadmap generator that turns gaps into prioritized actions.
* A local-only runtime: no cloud API, no SaaS call, no online inference. The LLM, embeddings, reference guide, and scoring logic must all run on the same machine. The strict interpretation is that even model files should already be present locally before runtime. That last point is my implementation recommendation based on the offline requirement.

What you are **not** required to do is train a model from scratch. You are being asked to **use** a lightweight local LLM, not invent one. The core engineering problem is orchestration and evaluation, not frontier-model research.

## What the CIS/NIST part means for your build

The CIS guide is especially useful because it already groups CSF outcomes into policy-relevant areas. Its contents include Govern categories like Organizational Context, Risk Management Strategy, Roles and Responsibilities, Policy, Oversight, and Supply Chain Risk Management; Identify categories like Asset Management and Risk Assessment; and Protect categories like Identity and Access, Awareness and Training, Data Security, Platform Security, and Technology Infrastructure Resilience. 

That means your system should not compare a policy against the whole universe blindly. It should first decide which parts of the CSF are relevant to the policy type.

For example, a **Risk Management** policy should heavily map into **GV.RM**, **GV.OV**, and **ID.RA** because the CIS guide explicitly ties those outcomes to Information Security Policy, Information Security Risk Management, and Standard Risk Assessment Policy templates. 

A **Patch Management** policy should strongly map into **ID.RA** and **PR.DS/PR.PS** because the guide explicitly associates Patch Management Standard with threat and vulnerability assessment and with protection of data at rest/in transit, while Platform Security includes software maintenance outcomes. 

An **ISMS-style umbrella policy** should lean strongly on **Govern**, because in CSF 2.0 NIST puts Govern at the center of the wheel and says it informs how the other five Functions are implemented. ([NIST Publications][1])

A **Data Privacy and Security** policy is trickier. NIST explicitly says cybersecurity and privacy are related but independent disciplines, and that privacy risks can arise in ways unrelated to cybersecurity incidents. So you can absolutely benchmark the “security” part using CSF/CIS, but for full privacy rigor you should note that CSF alone is not a complete privacy framework. ([NIST Publications][1])

## The right production-ready architecture

The best design here is **hybrid**, not pure-LLM.

### 1) Document ingestion and normalization

Use local Python parsers to read policy files. PyMuPDF is a solid choice for PDFs and is designed for extraction and manipulation of PDFs; its docs also note that plain-text extraction may not always match natural reading order unless you sort appropriately. For DOCX, `python-docx` supports reading and updating Word files. ([pymupdf.readthedocs.io][2])

### 2) Build a structured offline reference catalog

Do not feed the raw CIS PDF into the model every time and hope for the best. Parse it once into a local JSON catalog like:

* `csf_function`
* `category`
* `subcategory_id`
* `subcategory_text`
* `mapped_policy_templates`
* `keywords`
* `priority`
* `domain_tags`

This matters because NIST says the Core is arranged by Function, Category, and Subcategory, and the outcomes are not literal checklist text. A structured catalog gives you something the model can reason over reliably. ([NIST Publications][1])

### 3) Retrieval layer

For semantic matching, use a local embedding model and a local vector index. Sentence Transformers supports computing embeddings and can load models from a local filepath; FAISS is built for efficient similarity search over dense vectors. A lightweight embedding choice like `all-MiniLM-L6-v2` is practical because its model card states it maps text into a 384-dimensional dense vector space for semantic search and clustering. ([Sentence Transformers][3])

### 4) Local LLM runtime

Use `llama.cpp` through `llama-cpp-python`. `llama.cpp` is explicitly designed for efficient local inference, and `llama-cpp-python` exposes Python bindings plus backend acceleration options. GGUF is the common format for this ecosystem and Hugging Face documents it as a format optimized for inference with GGML/GGUF tooling. ([GitHub][4])

### 5) Model choice

For a lightweight, laptop-friendly default, use something in the **3B to 7B instruct** range. Practical candidates include Qwen2.5-3B-Instruct, Phi-3.5-mini-instruct, or Mistral-7B-Instruct-v0.3. Qwen2.5 includes models from 0.5B to 72B; Phi-3.5-mini is positioned as a lightweight model with 128K context; Mistral-7B-Instruct-v0.3 is the instruct-tuned 7B variant. ([Hugging Face][5])

My recommendation:

* **Low-RAM laptop**: Phi-3.5-mini or Qwen2.5-3B in GGUF
* **Better laptop/workstation**: Mistral-7B-Instruct-v0.3 in GGUF

### 6) Gap engine

This is the heart of the system.

Do it in two stages:

**Stage A: deterministic evidence detection**

* chunk policy text
* retrieve top matching CSF subcategories
* score evidence by lexical overlap + embedding similarity + section heuristics
* mark each subcategory as:

  * Covered
  * Partially Covered
  * Missing
  * Ambiguous

**Stage B: constrained LLM reasoning**
Give the model only:

* the policy section
* the matched CSF subcategory text
* evidence spans
* a strict output schema

Then ask it to explain:

* why coverage exists or not
* what exact gap is present
* what revision language is needed

This architecture is much safer than raw prompt-only analysis because the small local model is being used for **judgment and drafting**, not for inventing the standard.

## What the outputs should look like

Your module should produce at least three outputs.

**1. Gap analysis report**
For each relevant CSF subcategory:

* subcategory ID
* description
* status: covered / partial / missing
* evidence quote from the policy
* reason for the score
* severity
* suggested fix

**2. Revised policy**
This should not just be a summary. It should be a proper revised document with:

* improved scope
* roles and responsibilities
* review frequency
* exceptions process
* enforcement language
* audit/monitoring language
* references to risk and incident handling where relevant

**3. Roadmap**
A prioritized plan such as:

* Immediate
* Near term
* Medium term

This is directly aligned with the CSF profile-and-gap idea from NIST. ([NIST Publications][1])

## What “good” looks like for each dummy policy

For your test data, you should intentionally create weak dummy policies so the system has something to detect.

For **ISMS**, common gaps to test:

* no ownership
* no review cadence
* no risk appetite linkage
* no third-party risk mention
* no oversight metrics

For **Data Privacy and Security**:

* vague data classification
* weak access control language
* no encryption expectations
* no disposal/retention controls
* no breach communication path
  Also add a note in documentation that privacy-specific compliance may exceed what CSF alone covers. ([NIST Publications][1])

For **Patch Management**:

* no asset inventory dependency
* no criticality-based prioritization
* no exception handling
* no rollback/validation
* no reporting metrics
  These map well to ID.RA, PR.DS, and PR.PS themes in the CIS guide. 

For **Risk Management**:

* no scoring method
* no risk register tracking
* no treatment ownership
* no acceptance criteria
* no executive review loop
  These line up with GV.RM, GV.OV, and related Govern outcomes. 

## Non-functional requirements for a real build

To make this production-ready, I would require:

* no network calls at runtime
* model files stored locally
* reference guide stored locally
* deterministic JSON output mode
* audit logging of input file, timestamp, model version, and analysis run
* reproducible prompts
* configurable thresholds
* human-review warning on every revised policy draft

That last one matters because the CIS guide itself says its templates are a baseline and not something to use blindly as legal or compliance advice. 

## Recommended repo shape

A clean repo would look like:

* `ingestion/`
* `reference_builder/`
* `retrieval/`
* `analysis/`
* `revision/`
* `reporting/`
* `models/`
* `tests/`
* `docs/`

And your primary entry point could be something like:

```bash
python main.py \
  --policy ./samples/patch_management.docx \
  --domain patch_management \
  --reference ./reference/cis_nist_policy_guide_2024.json \
  --model ./models/qwen2.5-3b-instruct-q4.gguf \
  --out ./outputs/
```

## The safest final interpretation

So, the exact thing you need to build is:

**An offline Python module that accepts an organizational policy, maps it to relevant NIST CSF 2.0 outcomes using the CIS 2024 policy template guide as the benchmark, identifies missing or weak provisions with evidence, generates a revised policy draft, and outputs a prioritized improvement roadmap — all using only local models and local processing.**

That is the correct reading of the problem statement.

The next step should be turning this into a concrete implementation plan with repo structure, file-by-file modules, and the actual Python starter code.

[1]: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf "The NIST Cybersecurity Framework (CSF) 2.0"
[2]: https://pymupdf.readthedocs.io/?utm_source=chatgpt.com "PyMuPDF documentation"
[3]: https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html?utm_source=chatgpt.com "SentenceTransformer"
[4]: https://github.com/ggml-org/llama.cpp?utm_source=chatgpt.com "ggml-org/llama.cpp: LLM inference in C/C++"
[5]: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct?utm_source=chatgpt.com "Qwen/Qwen2.5-3B-Instruct"
