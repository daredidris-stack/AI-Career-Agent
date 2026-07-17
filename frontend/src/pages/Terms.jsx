import { Link } from "react-router-dom";

function Terms() {
  return (
    <main className="min-h-screen bg-gray-950 px-6 py-12 text-gray-300">
      <article className="mx-auto max-w-3xl space-y-7 rounded-3xl border border-gray-800 bg-gray-900 p-8 md:p-12">
        <div><p className="text-sm font-semibold text-blue-400">Effective July 17, 2026</p><h1 className="mt-2 text-4xl font-bold text-white">Terms of Use</h1></div>
        <section><h2 className="text-xl font-semibold text-white">The service</h2><p className="mt-2 leading-7">NextHire AI provides career organization and AI-assisted drafting tools. It does not act as an employer, recruiter, employment agency, lawyer, or financial adviser. Job listings originate from identified third-party providers.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Your responsibilities</h2><p className="mt-2 leading-7">You must provide lawful and accurate information, protect your account, review generated material before use, and ensure every application remains truthful. Do not upload content you lack permission to process or use the service to violate another person’s rights.</p></section>
        <section><h2 className="text-xl font-semibold text-white">AI and job information</h2><p className="mt-2 leading-7">AI output may be incomplete or inaccurate and is not a guarantee of employment. Job availability, salary, location, and requirements can change. Verify listing details with the source provider and employer before applying or sharing personal information.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Acceptable use</h2><p className="mt-2 leading-7">Do not bypass usage limits, scrape the service, distribute malware, probe other accounts, automate abusive traffic, impersonate others, or interfere with providers. Access may be limited or suspended to protect users and infrastructure.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Accounts and content</h2><p className="mt-2 leading-7">You retain rights in content you submit. You permit processing only as needed to operate and secure the service. You may export or delete your data in Settings. Third-party services remain governed by their own terms.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Commercial terms</h2><p className="mt-2 leading-7">Plan limits, prices, renewal terms, cancellation rights, and refund rules will be shown before a paid purchase. Paid features must not be activated until those terms and the operating company’s legal identity are finalized.</p></section>
        <section><h2 className="text-xl font-semibold text-white">Important legal notice</h2><p className="mt-2 leading-7">Warranty disclaimers, liability limits, governing law, dispute terms, company identity, and formal contact details require approval for the launch jurisdiction before commercial release. This beta draft does not replace that review.</p></section>
        <Link to="/login" className="inline-block font-semibold text-blue-400">Return to sign in</Link>
      </article>
    </main>
  );
}

export default Terms;
