import tomllib
import subprocess
import os
import sys
import time
import db

def launch_mounts(config_path="config.toml"):
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found.")
        sys.exit(1)

    databases = config.get("databases", [])
    if not databases:
        print("No databases found in config.")
        return

    processes = []

    for entry in databases:
        name = entry.get("name", "unknown")
        mount_point = entry.get("mount_point")
        
        if not mount_point:
            print(f"Skipping {name}: No mount_point specified.")
            continue

        # Prepare arguments for this specific connection
        db_args = [
            "--db-user", str(entry.get("user", "")),
            "--db-pass", str(entry.get("password", "")),
            "--db-host", str(entry.get("host", "localhost")),
            "--db-port", str(entry.get("port", "5432")),
            "--db-name", str(entry.get("db_name", ""))
        ]

        # Create mount point if it doesn't exist
        if not os.path.exists(mount_point):
            os.makedirs(mount_point)

        print(f"Testing connection for '{name}'...")
        
        # Test connection by passing args to a subprocess that calls db.setup
        test_script = f"import db; db.setup('{entry.get('user')}', '{entry.get('password')}', '{entry.get('host')}', '{entry.get('port')}', '{entry.get('db_name')}'); sys.exit(0 if db.test_connection() else 1)"
        test_cmd = ["uv", "run", "python", "-c", f"import sys; {test_script}"]
        
        try:
            subprocess.run(test_cmd, check=True, capture_output=True)
            print(f"Connection successful for '{name}'.")
        except subprocess.CalledProcessError:
            print(f"Connection failed for '{name}'. Skipping mount.")
            continue

        print(f"Mounting '{name}' to '{mount_point}'...")
        # Start main.py with the mount point and DB args using uv run
        proc = subprocess.Popen(
            ["uv", "run", "main.py", mount_point] + db_args
        )
        processes.append((name, proc))
        # Give it a second to initialize
        time.sleep(1)

    if not processes:
        print("No mounts started.")
        return

    print("\nAll successful mounts are running in the background.")
    print("Processes:")
    for name, proc in processes:
        print(f" - {name} (PID: {proc.pid})")
    
    print("\nTo unmount all, you can run 'make unmount'")

if __name__ == "__main__":
    launch_mounts()
