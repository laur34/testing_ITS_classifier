import random
import sys

def subsample_fasta(input_fasta, output_fasta, sample_size=100000):
    print("Scanning FASTA file indexing sequences...")
    # Store the byte offsets of each sequence header
    offsets = []
    with open(input_fasta, 'rb') as f:
        offset = f.tell()
        line = f.readline()
        while line:
            if line.startswith(b'>'):
                offsets.append(offset)
            offset = f.tell()
            line = f.readline()
            
    total_seqs = len(offsets)
    print(f"Found {total_seqs} total sequences.")
    
    if sample_size > total_seqs:
        sample_size = total_seqs
        
    print(f"Randomly selecting {sample_size} sequences...")
    sampled_offsets = set(random.sample(offsets, sample_size))
    
    print(f"Writing to {output_fasta}...")
    with open(input_fasta, 'rb') as infile, open(output_fasta, 'wb') as outfile:
        for offset in offsets:
            if offset in sampled_offsets:
                infile.seek(offset)
                # Write header
                outfile.write(infile.readline())
                # Write sequence lines until next header or EOF
                while True:
                    curr_pos = infile.tell()
                    line = infile.readline()
                    if not line or line.startswith(b'>'):
                        break
                    outfile.write(line)

if __name__ == "__main__":
    # Adjust file names as needed
    subsample_fasta("unite_rdp_train.fasta", "test_subsample.fasta", 100000)
    print("Done!")

