import { useEffect, useState } from "react";
import {
  Sparkles,
  FileText,
  Briefcase,
  CheckCircle,
} from "lucide-react";

import api from "../services/api";
import DocumentLibrary from "../components/documents/DocumentLibrary";

function ResumeTailor() {
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState("auto");

  useEffect(() => {
    let active = true;

    api.get("/resume/templates")
      .then((response) => {
        if (active) setTemplates(response.data);
      })
      .catch(() => {
        if (active) setTemplates([]);
      });

    return () => {
      active = false;
    };
  }, []);

  const tailorResume = async () => {
    if (!jobDescription.trim()) {
      alert("Please paste a job description.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      formData.append("job_description", jobDescription);
      formData.append("template_id", selectedTemplate);

      const response = await api.post(
        "/resume/tailor-upload",
        formData
      );

      setResult(response.data);
    } catch (requestError) {
      const detail = requestError.response?.data?.detail;
      alert(
        typeof detail === "string"
          ? detail
          : "Resume tailoring failed."
      );
    }

    setLoading(false);
  };

  return (
    <div className="space-y-8">

      {/* Hero */}

      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 shadow-xl">

        <h1 className="text-4xl font-bold text-white">
          AI Resume Tailor
        </h1>

        <p className="text-blue-100 mt-3 text-lg">
          Optimize your resume for any job description using AI.
        </p>

      </div>

      {/* Upload & Job Description */}

      <div className="grid grid-cols-1 gap-6">
        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

          <div className="flex items-center gap-3 mb-5">

            <Briefcase className="text-blue-500" />

            <h2 className="text-2xl font-bold text-white">
              Job Description
            </h2>

          </div>

          <p className="mb-4 text-sm text-gray-400">
            Your latest Resume Studio document and authenticated profile are used automatically.
          </p>

          <textarea
            rows={10}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description..."
            className="w-full bg-gray-800 rounded-xl border border-gray-700 p-4 text-white resize-none focus:outline-none focus:border-blue-500"
          />

        </div>

      </div>

      {/* Template selection */}

      <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">
        <div className="flex items-center gap-3 mb-2">
          <FileText className="text-blue-400" />
          <h2 className="text-2xl font-bold text-white">
            Resume Template
          </h2>
        </div>
        <p className="mb-5 text-sm text-gray-400">
          Let the AI agent choose the best design, or select one yourself.
        </p>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <button
            type="button"
            onClick={() => setSelectedTemplate("auto")}
            className={`rounded-xl border p-4 text-left transition ${selectedTemplate === "auto" ? "border-blue-500 bg-blue-500/10" : "border-gray-700 bg-gray-800 hover:border-gray-600"}`}
          >
            <div className="mb-3 h-2 rounded-full bg-gradient-to-r from-blue-500 via-teal-500 to-gray-300" />
            <h3 className="font-semibold text-white">AI recommended</h3>
            <p className="mt-2 text-sm text-gray-400">
              The agent selects a suitable ATS-safe design for the role.
            </p>
          </button>

          {templates.map((template) => (
            <button
              key={template.id}
              type="button"
              onClick={() => setSelectedTemplate(template.id)}
              className={`rounded-xl border p-4 text-left transition ${selectedTemplate === template.id ? "border-blue-500 bg-blue-500/10" : "border-gray-700 bg-gray-800 hover:border-gray-600"}`}
            >
              <div
                className="mb-3 h-2 rounded-full"
                style={{ backgroundColor: template.accent }}
              />
              <h3 className="font-semibold text-white">{template.name}</h3>
              <p className="mt-1 text-xs uppercase tracking-wide text-gray-500">
                {template.font_style}
              </p>
              <p className="mt-2 text-sm text-gray-400">
                {template.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Button */}

      <button
        onClick={tailorResume}
        className="bg-blue-600 hover:bg-blue-700 transition px-8 py-3 rounded-xl text-white font-semibold"
      >
        {loading ? "Tailoring Resume..." : "Tailor Resume"}
      </button>

      {/* Results */}

      {result && (
        <>
          <div className="flex items-center gap-2 rounded-xl border border-blue-900 bg-blue-950/40 px-4 py-3 text-sm text-blue-200">
            <CheckCircle size={17} />
            Template: {templates.find((template) => template.id === result.template_id)?.name || result.template_id}
          </div>

          {/* Professional Summary */}

          <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

            <div className="flex items-center gap-3 mb-5">

              <Sparkles className="text-yellow-400" />

              <h2 className="text-2xl font-bold text-white">
                AI Professional Summary
              </h2>

            </div>

            <p className="text-gray-300 whitespace-pre-wrap leading-8">
              {result.summary}
            </p>

          </div>

          {/* Skills */}

          <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

            <div className="flex items-center gap-3 mb-5">

              <FileText className="text-green-500" />

              <h2 className="text-2xl font-bold text-white">
                Optimized Skills
              </h2>

            </div>

            <div className="flex flex-wrap gap-3">

              {result.skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-green-700 rounded-full px-4 py-2 flex items-center gap-2"
                >
                  <CheckCircle size={16} />
                  {skill}
                </span>
              ))}

            </div>

          </div>

          {/* Experience */}

          <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

            <h2 className="text-2xl font-bold text-white mb-5">
              Tailored Experience
            </h2>

            <div className="space-y-4">

              {result.experience.map((item, index) => (
                <div
                  key={index}
                  className="bg-gray-800 rounded-xl p-4"
                >
                  {typeof item === "object" && item !== null ? (
                    <>
                      {(item.role || item.company || item.dates) && (
                        <h3 className="font-semibold text-white">
                          {[item.role, item.company, item.dates]
                            .filter(Boolean)
                            .join(" | ")}
                        </h3>
                      )}
                      {Array.isArray(item.bullets) && item.bullets.length > 0 && (
                        <ul className="mt-3 list-disc space-y-2 pl-5 text-gray-300">
                          {item.bullets.map((bullet) => (
                            <li key={bullet}>{bullet}</li>
                          ))}
                        </ul>
                      )}
                    </>
                  ) : (
                    item
                  )}
                </div>
              ))}

            </div>

          </div>

          {[
            ["Education", result.education],
            ["Certifications", result.certifications],
            ["Projects", result.projects],
          ].map(([heading, values]) => (
            Array.isArray(values) && values.length > 0 && (
              <div key={heading} className="bg-gray-900 rounded-2xl border border-gray-800 p-6">
                <h2 className="text-2xl font-bold text-white mb-5">
                  {heading}
                </h2>
                <ul className="list-disc space-y-2 pl-5 text-gray-300">
                  {values.map((value) => (
                    <li key={value}>{value}</li>
                  ))}
                </ul>
              </div>
            )
          ))}
        </>
      )}

      <DocumentLibrary refreshToken={result?.document_id} />

    </div>
  );
}

export default ResumeTailor;
