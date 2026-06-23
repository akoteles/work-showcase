import os
import subprocess
import sys

source = os.getenv("SOURCE")
top_file = os.getenv("TOP_FILE")
bucket = os.getenv("BUCKET")
path = os.getenv("PATH")
dest_filename = os.getenv("FILENAME")
move = os.getenv("MOVE", "False") == "True"
globs = os.getenv("GLOB").split(',')

def rclone_cmd(command, params, source, dest):
    cmd = ["/usr/local/bin/rclone",
           "--config=/var/secrets/rclone/rclone.conf",
           "--verbose=4"]
    cmd.append(command)
    for p in params:
        cmd.append("--include")
        cmd.append(p)
    cmd.append(source)
    cmd.append(dest)
    return subprocess.call(cmd)

if __name__ == "__main__":
    params = globs
    params = [x for x in params if x and x != ""]
    check = subprocess.run(["/usr/local/bin/rclone",
                            "--config=/var/secrets/rclone/rclone.conf",
                            "ls",
                            f"{source}{top_file}"
                            ], capture_output=True)
    if check.returncode != 0:
        print("No top file present in FTP")
        sys.exit(-1)
    if move:
        if dest_filename and dest_filename != "":
            rclone_action = rclone_cmd("moveto", "", source, f"gcs_dest_dcproc:{bucket}/{path}/{dest_filename}")
        else:
            rclone_action = rclone_cmd("move", params, source, f"gcs_dest_dcproc:{bucket}/{path}")
    else:
        if dest_filename and dest_filename != "":
            rclone_action = rclone_cmd("copyto", "", source, f"gcs_dest_dcproc:{bucket}/{path}/{dest_filename}")
        else:
            rclone_action = rclone_cmd("copy", params, source, f"gcs_dest_dcproc:{bucket}/{path}")
    sys.exit(rclone_action)
