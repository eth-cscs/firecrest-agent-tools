from typing import List, Optional, Dict, Any
from fastmcp import FastMCP
from config import settings
import firecrest as fc
import argparse
import datetime
import logging


mcp = FastMCP("firecrest-mcp")

auth = fc.ClientCredentialsAuth(
    client_id=settings.oauth_client_id,
    client_secret=settings.oauth_client_secret,
    token_uri=settings.oauth_token_url,
)

# Every HTTP request the client sends to FirecREST (retries included) is
# counted and recorded in ``client.request_stats`` (pyfirecrest newer than
# 3.10.0, see https://github.com/eth-cscs/pyfirecrest/pull/223). Older
# versions of pyfirecrest have no such attribute: the server still works, but
# the statistics tools report that nothing is being recorded.
if hasattr(fc.v2, "RequestStats"):
    request_stats = fc.v2.RequestStats(
        max_records=settings.request_stats_max_records or None
    )
    client_kwargs = {"request_stats": request_stats}
else:
    request_stats = None
    client_kwargs = {}

client = fc.v2.AsyncFirecrest(
    firecrest_url=settings.backend_api_base_url,
    authorization=auth,
    **client_kwargs,
)

if request_stats is None:
    logging.warning(
        "The installed pyfirecrest does not record request statistics; "
        "upgrade it to enable the get_request_stats tool"
    )
else:
    request_stats.listeners.append(
        lambda r: logging.info(
            f"FirecREST request: {r.method} {r.endpoint} -> "
            f"{r.status_code if r.status_code is not None else r.error} "
            f"({r.duration:.3f}s, attempt {r.attempt})"
        )
    )


# ---------------------------------------------------------------------------
# System information
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_server_version() -> Optional[str]:
    """Get the FirecREST server version.

    Returns:
        Server version string, or None if unavailable.
    """
    logging.info("Invoking get_server_version tool")
    return await client.server_version()


@mcp.tool()
async def get_systems() -> List[Dict[str, Any]]:
    """Fetch the list of available HPC systems.

    Returns:
        List of system information dicts, each containing system name and other metadata.
    """
    logging.info("Invoking get_systems tool")
    system_status = await client.systems()
    return system_status


@mcp.tool()
async def get_nodes(system_name: str) -> List[Dict[str, Any]]:
    """Get the list of nodes on an HPC system.

    Args:
        system_name: Target HPC system name.

    Returns:
        List of node info dicts.
    """
    logging.info(f"Fetching nodes for {system_name}")
    return await client.nodes(system_name=system_name)


@mcp.tool()
async def get_partitions(system_name: str) -> List[Dict[str, Any]]:
    """Get the list of partitions on an HPC system.

    Args:
        system_name: Target HPC system name.

    Returns:
        List of partition info dicts.
    """
    logging.info(f"Fetching partitions for {system_name}")
    return await client.partitions(system_name=system_name)


@mcp.tool()
async def get_reservations(system_name: str) -> List[Dict[str, Any]]:
    """Get the list of reservations on an HPC system.

    Args:
        system_name: Target HPC system name.

    Returns:
        List of reservation info dicts.
    """
    logging.info(f"Fetching reservations for {system_name}")
    return await client.reservations(system_name=system_name)


@mcp.tool()
async def get_userinfo(system_name: str) -> Dict[str, Any]:
    """Get information about the current user on an HPC system.

    Args:
        system_name: Target HPC system name.

    Returns:
        Dict with user info (uid, gid, groups, etc.).
    """
    logging.info(f"Fetching userinfo for {system_name}")
    return await client.userinfo(system_name=system_name)


# ---------------------------------------------------------------------------
# File information
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_files(
    system_name: str,
    path: str,
    show_hidden: bool = False,
    recursive: bool = False,
    numeric_uid: bool = False,
    dereference: bool = False,
) -> List[Dict[str, Any]]:
    """List files and directories at a path on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to list.
        show_hidden: Include hidden files (dotfiles).
        recursive: List recursively.
        numeric_uid: Show numeric UID/GID instead of names.
        dereference: Dereference symbolic links.

    Returns:
        List of file/directory info dicts.
    """
    logging.info(f"Listing files at {system_name}:{path}")
    return await client.list_files(
        system_name=system_name,
        path=path,
        show_hidden=show_hidden,
        recursive=recursive,
        numeric_uid=numeric_uid,
        dereference=dereference,
    )


