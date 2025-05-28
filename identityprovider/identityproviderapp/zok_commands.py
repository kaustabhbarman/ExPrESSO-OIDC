import hashlib
import subprocess
import json
import os

def serialize_signature_for_zokrates(self, pk, sig, msg):
    "Writes the input arguments for verifyEddsa in the ZoKrates stdlib to file."
    sig_R, sig_S = sig
    args = [sig_R.x, sig_R.y, sig_S, pk.p.x.n, pk.p.y.n]
    args = " ".join(map(str, args))
    return args

def calculate_hash_file(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()

# Function to execute a Zokrates command
def run_zokrates_command(command_args):
    """
    Executes a Zokrates command inside the 'zokrates' Docker container.
    """
    try:
        # The command to execute in the host's terminal
        # "docker exec" is how you run commands in a running container
        full_command = ["docker", "exec", "zok"] + command_args
        
        print(f"Executing: {' '.join(full_command)}") # For debugging

        result = subprocess.run(
            full_command,
            capture_output=True, # Capture stdout and stderr
            text=True,           # Decode stdout/stderr as text
            check=True           # Raise CalledProcessError for non-zero exit codes
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Zokrates command failed: {e.cmd}")
        print(f"Return Code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise # Re-raise the exception after logging details
    except FileNotFoundError:
        # This means 'docker' command itself was not found on the host running Django
        print("Error: 'docker' command not found. Is Docker installed and in PATH?")
        raise

# Example usage in a Django view or Celery task:
def generate_proof_for_input(input_a, input_b):
    circuit_path_in_zokrates_container = "/home/zokrates/my_circuit.zok"
    output_dir_in_zokrates_container = "/home/zokrates/out" # Where artifacts are saved

    try:
        # 1. Compile (usually done once, or on circuit change)
        # You might skip this if your circuit is pre-compiled
        run_zokrates_command(["zokrates", "compile", "-i", circuit_path_in_zokrates_container])

        # 2. Setup (usually done once, or on circuit change)
        # You might skip this if proving/verification keys are pre-generated
        run_zokrates_command(["zokrates", "setup"])

        # 3. Compute witness
        # Inputs 'input_a' and 'input_b' are passed directly
        run_zokrates_command(["zokrates", "compute-witness", "-a", str(input_a), str(input_b)])

        # 4. Generate proof
        run_zokrates_command(["zokrates", "generate-proof"])

        # 5. (Optional) Verify proof (from Django for confidence)
        # run_zokrates_command(["zokrates", "verify"])
        # You might also read the generated proof.json and pass it to a smart contract for on-chain verification

        print("Zokrates operations completed successfully.")

        # You can now access generated files from 'zokrates_artifacts' volume
        # which maps to `./zokrates_workspace/out` on your host, or directly
        # read from the shared volume if Django also mounts `/home/zokrates/out`

        # Example: Read the generated proof.json
        # proof_file_path_on_host = os.path.join("./zokrates_workspace", "out", "proof.json")
        # with open(proof_file_path_on_host, 'r') as f:
        #     proof_data = json.load(f)
        # return proof_data

    except Exception as e:
        print(f"An error occurred during Zokrates operations: {e}")
        # Handle the error appropriately in your Django app (e.g., return an error response)
        raise