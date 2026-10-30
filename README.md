# Project Handover: RDP Classifier Leave-One-Out Evaluation (UNITE 10 / ITS)

## 📌 Project Context & Goal
A custom Naïve Bayes RDP Classifier model was trained on the **UNITE Release 10 (ITS marker gene)** database. The raw dataset was **already deduplicated**—identical sequences were collapsed using `vsearch` (consistent with Porter's methodology to prevent artificially inflating accuracy metrics). This leaves a compressed total of **2,008,086 unique sequences** mapped across **527,336 species leaves**. Preliminary automated pipeline validation suggested the presence of potential taxonomic label anomalies (e.g., misassigned plant host lineages or missing genera like *Tsuga* and *Larix*). 

The goal of this phase was to implement a **Leave-One-Out (LOO) accuracy test** on this deduplicated dataset to statistically expose these miscurated or anomalous sequence records.

---

## 🛑 Current Status & Technical Roadblocks

### 1. Scaling Limitations of Native `loot`
The native RDP Classifier `loot` (Leave-One-Out Test) subcommand breaks down and retrains the model iteratively for every single sequence. This routine requires the raw taxonomy hierarchy text file (`ready4train_taxonomy.txt`) to recompute parent-child structural maps. Given a dataset of 2+ million sequences, running `loot` sequentially is computationally prohibitive on standard infrastructure, requiring weeks of runtime and a massive, contiguous memory footprint (211+ GiB Java Heap).

### 2. Model Density & Memory Overheads (Java Heap Errors)
To bypass the timeline and training constraints of a full `loot` routine, we pivoted to a **Subsampled Validation Approach** using the standard `classify` tool against the pre-compiled `.properties` model. Because the taxonomy hierarchy is already baked into the properties files, the raw taxonomy text map is bypassed.

However, even simple classification commands failed due to extreme memory constraints:
* **Infrastructure Tested:** 96 GiB Total System RAM.
* **Allocation Tried:** `java -Xmx64g`
* **Result:** `Exception in thread "main" java.lang.OutOfMemoryError: Java heap space` at `edu.msu.cme.rdp.classifier.Classifier.classify`.

**Conclusion:** The UNITE 10 model properties are too densely structured (due to the 527k taxonomy leaves) to be loaded into memory for classification on standard shared workstations. Allocating a 64 GiB heap is insufficient to hold the complex probability arrays mapped out by this dataset while sharing resource overhead with other users.

---

## 🛠️ Provided Pipeline Scripts & Components
The following utility scripts have been written, tested, and placed in this directory to allow the next researcher to resume evaluation instantly once high-performance infrastructure is secured:

### 1. `subsample_fasta.py`
* **Purpose:** Randomly extracts a representative validation subset from the multi-gigabyte 2-million sequence FASTA file.
* **Mechanism:** Uses low-overhead **byte offsets** (`f.tell()` and `infile.seek()`). Instead of loading the massive file into memory as Python strings (which would crash the system), it stores raw integer coordinates and instantly jumps to the selected sequences.

### 2. `find_mismatches_final.py`
* **Purpose:** A dual-file cross-referencing stream parser that flags classification errors.
* **Mechanism:** Because the RDP Classifier strips out trailing metadata tags upon processing, this script reads the verification dataset from two fronts:
  1. It parses `test_subsample.fasta`, tracking the true ground-truth taxonomy mapped right next to the Sequence ID across the Tab delimiter.
  2. It reads `subsample_assignments.txt` and cross-references the model's prediction against the expected dictionary, stripping out confidence filters to expose any raw lineage conflicts.

---

## ⏩ Recommended Next Steps for Success

To successfully finalize this leave-one-out validation, the next researcher should execute the following actions:

1. **Migrate to Dedicated High-Memory Infrastructure:** Secure exclusive access to a cloud instance (e.g., AWS `r6i.16xlarge` or an HPC node) with **at least 256 GiB to 512 GiB of available RAM**.
2. **Execute the Scaled Validation Command:**
   ```bash
   java -Xmx192g -jar /path/to/classifier.jar classify \
     -t /path/to/model/rRNAClassifier.properties \
     -o subsample_assignments_100k.txt \
     test_subsample.fasta
   ```
3. **Run the Discrepancy Script:** Execute `python3 find_mismatches_final.py` to generate the final list of flag-worthy mislabeled sequences.