@mcp.tool()
async def head_file(
    system_name: str,
    path: str,
    num_bytes: Optional[int] = None,
    num_lines: Optional[int] = None,
    exclude_trailing: bool = False,
) -> Dict[str, Any]:
    """Read the beginning of a file on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to the file.
        num_bytes: Number of bytes to read (mutually exclusive with num_lines).
        num_lines: Number of lines to read (mutually exclusive with num_bytes).
        exclude_trailing: Exclude the last num_lines lines instead of showing first.

    Returns:
        Dict with file content.
    """
    logging.info(f"Head of {system_name}:{path}")
    return await client.head(
        system_name=system_name,
        path=path,
        num_bytes=num_bytes,
        num_lines=num_lines,
        exclude_trailing=exclude_trailing,
    )


@mcp.tool()
async def tail_file(
    system_name: str,
    path: str,
    num_bytes: Optional[int] = None,
    num_lines: Optional[int] = None,
    exclude_beginning: bool = False,
) -> Dict[str, Any]:
    """Read the end of a file on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to the file.
        num_bytes: Number of bytes to read (mutually exclusive with num_lines).
        num_lines: Number of lines to read (mutually exclusive with num_bytes).
        exclude_beginning: Exclude the first num_lines lines instead of showing last.

    Returns:
        Dict with file content.
    """
    logging.info(f"Tail of {system_name}:{path}")
    return await client.tail(
        system_name=system_name,
        path=path,
        num_bytes=num_bytes,
        num_lines=num_lines,
        exclude_beginning=exclude_beginning,
    )


@mcp.tool()
async def view_file(system_name: str, path: str) -> str:
    """View the full content of a (small) file on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to the file.

    Returns:
        File content as a string.
    """
    logging.info(f"Viewing {system_name}:{path}")
    return await client.view(system_name=system_name, path=path)


@mcp.tool()
async def get_checksum(system_name: str, path: str) -> Dict[str, Any]:
    """Get the checksum of a file on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to the file.

    Returns:
        Dict with checksum info.
    """
    logging.info(f"Checksum of {system_name}:{path}")
    return await client.checksum(system_name=system_name, path=path)


@mcp.tool()
async def get_file_type(system_name: str, path: str) -> str:
    """Get the type of a file on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to the file.

    Returns:
        File type string (e.g. "regular file", "directory").
    """
    logging.info(f"File type of {system_name}:{path}")
    return await client.file_type(system_name=system_name, path=path)


@mcp.tool()
async def stat_path(
    system_name: str,
    path: str,
    dereference: bool = False,
) -> Dict[str, Any]:
    """Stat a file or directory on an HPC system.

    Args:
        system_name: Target HPC system name.
        path: Absolute path to the file or directory.
        dereference: Dereference symbolic links.

    Returns:
        Dict with stat info (size, permissions, timestamps, etc.).
    """
    logging.info(f"Stat of {system_name}:{path}")
    return await client.stat(
        system_name=system_name,
        path=path,
        dereference=dereference,
    )


# ---------------------------------------------------------------------------
# File attribute operations
# ---------------------------------------------------------------------------

# @mcp.tool()
# async def chmod(system_name: str, path: str, mode: str) -> Dict[str, Any]:
#     """Change the permissions of a file or directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         path: Absolute path to the file or directory.
#         mode: Permission mode string (e.g. "755", "644").
#
#     Returns:
#         Dict with the result.
#     """
#     logging.info(f"Chmod {mode} on {system_name}:{path}")
#     return await client.chmod(system_name=system_name, path=path, mode=mode)


# @mcp.tool()
# async def chown(
#     system_name: str,
#     path: str,
#     owner: str,
#     group: str,
# ) -> Dict[str, Any]:
#     """Change the owner and group of a file or directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         path: Absolute path to the file or directory.
#         owner: New owner username.
#         group: New group name.
#
#     Returns:
#         Dict with the result.
#     """
#     logging.info(f"Chown {owner}:{group} on {system_name}:{path}")
#     return await client.chown(
#         system_name=system_name,
#         path=path,
#         owner=owner,
#         group=group,
#     )


