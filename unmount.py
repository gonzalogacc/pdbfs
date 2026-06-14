import tomllib
import subprocess
import os

def unmount_all(config_path="config.toml"):
    if not os.path.exists(config_path):
        print(f"Config file {config_path} not found.")
        return

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    for db in config.get("databases", []):
        mount_point = db.get("mount_point")
        if mount_point:
            print(f"Unmounting {mount_point}...")
            # Use fusermount -u for Linux, or umount for general compatibility
            # We'll stick to fusermount -u as it's standard for FUSE
            try:
                subprocess.run(["fusermount", "-u", mount_point], check=True, capture_output=True)
                print(f"Successfully unmounted {mount_point}.")
            except subprocess.CalledProcessError as e:
                # Often happens if it's already unmounted
                stderr = e.stderr.decode().strip()
                if "not mounted" in stderr or "invalid argument" in stderr:
                    print(f"{mount_point} was not mounted.")
                else:
                    print(f"Failed to unmount {mount_point}: {stderr}")

if __name__ == "__main__":
    unmount_all()
