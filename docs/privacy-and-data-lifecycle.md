# Privacy and data lifecycle

NextHire AI processes account details, career profiles, resumes, generated documents, job applications, and AI usage metadata. These records are private to the authenticated account and must never be used to train a model or shared with a third party without an explicit, documented basis and user notice.

## User controls

- `GET /users/me/export` provides a portable JSON copy of all stored account data except password hashes and authentication internals.
- `DELETE /users/me` requires the current password and permanently removes the account, profile, resume analyses, career documents and revisions, applications, and AI usage events.
- Individual documents, profiles, and applications can be deleted from their respective interfaces.

Deletion from the primary database is immediate. Backup copies expire according to the backup retention schedule and must not be restored into production without reapplying deletion requests recorded after the backup timestamp.

## Retention policy

- Active customer content is retained until the user deletes it or closes the account.
- AI usage events should be retained only as long as needed for abuse prevention, billing reconciliation, and security review.
- Application logs must not contain resumes, profile content, job descriptions, access tokens, passwords, or request bodies.
- Production backups must have a documented retention period, encryption, access controls, and tested deletion/restore procedures.

Before commercial launch, publish a jurisdiction-appropriate privacy notice that identifies the company acting as data controller, subprocessors, international transfers, lawful bases, contact channel, retention periods, and user rights.

## Upload security

Resume uploads accept only PDF and DOCX, are capped at 5 MB by default, and are checked for matching file signatures before parsing. Files are processed through short-lived temporary storage and removed after extraction. Uploaded filenames are metadata only and are never used as filesystem paths.

Production should additionally scan uploads with a maintained malware scanner in an isolated worker before document parsing. Parsing workers should have no cloud metadata access, minimal filesystem permissions, memory/CPU limits, and no unrestricted outbound network access.

## Isolation verification

All repositories for profiles, documents, revisions, applications, analyses, exports, and AI usage scope queries by authenticated `user_id`. Automated tests must continue to cover cross-account reads, updates, exports, and deletions whenever these data models change.