# ---------------------------------------------------------------------------
# File manipulation operations
# ---------------------------------------------------------------------------

# @mcp.tool()
# async def mkdir(
#     system_name: str,
#     path: str,
#     create_parents: bool = False,
# ) -> Dict[str, Any]:
#     """Create a directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         path: Absolute path of the directory to create.
#         create_parents: Create parent directories as needed (like mkdir -p).
#
#     Returns:
#         Dict with the result.
#     """
#     logging.info(f"Mkdir {system_name}:{path}")
#     return await client.mkdir(
#         system_name=system_name,
#         path=path,
#         create_parents=create_parents,
#     )


# @mcp.tool()
# async def create_symlink(
#     system_name: str,
#     source_path: str,
#     link_path: str,
# ) -> Dict[str, Any]:
#     """Create a symbolic link on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         source_path: Absolute path that the symlink will point to.
#         link_path: Absolute path of the symlink to create.
#
#     Returns:
#         Dict with the result.
#     """
#     logging.info(f"Symlink {system_name}:{link_path} -> {source_path}")
#     return await client.symlink(
#         system_name=system_name,
#         source_path=source_path,
#         link_path=link_path,
#     )


# @mcp.tool()
# async def move_path(
#     system_name: str,
#     source_path: str,
#     target_path: str,
#     account: Optional[str] = None,
#     blocking: bool = True,
#     timeout: Optional[float] = None,
# ) -> Dict[str, Any]:
#     """Move or rename a file or directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         source_path: Absolute path of the source.
#         target_path: Absolute path of the destination.
#         account: Account/project for the transfer job.
#         blocking: Wait for the operation to complete.
#         timeout: Maximum time to wait for the job to complete.
#
#     Returns:
#         Dict with the result.
#     """
#     logging.info(f"Move {system_name}:{source_path} -> {target_path}")
#     return await client.mv(
#         system_name=system_name,
#         source_path=source_path,
#         target_path=target_path,
#         account=account,
#         blocking=blocking,
#         timeout=timeout,
#     )


# @mcp.tool()
# async def copy_path(
#     system_name: str,
#     source_path: str,
#     target_path: str,
#     dereference: bool = False,
#     account: Optional[str] = None,
#     blocking: bool = True,
#     timeout: Optional[float] = None,
# ) -> Dict[str, Any]:
#     """Copy a file or directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         source_path: Absolute path of the source.
#         target_path: Absolute path of the destination.
#         dereference: Dereference symbolic links when copying.
#         account: Account/project for the transfer job.
#         blocking: Wait for the operation to complete.
#         timeout: Maximum time to wait for the job to complete.
#
#     Returns:
#         Dict with the result.
#     """
#     logging.info(f"Copy {system_name}:{source_path} -> {target_path}")
#     return await client.cp(
#         system_name=system_name,
#         source_path=source_path,
#         target_path=target_path,
#         dereference=dereference,
#         account=account,
#         blocking=blocking,
#         timeout=timeout,
#     )


# @mcp.tool()
# async def remove_path(
#     system_name: str,
#     path: str,
#     account: Optional[str] = None,
#     blocking: bool = True,
#     timeout: Optional[float] = None,
# ) -> Dict[str, Any]:
#     """Remove a file or directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         path: Absolute path to remove.
#         account: Account/project for the transfer job (only relevant when the
#             file is not deleted directly).
#         blocking: Wait for the operation to complete.
#         timeout: Maximum time to wait for the job to complete.
#
#     Returns:
#         Dict with the result, or empty dict if none returned.
#     """
#     logging.info(f"Remove {system_name}:{path}")
#     result = await client.rm(
#         system_name=system_name,
#         path=path,
#         account=account,
#         blocking=blocking,
#         timeout=timeout,
#     )
#     return result if result is not None else {}


# ---------------------------------------------------------------------------
# File transfer
# ---------------------------------------------------------------------------

