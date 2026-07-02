export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Privacy Notice</h1>
        <p className="text-sm text-slate-500">Last updated: July 2026</p>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-800">Overview</h2>
          <p className="text-slate-600 leading-relaxed">
            This website is a personal portfolio and resume platform. We respect your privacy and are committed to protecting your personal data. This privacy notice explains how we handle information when you visit our site.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-800">Data We Collect</h2>
          <ul className="list-disc list-inside space-y-2 text-slate-600">
            <li>
              <strong>No personal data collection:</strong> This site does not collect, store, or process any personal information from visitors.
            </li>
            <li>
              <strong>No cookies:</strong> We do not use tracking cookies or third-party analytics.
            </li>
            <li>
              <strong>No user accounts:</strong> There is no registration or login system for visitors.
            </li>
            <li>
              <strong>AI Chatbot:</strong> Questions you ask the AI assistant are processed in real-time and are not stored or logged.
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-800">Third-Party Services</h2>
          <ul className="list-disc list-inside space-y-2 text-slate-600">
            <li>
              <strong>AI Provider (DeepSeek):</strong> Chat queries are sent to DeepSeek API for processing. Please review their privacy policy at deepseek.com.
            </li>
            <li>
              <strong>Hosting:</strong> This site is hosted on servers that may log standard access information (IP address, browser type, timestamp) for security purposes.
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-800">Your Rights (GDPR)</h2>
          <p className="text-slate-600 leading-relaxed">
            Under the General Data Protection Regulation (GDPR), you have rights regarding your personal data. Since we do not collect personal data, these rights are not directly applicable. However, if you have any concerns or questions, please contact us using the information below.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-800">Contact</h2>
          <p className="text-slate-600 leading-relaxed">
            For privacy-related inquiries, please reach out via the contact methods listed on our homepage.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-slate-800">Changes to This Notice</h2>
          <p className="text-slate-600 leading-relaxed">
            We may update this privacy notice from time to time. Any changes will be posted on this page with an updated revision date.
          </p>
        </section>

        <div className="pt-6 border-t border-slate-200">
          <a
            href="/"
            className="inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-lg transition"
          >
            Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
