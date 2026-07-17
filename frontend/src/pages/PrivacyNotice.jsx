import { Link } from "react-router-dom";

function PrivacyNotice() {
  return (
    <main className="min-h-screen bg-gray-950 px-6 py-12 text-gray-300">
      <article className="mx-auto max-w-3xl space-y-7 rounded-3xl border border-gray-800 bg-gray-900 p-8 md:p-12">
        <div><p className="text-sm font-semibold text-blue-400">Effective July 17, 2026</p><h1 className="mt-2 text-4xl font-bold text-white">Privacy Notice</h1></div>
        <section><h2 className="text-xl font-semibold text-white">Data we process</h2><p className="mt-2 leading-7">We process account identifiers, career profiles, uploaded resume text, generated documents, job applications, product usage records, and security events. Passwords are stored only as one-way hashes.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Why we use it</h2><p className="mt-2 leading-7">Data is used to provide requested career features, authenticate accounts, personalize results, enforce limits, prevent abuse, maintain reliability, and meet legal obligations. Customer content must not be used for model training without separate explicit consent.</p></section>
        <section><h2 className="text-xl font-semibold text-white">AI and job providers</h2><p className="mt-2 leading-7">Resume or career content may be sent to the configured AI provider to complete a requested feature. Job-search terms are sent to the providers identified in search results. Production launch requires a current subprocessor list and review of each provider’s contract and transfer terms.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Retention and security</h2><p className="mt-2 leading-7">Active content remains until you delete it or close your account. Operational records and backups follow documented, limited retention schedules. We use access controls, encrypted transport, scoped repositories, upload limits, and monitoring, but no system can guarantee absolute security.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Your choices</h2><p className="mt-2 leading-7">Settings lets you download a portable copy of stored data and permanently delete your account. Depending on location, you may also have rights to access, correct, restrict, object, or complain to a regulator.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Launch notice</h2><p className="mt-2 leading-7">The operating company’s legal name, privacy contact, jurisdiction-specific rights, subprocessors, international transfer mechanism, cookie details, and exact retention periods must be added before public commercial launch.</p></section>
        <Link to="/login" className="inline-block font-semibold text-blue-400">Return to sign in</Link>
      </article>
    </main>
  );
}

export default PrivacyNotice;