# @mcp.tool()
# async def upload_file(
#     system_name: str,
#     local_file: str,
#     directory: str,
#     filename: str,
#     account: Optional[str] = None,
#     blocking: bool = True,
#     transfer_method: str = "s3",
# ) -> Dict[str, Any]:
#     """Upload a local file to a remote directory on an HPC system.
#
#     Args:
#         system_name: Target HPC system name.
#         local_file: Path to the local file to upload.
#         directory: Target directory on the remote filesystem.
#         filename: Name of the file on the remote filesystem.
#         account: Account/project for the transfer job (relevant for large files only).
#         blocking: Wait for the transfer to complete (relevant for large files only).
#         transfer_method: Method used to upload large files. One of "s3",
#             "streamer", "wormhole" (default "wormhole").
#
#     Returns:
#         Dict with transfer job info for large files, or empty dict for small files.
#     """
#     logging.info(f"Uploading {local_file} to {system_name}:{directory}/{filename}")
#     result = await client.upload(
#         system_name=system_name,
#         local_file=local_file,
#         directory=directory,
#         filename=filename,
#         account=account,
#         blocking=blocking,
#         transfer_method=transfer_method,
#     )
#     return result if result is not None else {}


@mcp.tool()
async def download_file(
    system_name: str,
    source_path: str,
    target_path: str,
    account: Optional[str] = None,
    blocking: bool = True,
    transfer_method: str = "s3",
) -> Dict[str, Any]:
    """Download a file from a remote HPC system to a local path.

    Args:
        system_name: Source HPC system name.
        source_path: Path to the file on the remote filesystem.
        target_path: Local path where the file should be saved.
        account: Account/project for the transfer job (relevant when the file
            is larger than MAX_DIRECT_UPLOAD_SIZE).
        blocking: Wait for the transfer to complete.
        transfer_method: Method used to download large files. One of "s3",
            "streamer", "wormhole" (default "wormhole").

    Returns:
        Dict with transfer job info for large files, or empty dict for small files.
    """
    logging.info(f"Downloading {system_name}:{source_path} to {target_path}")
    result = await client.download(
        system_name=system_name,
        source_path=source_path,
        target_path=target_path,
        account=account,
        blocking=blocking,
        transfer_method=transfer_method,
    )
    return result if result is not None else {}


# ---------------------------------------------------------------------------
# Archive operations
# ---------------------------------------------------------------------------

# @mcp.tool()
# async def compress_path(
#     system_name: str,
#     source_path: str,
#     target_path: str,
#     dereference: bool = False,
#     compression: str = "gzip",
#     match_pattern: Optional[str] = None,
#     account: Optional[str] = None,
#     blocking: bool = True,
# ) -> str:
#     """Compress a file or directory into an archive on an HPC system.
#
#     Args:
#         system_name: HPC system name where the filesystem belongs.
#         source_path: Absolute path to the source file or directory to compress.
#         target_path: Absolute path for the newly created compressed archive.
#         dereference: Dereference symbolic links when compressing.
#         compression: Compression algorithm to use (default: "gzip").
#         match_pattern: Optional glob pattern to filter files to compress.
#         account: Account/project for the operation.
#         blocking: Wait for the operation to complete.
#
#     Returns:
#         Confirmation message.
#     """
#     logging.info(f"Compressing {system_name}:{source_path} -> {target_path}")
#     await client.compress(
#         system_name=system_name,
#         source_path=source_path,
#         target_path=target_path,
#         dereference=dereference,
#         compression=compression,
#         match_pattern=match_pattern,
#         account=account,
#         blocking=blocking,
#     )
#     return f"Compressed {source_path} to {target_path} on {system_name}."


# @mcp.tool()
# async def extract_archive(
#     system_name: str,
#     source_path: str,
#     target_path: str,
#     compression: str = "gzip",
#     account: Optional[str] = None,
#     blocking: bool = True,
# ) -> str:
#     """Extract an archive on an HPC system.
#
#     Args:
#         system_name: HPC system name where the filesystem belongs.
#         source_path: Absolute path to the archive to extract.
#         target_path: Absolute path of an existing directory where files will be extracted.
#         compression: Compression algorithm to use (default: "gzip").
#         account: Account/project for the operation.
#         blocking: Wait for the operation to complete.
#
#     Returns:
#         Confirmation message.
#     """
#     logging.info(f"Extracting {system_name}:{source_path} -> {target_path}")
#     await client.extract(
#         system_name=system_name,
#         source_path=source_path,
#         target_path=target_path,
#         compression=compression,
#         account=account,
#         blocking=blocking,
#     )
#     return f"Extracted {source_path} to {target_path} on {system_name}."


