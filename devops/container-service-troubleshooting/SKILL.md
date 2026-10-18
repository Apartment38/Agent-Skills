---
name: container-service-troubleshooting
description: "Use when containerized services fail. Diagnose and repair."
version: 1.0.0
---

# Container Service Troubleshooting

Use this for Podman or Docker Compose stacks where a web service, reverse proxy, controller, or managed child container fails even though one component appears healthy.

## Principles

- Build a tight probe for the reported boundary before changing configuration.
- Treat host port access, container-network access, and public reverse-proxy access as three different paths.
- Read component logs for the exact failing boundary. A healthy application process does not prove its controller can reach the container API.
- Make the smallest repair, then verify from the same process that failed—not merely from the host.

## Investigation sequence

### 1. Establish the path that fails

For HTTP services, probe separately:

1. upstream directly from the host, if intentionally published;
2. upstream from the proxy container using the service DNS name;
3. the hostname through the proxy with an explicit local resolution override;
4. the public hostname, if it should be public.

A proxy `502` accompanied by `lookup <service>: no such host` is a container-network membership or service-name issue, not an application failure. Inspect both containers' network memberships. Connect the proxy to the service's private network rather than exposing the upstream on a public network just to make DNS work.

### 2. Diagnose controllers that deploy child containers

When an application uses the Docker-compatible API to create or manage containers:

- inspect the worker/controller logs for Docker API exceptions;
- inspect the configured bind mount source and destination;
- check that both ends are Unix sockets, not directories or regular files;
- test the API from inside the exact worker/controller using its native client library.

A mount declaration can look correct while the mounted path is wrong at runtime. This happens when a bind-mount source did not exist at container creation and a directory was created in its place.

### 3. Repair a stale rootless Podman API socket mount

Use this only after proving the host API path and the in-container destination should be sockets.

1. Check the expected host API path with `stat`; do not assume an active `podman.socket` unit means the path is a socket.
2. If the expected socket path is an empty stale directory, remove only that empty directory (`rmdir`, never recursive deletion).
3. Restart the user socket unit so it recreates its Unix socket.
4. Verify the host API via a Unix-socket HTTP ping.
5. Force-recreate the consumer container. A normal Compose up may preserve the stale bind mount because the YAML is unchanged.
6. Verify the mounted destination is a socket and run the controller's own Docker-client ping/version call inside the container.

Do not report deployment capability restored until the in-container client succeeds.

## Verification checklist

- Compose configuration validates.
- Relevant service and dependencies are running.
- Proxy resolves and reaches the intended upstream over its container network.
- Any removed host port has no listener, while the proxy hostname still succeeds.
- Controller API socket is a socket at both host and container paths.
- The controller's native client can ping/version the API.
- Logs since the repair contain no recurrence of the original connection, permission, or DNS failure.

## Relocating existing rootless storage

- Inspect `podman info --format '{{json .Store}}'`, the destination contents, and `findmnt -T` before recommending relocation. Never merge the storage tree into an existing project directory.
- Measure with `podman unshare du -sh` when ordinary `du` reports permission errors; mapped rootless UIDs can otherwise hide substantial volume data.
- For existing containers, prefer preserving the original graphroot pathname with a persistent bind mount to a dedicated directory on the destination filesystem. Simply copying storage and changing graphroot can conflict with absolute paths in persisted metadata. `podman system migrate` is not a graphroot relocation command.
- Require downtime authorization before stopping services. Stop API activation and other writers, stop containers gracefully, and unmount their layers before copying. Preserve numeric ownership, hard links, ACLs, and xattrs using `sudo rsync -aHAXS --numeric-ids`.
- Verify the copied tree with a checksum dry run before cutover; retain the old tree for rollback until container and application health is verified. A retained backup does not reclaim source disk space.
- Make the bind mount depend on the backing filesystem at boot, and ensure container startup waits for the bind mount. Do not use `nofail` for required container storage: silently starting on an empty underlying directory is unsafe.

## Safety notes

- A container API socket is privileged control-plane access. Mount it only into the specific controller that needs it; do not place it in reverse proxies or general application containers.
- Do not make a private service public merely to work around a proxy network problem.
- Preserve unrelated Compose changes; infrastructure repositories commonly have concurrent edits.

See `references/rootless-podman-api-socket.md` for a tested rootless Podman diagnosis and recovery recipe.
