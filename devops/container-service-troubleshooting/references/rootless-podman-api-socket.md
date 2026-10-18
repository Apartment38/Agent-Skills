# Rootless Podman API socket: verified recovery recipe

## Failure signature

An application controller using the Docker Python client fails with an error equivalent to:

`DockerException: Error while fetching server API version: ... PermissionError(13, 'Permission denied')`

Its Compose configuration may already mount the expected rootless API path to `/var/run/docker.sock` and run as root. Do not change users or permissions first.

## What to prove

Check all of these independently:

- the user systemd socket unit is enabled and active;
- the host path advertised by the unit is actually a Unix socket;
- the consumer container's `/var/run/docker.sock` is actually a Unix socket;
- the API responds over that socket from inside the consumer container.

`systemctl --user is-active podman.socket` alone is insufficient. A stale directory can occupy the configured socket pathname while the unit still appears active.

## Tested recovery

1. Inspect the host path with `stat -Lc 'type=%F ...'`.
2. If it is an empty directory, check it is empty and remove it with `rmdir` only.
3. `systemctl --user restart podman.socket`.
4. Ping the host API through its Unix socket; the Podman Docker-compatible endpoint returns HTTP 200 and `OK` for `/_ping`.
5. Force-recreate the consumer: `podman compose up -d --no-deps --force-recreate <worker>`.
6. Inspect the destination again. It must report `type=socket`.
7. Use the controller's installed client library inside the consumer to call its API `version()` and `ping()` methods.

Why force recreation: a normal compose reconciliation may keep a running container when the YAML did not change, leaving its old directory bind mount intact even after the host socket is repaired.

## Scope

This recipe applies to a rootless Podman socket mapped into an application expecting Docker's Unix socket. It does not replace the need to verify the application's service connection configuration or an actual subsequent deployment.