# ---------------------------------------------------------------------------
# Job management
# ---------------------------------------------------------------------------

@mcp.tool()
async def submit_job(
    system_name: str,
    working_directory: str,
    script: Optional[str] = None,
    script_local_path: Optional[str] = None,
    script_remote_path: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    account: Optional[str] = None,
) -> Dict[str, Any]:
    """Submit a batch job to the HPC scheduler on the given system.

    Exactly one of `script` (inline content), `script_local_path` (local file),
    or `script_remote_path` (path already on the remote filesystem) must be provided.

    Args:
        system_name: Target HPC system name.
        working_directory: Working directory for the job on the remote filesystem.
        script: Inline batch script content.
        script_local_path: Path to a local batch script file to upload and submit.
        script_remote_path: Path to an existing batch script on the remote filesystem.
        env_vars: Optional dict of environment variables to set for the job.
        account: Optional account/project to charge.

    Returns:
        Dict containing the submitted job ID, e.g. {"jobId": "12345"}.
    """
    if not script and not script_local_path and not script_remote_path:
        raise ValueError(
            "One of 'script', 'script_local_path', or 'script_remote_path' must be provided."
        )

    logging.info(f"Submitting job on {system_name}")

    result = await client.submit(
        system_name=system_name,
        working_dir=working_directory,
        script_str=script,
        script_local_path=script_local_path,
        script_remote_path=script_remote_path,
        env_vars=env_vars,
        account=account,
    )

    return result


@mcp.tool()
async def get_job_status(
    system_name: str,
    job_id: str | None = None,
    allusers: bool = False,
    account: Optional[str] = None,
) -> Dict[str, Any] | List[Dict[str, Any]]:
    """Get the status and details of a job, or of all jobs.

    Args:
        system_name: Target HPC system name.
        job_id: The job ID to query. If None, returns the status of all jobs.
        allusers: Return jobs of all users instead of only the current user.
        account: Account to filter the jobs by. Only taken into account when
            no job_id is specified.

    Returns:
        A single dict with the job details when job_id is given, or a list of
        job dicts when querying all jobs. Each dict includes state, exit code,
        timing, nodes, etc.
    """
    logging.info(f"Fetching status for job {job_id} on {system_name}")
    result = await client.job_info(
        system_name=system_name,
        jobid=job_id,
        allusers=allusers,
        account=account,
    )
    if job_id is not None:
        return result[0] if result else {}
    return result


@mcp.tool()
async def get_job_metadata(system_name: str, job_id: str) -> List[Dict[str, Any]]:
    """Get detailed metadata for a specific job.

    Args:
        system_name: Target HPC system name.
        job_id: The job ID to query.

    Returns:
        Dict with detailed job metadata.
    """
    logging.info(f"Fetching metadata for job {job_id} on {system_name}")
    return await client.job_metadata(system_name=system_name, jobid=job_id)


@mcp.tool()
async def cancel_job(system_name: str, job_id: str) -> str:
    """Cancel a running or pending job.

    Args:
        system_name: Target HPC system name.
        job_id: The job ID to cancel.

    Returns:
        Confirmation message.
    """
    logging.info(f"Cancelling job {job_id} on {system_name}")
    await client.cancel_job(system_name=system_name, jobid=job_id)
    return f"Job {job_id} cancelled successfully."


@mcp.tool()
async def attach_to_job(
    system_name: str,
    job_id: str,
    command: str,
) -> Dict[str, Any]:
    """Attach a command to a running job on an HPC system.

    Args:
        system_name: Target HPC system name.
        job_id: The job ID to attach to.
        command: Command to run attached to the job.

    Returns:
        Dict with the result.
    """
    logging.info(f"Attaching to job {job_id} on {system_name}")
    return await client.attach_to_job(
        system_name=system_name,
        jobid=job_id,
        command=command,
    )


