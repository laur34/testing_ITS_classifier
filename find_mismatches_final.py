import re

def load_expected_taxonomy(fasta_file):
    """Reads the FASTA file and maps sequence IDs to their true expected genus."""
    print(f"Loading true taxonomy from {fasta_file}...")
    expected_genera = {}
    
    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                # Strip the leading '>' and split by tab
                header = line.strip().lstrip('>')
                parts = header.split('\t')
                
                if len(parts) >= 2:
                    seq_id = parts[0].strip()
                    full_lineage = parts[1].strip()
                    
                    # Search for the genus in the full lineage string (e.g., ;g__Oidiodendron;)
                    genus_match = re.search(r';g__([^;\s|]+)', full_lineage)
                    if genus_match:
                        expected_genera[seq_id] = genus_match.group(1).strip().lower()
                        
    print(f"Loaded {len(expected_genera)} sequence metadata mappings.")
    return expected_genera

def cross_reference_results(assignment_file, expected_genera):
    """Compares RDP assignments against the true expected taxonomy map."""
    print(f"Cross-referencing against {assignment_file}...")
    mismatches = 0
    total_parsed = 0
    
    with open(assignment_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
                
            total_parsed += 1
            seq_id = parts[0].strip()
            
            # Find the assigned genus name in the RDP output columns
            assigned_genus = None
            for i in range(1, len(parts) - 2, 3):
                rank = parts[i+1].lower()
                if rank == 'genus':
                    assigned_genus = parts[i]
                    break
            
            if assigned_genus:
                clean_assigned = assigned_genus.replace("g__", "").strip().lower()
                
                # Look up the true genus from our FASTA dictionary
                if seq_id in expected_genera:
                    expected_genus = expected_genera[seq_id]
                    
                    # Flag if the model's assignment differs from the true label
                    if clean_assigned != expected_genus:
                        print(f"⚠️ MISMATCH IDENTIFIED:")
                        print(f"   -> Sequence ID:   {seq_id}")
                        print(f"   -> Database Label: {expected_genus}")
                        print(f"   -> Model Assigned: {clean_assigned}")
                        print("-" * 50)
                        mismatches += 1
                else:
                    # Optional warning if an assignment ID isn't in the current FASTA slice
                    pass
                        
    print(f"Analysis complete. Parsed {total_parsed} assignment rows.")
    print(f"Flagged {mismatches} true discrepancies.")

if __name__ == "__main__":
    # Cross-reference the 100k batch if available, otherwise 20k
    import os
    fasta = "test_subsample.fasta"
    assignments = "subsample_assignments_100k.txt" if os.path.exists("subsample_assignments_100k.txt") else "subsample_assignments.txt"
    
    if os.path.exists(fasta) and os.path.exists(assignments):
        true_map = load_expected_taxonomy(fasta)
        cross_reference_results(assignments, true_map)
    else:
        print("Error: Missing input files. Ensure your subsample fasta and assignments files are present.")

