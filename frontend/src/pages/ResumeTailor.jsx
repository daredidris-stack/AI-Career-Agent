import { useState } from "react";
import {
  Upload,
  Sparkles,
  FileText,
  Briefcase,
  CheckCircle,
} from "lucide-react";

import api from "../services/api";

function ResumeTailor() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const tailorResume = async () => {
    if (!file) {
      alert("Please upload your resume.");
      return;
    }

    if (!jobDescription.trim()) {
      alert("Please paste a job description.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      formData.append("file", file);
      formData.append("job_description", jobDescription);

      const response = await api.post(
        "/resume/tailor-upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
    } catch {
      alert("Resume tailoring failed.");
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

          <div className="flex items-center gap-3 mb-5">

            <Upload className="text-blue-500" />

            <h2 className="text-2xl font-bold text-white">
              Upload Resume
            </h2>

          </div>

          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full bg-gray-800 rounded-xl p-4 text-white"
          />

          {file && (
            <p className="text-green-400 mt-4">
              {file.name}
            </p>
          )}

        </div>

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

          <div className="flex items-center gap-3 mb-5">

            <Briefcase className="text-blue-500" />

            <h2 className="text-2xl font-bold text-white">
              Job Description
            </h2>

          </div>

          <textarea
            rows={10}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description..."
            className="w-full bg-gray-800 rounded-xl border border-gray-700 p-4 text-white resize-none focus:outline-none focus:border-blue-500"
          />

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
                  {item}
                </div>
              ))}

            </div>

          </div>
        </>
      )}

    </div>
  );
}

export default ResumeTailor;