@mcp.tool()
async def wait_for_job(
    system_name: str,
    job_id: str,
    timeout: Optional[float] = None,
    not_found_timeout: float = 20.0,
) -> Optional[Dict[str, Any]]:
    """Wait for a job to complete on an HPC system (blocking poll).

    Args:
        system_name: Target HPC system name.
        job_id: The job ID to wait for.
        timeout: Maximum seconds to wait (None = wait indefinitely).
        not_found_timeout: Seconds to keep retrying if job is not found yet (default 20).

    Returns:
        List with final job state info.
    """
    logging.info(f"Waiting for job {job_id} on {system_name}")
    return await client.wait_for_job(
        system_name=system_name,
        job_id=job_id,
        timeout=timeout,
        not_found_timeout=not_found_timeout,
    )


# ---------------------------------------------------------------------------
# Request statistics
# ---------------------------------------------------------------------------
# The statistics are global to the server process. Over stdio the process
# serves a single Claude Code session, so they describe exactly what that
# session did and the tools below are registered. Over HTTP the process is
# shared by all the users, so the tools are not registered: they would expose
# everyone's requests (endpoints, query parameters) to any user, and let any
# user reset the counters. The per-request log lines are emitted in both modes.

def _record_as_dict(record) -> Dict[str, Any]:
    d = record.as_dict()
    d["time"] = datetime.datetime.fromtimestamp(
        record.timestamp, tz=datetime.timezone.utc
    ).isoformat(timespec="milliseconds")
    return d


async def get_request_stats(last: int = 20) -> Dict[str, Any]:
    """Get statistics about the HTTP requests this server has sent to the
    FirecREST API since it started (or since the last reset).

    Every request is counted, retries included. Use this to see how many
    calls the tools translate to, which endpoints are hit, how long they
    take and which ones fail.

    Args:
        last: Number of most recent requests to include in `records`
            (0 for none). The server keeps the last
            REQUEST_STATS_MAX_RECORDS requests (1000 by default, 0 for
            all); the number kept is returned in `recorded`.

    Returns:
        Dict with the counters (total, retries, failed, total_duration,
        average_duration, by_method, by_endpoint, by_status) and the most
        recent requests under `records`, oldest first. Each record has the
        method, endpoint, query params, status code or error, duration,
        time, attempt number and tracing IDs.
    """
    logging.info("Invoking get_request_stats tool")
    if request_stats is None:
        return {
            "enabled": False,
            "message": "The installed pyfirecrest does not record request "
                       "statistics (a release newer than 3.10.0 is needed).",
        }

    stats = request_stats.as_dict()
    records = stats.pop("records")
    stats["average_duration"] = (
        stats["total_duration"] / stats["total"] if stats["total"] else 0.0
    )
    stats["recorded"] = len(records)
    stats["records"] = [
        _record_as_dict(r) for r in request_stats.records[-last:]
    ] if last > 0 else []
    return {"enabled": request_stats.enabled, **stats}


async def reset_request_stats() -> Dict[str, Any]:
    """Reset the request statistics of this server: the counters go back
    to zero and the history of requests is cleared. The FirecREST API and
    the HPC systems are not touched.

    Returns:
        Dict with the counters that were discarded (total, retries, failed).
    """
    logging.info("Invoking reset_request_stats tool")
    if request_stats is None:
        return {"enabled": False, "total": 0, "retries": 0, "failed": 0}

    discarded = {
        "total": request_stats.total,
        "retries": request_stats.retries,
        "failed": request_stats.failed,
    }
    request_stats.reset()
    return {"enabled": request_stats.enabled, **discarded}


# ---------------------------------------------------------------------------
# Server entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["http", "stdio"], default="http")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8888)
    return parser.parse_args()


def register_request_stats_tools():
    mcp.tool(get_request_stats)
    mcp.tool(reset_request_stats)


def main(args):
    if args.transport == "stdio":
        register_request_stats_tools()
        mcp.run(transport="stdio")
    else:
        # FIXME: stateless_http=True was added to simplify the invokations debugging during development (implications unclear!)
        mcp.run(transport="http", stateless_http=True, host=args.host, port=args.port)


if __name__ == "__main__":
    main(args=parse_args())
