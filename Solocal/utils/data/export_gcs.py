import os
import subprocess
import sys

dest = os.getenv("DEST")
top_file = os.getenv("TOP_FILE")
bucket = os.getenv("BUCKET")
path = os.getenv("PATH")
dest_filename = os.getenv("FILENAME")
dry_run_var = os.getenv("DRY_RUN", "True")
additional_rclone_params = os.getenv("RCLONE_PARAMS", "").split(" ")
dry_run = True

if dry_run_var and dry_run_var.upper() == "FALSE":
    dry_run = False

print(f"Running with DRY_RUN={dry_run}")


def rclone_cmd(command, params, source, dest):
    cmd = ["/usr/local/bin/rclone",
           "--config=/var/secrets/rclone/rclone.conf",
           "--verbose=4"]
    for p in params:
        cmd.append(p)
    cmd.append(command)
    cmd.append(source)
    cmd.append(dest)
    return subprocess.call(cmd)


if __name__ == "__main__":
    params = additional_rclone_params
    if dry_run:
        params.append("--dry-run")
    params = [x for x in params if x and x != ""]
    if dest_filename and dest_filename != "":
        check = rclone_cmd("copyto", params, f"gcs_dest_dcproc:{bucket}/{path}", dest + "/" + dest_filename)
    else:
        check = rclone_cmd("copy", params, f"gcs_dest_dcproc:{bucket}/{path}", dest + "/" + dest_filename)

    if top_file != "None" and top_file != "":
        if check != 0:
            print("Error copying files, not writing TOP file")
            sys.exit(1)
        with open(f"/tmp/{top_file}", "wb") as fd:
            fd.close()
        print("Copying TOP file")
        rclone_cmd("copy", params, f"/tmp/{top_file}", dest)
    else:
        if check != 0:
            print("Error copying files")
            sys.exit(1)
