### Description

Submitting, monitoring and cancelling batch jobs on HPC systems through the FirecREST MCP server (`submit_job`, `get_job_status`, `get_job_metadata`, `wait_for_job`, `cancel_job`, `attach_to_job`, plus `get_partitions`, `get_nodes`, `get_reservations`, `get_userinfo` for context). Use this skill whenever the user wants to run, submit, launch, queue, check on, wait for, debug, cancel or kill a job on a cluster or supercomputer, write or review a Slurm/sbatch script, see why a job is pending or failed, or find out which partitions, nodes or reservations are available, even if they never mention FirecREST. For reading job output files or managing files, combine with firecrest-files-read and firecrest-files-write.

# FirecREST: job management

Jobs consume shared, often accounted, compute resources. Submitting and cancelling have real consequences; checking status is free. Tool names carry the prefix `mcp__firecrest__`; load schemas with tool_search if needed.

## Always start with context

1. `system_name` is required everywhere. Use `get_systems` if unknown, and ask if several systems exist and the user did not say which.
2. For a new submission, gather what the job needs: partition, node and task counts, time limit, account. Use `get_partitions` (and `get_reservations` if the user mentions one) to confirm that the requested partition exists and its limits fit. `get_userinfo` shows the user's groups, which often hint at the project or account.
3. Never invent an account, partition or reservation. If it is missing, ask.

## Tool map

|Goal|Tool|Notes|
|---|---|---|
|Submit a job|`submit_job`|Exactly **one** of `script`, `script_local_path`, `script_remote_path`|
|List my jobs / check one job|`get_job_status`|No `job_id` = all of the user's jobs; `account` filters only in that case|
|Deeper details on one job|`get_job_metadata`|Needs `job_id`; fields depend on scheduler and server version|
|Block until a job finishes|`wait_for_job`|Set `timeout`; `not_found_timeout` covers the delay before a new job appears|
|Stop a job|`cancel_job`|Needs confirmation (see below)|
|Run a command inside a running job|`attach_to_job`|Needs confirmation (see below)|
|What can I request?|`get_partitions`, `get_nodes`, `get_reservations`|Read-only capacity info|

`job_id` is a **string**. Pass `"12345"`, not a number.

## Submitting a job

1. Choose the script source:
    - `script`: inline content, best when drafting a script together in chat
    - `script_remote_path`: the script is already on the cluster (verify with `stat_path` first)
    - `script_local_path`: a file on the machine running the MCP server
2. `working_directory` is required and must be an existing absolute remote path. Check it with `stat_path`, and create it with `mkdir` if the user agrees.
3. **Review the script before submitting.** Check the `#SBATCH` lines (or the scheduler's equivalent): partition, nodes, tasks, `--time`, `--account`, output/error file paths. Flag anything unusual: very large node counts, very long wall time, missing time limit, or output paths in a directory that does not exist (the job would fail silently).
4. **Confirm before submitting** when the job is large (many nodes or long wall time), charges an account the user did not name, or you changed or wrote the script yourself. For small jobs the user explicitly asked for, show the one-line summary and submit.
5. Pass `env_vars` as a dict of strings, and `account` only if the user gave one.
6. Report the returned job ID and the output file location, then offer to monitor it. Do not resubmit if a call times out; check `get_job_status` first, because the job may exist.

## Monitoring

- Start with `get_job_status` for a specific `job_id`. Summarize state, exit code, elapsed time and nodes, not raw JSON.
- Common states to explain: PENDING (queued; check `get_partitions`, `get_reservations` and job details for the reason), RUNNING, COMPLETED, FAILED, CANCELLED, TIMEOUT, OUT_OF_MEMORY. For states you do not recognize, quote them as returned.
- Use `wait_for_job` only when the user wants to block until completion, and always give a `timeout` (e.g. 300 to 900 seconds) instead of waiting indefinitely. If it times out, report the last known state and offer to check again, rather than looping silently.
- Do not poll in a tight loop. For long jobs, check on request or at sensible intervals.
- For "what is my job printing", find the output file path from the script or job metadata and `tail_file` it (see firecrest-files-read).
- `allusers: true` exposes other people's jobs. Use it only if the user asks.

## Debugging failed or pending jobs

1. `get_job_status` then `get_job_metadata` for state, exit code, nodes and timing.
2. `tail_file` the job's error and output files.
3. Map the symptoms:
    - TIMEOUT: the time limit was too short; suggest a larger `--time` within partition limits.
    - OUT_OF_MEMORY: suggest more memory or fewer tasks per node.
    - Failed immediately: usually a script error, a missing module or path, or a wrong account or partition.
    - Stuck PENDING: partition busy, resource request too large, or a reservation or limit.
4. Propose a fix. Resubmitting is a new submission, so the confirmation rules above apply.

## Cancelling jobs

`cancel_job` is irreversible: the job loses its place in the queue and its progress.

- Confirm first, naming the system, job ID and what is known about it (name, state, runtime).
- Cancel only job IDs the user named or clearly identified. Never bulk-cancel "all my jobs" without listing them and getting a yes for that list.
- Afterwards verify with `get_job_status`. A job may stay in a completing state briefly.

## Attaching to a job

`attach_to_job` runs a command inside a running job's allocation.

- Ask for confirmation, showing the exact command and job ID.
- Use it only for read-only diagnostics (e.g. `nvidia-smi`, `top -b -n 1`, `free -h`). Refuse commands that modify data, kill processes or start heavy work inside someone's allocation unless the user clearly asks and understands the effect.
- It works only on a RUNNING job. Check the state first.

## Errors

- _Job not found_: right after submission, wait a few seconds and retry; otherwise check `system_name`, the job ID and whether the job has aged out of the scheduler's history.
- _Invalid account or partition_: ask the user; do not guess alternatives.
- _Permission denied_: report it; do not try other users' jobs or workarounds.

## Example

User: "Run `train.sh` from my project folder and let me know when it's done."

1. `get_systems`, then `get_partitions` to confirm the partition named in the script exists
2. `stat_path` on the script and on the working directory
3. Read the script (`head_file`), summarize its resources, confirm if large
4. `submit_job` with `script_remote_path` and `working_directory`; report the job ID
5. `wait_for_job` with a `timeout`; then summarize the final state, and `tail_file` the output if it failed
