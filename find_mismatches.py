import re

def parse_results(assignment_file):
    print("Analyzing classification discrepancies...")
    mismatches = 0
    
    with open(assignment_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
                
            seq_id = parts[0]
            # Expected format in header: Root;k__...;p__...;g__GenusName;s__...
            # The original header path is often retained in the RDP output ID string
            
            # Extract assigned genus and its confidence score
            # RDP assignments alternate: [Taxon, Rank, Confidence]
            assigned_genus = None
            genus_conf = 0.0
            
            for i in range(1, len(parts) - 2, 3):
                rank = parts[i+1].lower()
                if rank == 'genus':
                    assigned_genus = parts[i]
                    genus_conf = float(parts[i+2])
                    break
            
            # If we matched genus with high confidence, verify against its original tag
            if assigned_genus and genus_conf >= 0.80:
                # Clean up prefixes like g__ if present in the output but missing in header
                clean_assigned = assigned_genus.replace("g__", "").lower()
                
                # Check if the expected genus is in the sequence header string
                # Looking for variations like g__GenusName or just GenusName boundary
                expected_match = re.search(r';g__([^;\s|]+)', seq_id)
                if expected_match:
                    expected_genus = expected_match.group(1).lower()
                    
                    if clean_assigned != expected_genus:
                        print(f"⚠️ SUSPECT RECORD FOUND: {seq_id}")
                        print(f"   -> Expected Genus: {expected_genus}")
                        print(f"   -> Model Predicted: {assigned_genus} (Confidence: {genus_conf:.2f})")
                        print("-" * 50)
                        mismatches += 1
                        
    print(f"Analysis complete. Flagged {mismatches} suspected anomalies.")

if __name__ == "__main__":
    parse_results("subsample_assignments.txt")

