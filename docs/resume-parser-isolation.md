# Resume parser isolation

NextHire parses every uploaded PDF or DOCX in a fresh subprocess after the API
has enforced the extension, 5 MB upload limit, file signature, and optional
ClamAV scan. The API awaits the worker asynchronously, so document parsing does
not run in the API process or block its event loop.

## Application boundary

The parser worker receives only:

- the application-generated absolute temporary-file path;
- the already-validated `.pdf` or `.docx` suffix; and
- bounded input, extracted-text, memory, and CPU settings.

It does not inherit the API environment, including database credentials, JWT
secrets, SMTP credentials, job-provider keys, or billing configuration. The
worker disables Python socket entry points before parsing, applies a CPU limit,
disables core dumps, limits open file descriptors, and applies an address-space
limit on Linux. PDF and DOCX readers stop accumulating text at the configured
character cap.

The parent API enforces a separate wall-clock timeout. Timeout or request
cancellation stops the worker. The temporary file is removed after clean,
rejected, unavailable, timed-out, or cancelled processing.

There is no in-process parser fallback:

- malformed, unreadable, empty-text, or text-limit failures return a generic
  HTTP 400 response;
- worker startup, resource, timeout, protocol, or unexpected-exit failures
  return a generic HTTP 503 response; and
- parser exceptions and subprocess output are not returned to the user.

## Configuration

```env
RESUME_PARSER_TIMEOUT_SECONDS=20
RESUME_PARSER_MAX_CPU_SECONDS=15
RESUME_PARSER_MAX_MEMORY_MB=512
RESUME_PARSER_MAX_TEXT_CHARACTERS=200000
```

Bounds are enforced in application settings. Tune them only from measured
staging evidence; a value that is too low rejects legitimate resumes, while an
unnecessarily high value weakens resource protection.

## Deployment hardening

The subprocess is a meaningful failure and secret-isolation boundary, but it
is not a separate container, virtual machine, or operating-system network
namespace. Python-level network blocking is defense in depth, not a substitute
for infrastructure egress controls.

Before public production use:

1. Run the API as an unprivileged user with a read-only application filesystem
   and a narrowly writable temporary directory.
2. Block cloud metadata and unrestricted outbound network access at the
   container or platform layer.
3. Apply container-level memory, CPU, process-count, and temporary-storage
   limits in addition to the per-worker limits.
4. Monitor parser 400/503 rates, timeouts, worker exits, latency, and container
   pressure without logging resume text or filenames.
5. Keep parser libraries patched and include them in dependency and
   vulnerability review.

## Staged verification

Use disposable accounts and synthetic documents:

1. Upload a genuine clean PDF and DOCX through Resume Studio, profile autofill,
   and Resume Tailor; confirm all six operations complete.
2. Confirm concurrent health and authenticated API requests remain responsive
   during parsing.
3. Confirm malformed PDF/DOCX content is rejected generically and no temporary
   file remains.
4. Set a deliberately low extracted-text limit in a non-production environment
   and confirm an oversized-text fixture is rejected before AI processing.
5. Exercise the automated timeout/cancellation coverage and confirm no parser
   subprocess remains.
6. Restore production-like bounds, repeat clean uploads, and record latency and
   resource use.

Do not test with real malware. Use the separately documented harmless scanner
fixture only when validating the ClamAV boundary.
