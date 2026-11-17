### Description

Read-only browsing and inspection of files and directories on HPC systems through the FirecREST MCP server (`list_files`, `stat_path`, `get_file_type`, `head_file`, `tail_file`, `view_file`, `get_checksum`). Use this skill whenever the user wants to look around a cluster filesystem, find or list files, check sizes, permissions or timestamps, read or peek at a log, output or config file, tail a job's output, or verify a checksum on an HPC system such as a supercomputer, cluster, scratch or home directory, even if they never mention FirecREST. Do NOT use it for creating, copying, moving, deleting, transferring or changing permissions on files; use firecrest-files-write for those.

# FirecREST: read-only file inspection

These tools never change anything on the remote system, so use them freely. Call the tools exactly as they are named by the MCP server (prefix `mcp__firecrest__`). If their schemas are not loaded yet, load them with tool_search first.

## Always start with the system name

Every tool needs `system_name`. If the user has not named one, or you are unsure, call `get_systems` once and reuse the answer for the rest of the conversation. If several systems exist and the user did not say which, ask. Do not guess.

Paths must be **absolute** (`/capstor/scratch/cscs/<user>/run1/log.txt`, not `~/log.txt` or `../log.txt`). If the user gives a relative path or `~`, resolve it with `get_userinfo` or ask for the full path.

## Choosing the right tool

|Goal|Tool|Notes|
|---|---|---|
|What is in this directory?|`list_files`|`show_hidden` for dotfiles; avoid `recursive` on big trees|
|Does this path exist? File or directory? Size, mode, mtime?|`stat_path`|Add `dereference: true` to follow symlinks|
|Only need the kind of thing it is|`get_file_type`|Cheaper than stat when size does not matter|
|Look at the start of a file|`head_file`|Use `num_lines` OR `num_bytes`, never both|
|Look at the end (logs, job output)|`tail_file`|Same rule: `num_lines` OR `num_bytes`|
|Read a whole small file|`view_file`|Only after confirming the file is small (see below)|
|Verify integrity after a transfer|`get_checksum`|Compare against a checksum computed locally|

## Rules of thumb

1. **Check size before reading.** Run `stat_path` first. Only use `view_file` for small text files (roughly under 100 KB). For anything larger, or of unknown size, use `head_file` / `tail_file` with an explicit `num_lines` (e.g. 50 to 200).
2. **Do not read binaries.** If `get_file_type` says the file is not text (archive, HDF5, executable), report its type and size instead of dumping its contents.
3. **Keep `list_files` narrow.** Prefer listing one directory at a time. Use `recursive` only on a small, known subtree, because scratch and project trees can hold millions of entries. Summarize long listings (counts, largest or newest items) instead of pasting everything.
4. **For "what is my job doing" questions,** `tail_file` the job's output or error file (look for `slurm-<jobid>.out` or the path set in the job script). Use `exclude_beginning` only when you really want "everything after line N".
5. **Do not echo secrets.** If a file looks like it holds credentials (SSH keys, tokens, `.netrc`, `.env`), tell the user it exists but do not print it unless they explicitly ask.

## Handling errors

- _Not found_: run `list_files` on the parent directory and check for typos, wrong filesystem (home vs scratch), or a purged scratch file.
- _Permission denied_: report it and run `stat_path` to show owner, group and mode. Do not try to fix it with `chmod` or `chown`; that belongs to firecrest-files-write and needs the user's confirmation.
- _Timeouts on big directories_: narrow the path or drop `recursive`.

## Output style

Report results concisely: path, type, size, a few relevant lines. When showing file contents, say which part you read (e.g. "last 50 lines of ...") so the user knows whether the file was truncated.

## Example

User: "What's the end of the log from my last run on daint?"

1. `list_files` on the run directory to find the newest `*.out`/`*.log` file
2. `stat_path` on it to confirm size
3. `tail_file` with `num_lines: 100`
4. Summarize, naming the file and the portion read
