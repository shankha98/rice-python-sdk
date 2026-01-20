import os
import sys
import fileinput
from grpc_tools import protoc


def replace_in_file(file_path, search_exp, replace_exp):
    with fileinput.FileInput(file_path, inplace=True) as file:
        for line in file:
            print(line.replace(search_exp, replace_exp), end="")


def generate_protos():
    # Define paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    protos_dir = os.path.join(project_root, "protos")
    state_out_dir = os.path.join(project_root, "rice_sdk", "state", "proto")
    storage_out_dir = os.path.join(project_root, "rice_sdk", "storage", "proto")

    # Ensure output directories exist
    os.makedirs(state_out_dir, exist_ok=True)
    os.makedirs(storage_out_dir, exist_ok=True)

    # Generate State protos
    print("Generating State protos...")
    state_proto = os.path.join(protos_dir, "state.proto")
    exit_code = protoc.main(
        (
            "",
            f"-I{protos_dir}",
            f"--python_out={state_out_dir}",
            f"--grpc_python_out={state_out_dir}",
            state_proto,
        )
    )
    if exit_code != 0:
        print(f"Failed to generate state protos. Exit code: {exit_code}")
        sys.exit(exit_code)

    # Fix imports for State
    replace_in_file(
        os.path.join(state_out_dir, "state_pb2_grpc.py"),
        "import state_pb2 as state__pb2",
        "from . import state_pb2 as state__pb2",
    )

    # Generate RiceDB protos
    print("Generating RiceDB protos...")
    ricedb_proto = os.path.join(protos_dir, "ricedb.proto")
    exit_code = protoc.main(
        (
            "",
            f"-I{protos_dir}",
            f"--python_out={storage_out_dir}",
            f"--grpc_python_out={storage_out_dir}",
            ricedb_proto,
        )
    )
    if exit_code != 0:
        print(f"Failed to generate ricedb protos. Exit code: {exit_code}")
        sys.exit(exit_code)

    # Fix imports for RiceDB
    replace_in_file(
        os.path.join(storage_out_dir, "ricedb_pb2_grpc.py"),
        "import ricedb_pb2 as ricedb__pb2",
        "from . import ricedb_pb2 as ricedb__pb2",
    )

    # Create __init__.py files to make them packages
    open(os.path.join(state_out_dir, "__init__.py"), "a").close()
    open(os.path.join(storage_out_dir, "__init__.py"), "a").close()

    print("Proto generation complete.")


if __name__ == "__main__":
    generate_protos()
