import re

def parse_results(assignment_file):
    print("Analyzing raw classification discrepancies (ignoring confidence thresholds)...")
    mismatches = 0
    total_parsed = 0
    
    with open(assignment_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
                
            total_parsed += 1
            seq_id = parts[0]
            
            # Find the assigned genus name in the RDP output columns
            assigned_genus = None
            for i in range(1, len(parts) - 2, 3):
                rank = parts[i+1].lower()
                if rank == 'genus':
                    assigned_genus = parts[i]
                    break
            
            if assigned_genus:
                # Clean up any potential formatting prefixes
                clean_assigned = assigned_genus.replace("g__", "").strip().lower()
                
                # Extract the expected genus from your specific header format
                # e.g., ;g__Oidiodendron;
                expected_match = re.search(r';g__([^;\s|]+)', seq_id)
                if expected_match:
                    expected_genus = expected_match.group(1).strip().lower()
                    
                    # Flag ANY difference, regardless of confidence score
                    if clean_assigned != expected_genus:
                        print(f"⚠️ DISCREPANCY DETECTED:")
                        print(f"   -> Sequence ID: {seq_id.split()[0]}")
                        print(f"   -> Label Says:    {expected_genus}")
                        print(f"   -> Model Assigned: {clean_assigned}")
                        print("-" * 50)
                        mismatches += 1
                        
    print(f"Analysis complete. Parsed {total_parsed} rows.")
    print(f"Flagged {mismatches} raw discrepancies.")

if __name__ == "__main__":
    parse_results("subsample_assignments.txt")

