---
name: linux-stale-drive-mounts
description: "Use when Linux drive mounts return I/O errors."
---

# Recover disconnected filesystem mounts

1. Distinguish EIO from EACCES using findmnt, stat, getfacl, kernel logs, and UUID resolution. A filesystem can show rw after XFS or ext4 has shut down. Never start with chmod/chown.
2. Compare the mounted device with the current UUID symlink and udev properties. USB reconnection can change device names while old mounts remain attached to removed devices. Check sibling drives sharing the enclosure.
3. Obtain recovery authorization. If sudo authentication is unavailable, installed pkexec with a desktop PolicyKit agent can prompt securely. Never accept credentials in chat; if no agent works, ask the user to run commands in their terminal.
4. Scan /proc as root for affected cwd/root symlinks, descriptors, mappings, and fdinfo mount IDs. Count permission-denied checks: an empty unprivileged scan does not prove a mount is unused.
5. If normal umount reports busy without process references, inspect exportfs -v. Kernel NFS exports can pin mounts even if nfs-server.service is inactive.
6. Capture export settings before withdrawing only the affected export with exportfs -u 'CLIENT:PATH'. Avoid withdrawing unrelated shares. A release-state warning can coexist with successful withdrawal; verify state and the unmount result.
7. Use normal umount followed by mount through UUID-based fstab, proceeding only on success. Do not force/lazy-unmount or repair as a first response. Verify the new device, kernel recovery logs, directory access, and ownership before restoring the share. Never export an empty underlying mountpoint after a failed remount.
8. Restore the specific export with captured options and read back exportfs -v. Leave permanent configuration and unrelated exports unchanged.
9. Verify user access with a unique temporary file: create, write, fsync, read-back, unlink. Clean up failures and never overwrite user files.
10. Read SMART where available, noting USB passthrough limitations. Recovery is not proof of file integrity or a completed surface test. Recommend backups and enclosure power/cable checks after shared disconnects.
