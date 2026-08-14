---
name: job-monitoring
description: Check the status of a Slurm job on a CSCS HPC system via FirecREST, inspect its output files, and diagnose why it is pending or failed. Use when the user asks about their job's state, progress, output, or errors.
---

# Monitoring a Slurm job through FirecREST

Use the `firecrest` MCP tools. Work read-only: this plugin cannot submit, cancel,
or modify anything.

## Workflow

1. **Identify system and job.** If the user didn't name the system, call
   `get_systems` and ask which one they mean (don't guess). If they didn't give a
   job ID, ask for it — job IDs are per-system.
2. **Get the job state** with `get_job_status`. Interpret the Slurm state for the
   user: `PENDING` (waiting for resources — check reason code), `RUNNING`,
   `COMPLETED`, `FAILED`, `TIMEOUT`, `OUT_OF_MEMORY`, `CANCELLED`, `NODE_FAIL`.
3. **For pending jobs**, explain the reason code (e.g. `Priority`, `Resources`,
   `ReqNodeNotAvail`, `QOSMaxJobsPerUserLimit`, `AssocGrpBillingMinutes`). Use
   `get_partitions` and `get_reservations` to check whether the requested
   partition is up and how busy it is, and `get_nodes` for node availability.
4. **For running or finished jobs**, find the output files: `get_job_metadata`
   returns the job's working directory and stdout/stderr paths. Use `tail_file`
   on stdout/stderr rather than `view_file` — output files can be huge. Quote the
   relevant lines when reporting errors.
5. **For failed jobs**, look at the end of stderr first, then the end of stdout.
   Common patterns: `OOM` / `oom-kill` (out of memory — suggest more memory per
   node or fewer tasks), `DUE TO TIME LIMIT` (suggest a longer `--time` or
   checkpointing), module or shared-library errors near the start of the output
   (environment problem in the job script — inspect it with `view_file` using the
   script path from the job metadata).
6. **Only poll when asked.** If the user asks to wait for a job, use
   `wait_for_job`. Otherwise report the current state once — don't loop.

## Reporting

Summarize state in one line first (state, elapsed/queue time, partition, nodes),
then the relevant detail (reason code, error excerpt, next steps). Use the user's
terminology ("your job", the job name) rather than raw Slurm field names where
possible.
