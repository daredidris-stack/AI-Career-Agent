import { useState } from "react";
import {
  Briefcase,
  Target,
  CheckCircle,
  XCircle,
  Sparkles,
} from "lucide-react";

import api from "../services/api";

function JobMatch() {
  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!resume || !jobDescription) {
      alert("Please enter both your resume and the job description.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/jobs/match", {
        resume,
        job_description: jobDescription,
      });

      setResult(response.data);
    } catch {
      alert("Job matching failed.");
    }

    setLoading(false);
  };

  const getStatus = (score) => {
    if (score >= 85) return "Excellent Match";
    if (score >= 70) return "Good Match";
    return "Needs Improvement";
  };

  return (
    <div className="space-y-8">

      {/* Hero */}

      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 shadow-xl">

        <h1 className="text-4xl font-bold text-white">
          AI Job Match
        </h1>

        <p className="text-blue-100 mt-3 text-lg">
          Compare your resume against a job description using AI.
        </p>

      </div>

      {/* Input Section */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

          <h2 className="text-2xl font-bold text-white mb-4">
            Your Resume
          </h2>

          <textarea
            rows={12}
            value={resume}
            onChange={(e) => setResume(e.target.value)}
            placeholder="Paste your resume here..."
            className="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white resize-none focus:outline-none focus:border-blue-500"
          />

        </div>

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

          <h2 className="text-2xl font-bold text-white mb-4">
            Job Description
          </h2>

          <textarea
            rows={12}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white resize-none focus:outline-none focus:border-blue-500"
          />

        </div>

      </div>

      {/* Analyze Button */}

      <button
        onClick={analyze}
        className="bg-blue-600 hover:bg-blue-700 transition px-8 py-3 rounded-xl text-white font-semibold"
      >
        {loading ? "Analyzing..." : "Analyze Match"}
      </button>

      {/* Results */}

      {result && (
        <>

          {/* Score Cards */}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

              <div className="flex items-center gap-4">

                <Target
                  size={45}
                  className="text-blue-500"
                />

                <div>

                  <p className="text-gray-400">
                    Match Score
                  </p>

                  <h2 className="text-4xl font-bold text-white">
                    {result.match_score}%
                  </h2>

                </div>

              </div>

              <div className="mt-6 w-full bg-gray-700 rounded-full h-4">

                <div
                  className="bg-blue-500 h-4 rounded-full"
                  style={{
                    width: `${result.match_score}%`,
                  }}
                />

              </div>

              <p className="mt-4 text-blue-400 font-semibold">
                {getStatus(result.match_score)}
              </p>

            </div>

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

              <div className="flex items-center gap-4">

                <Briefcase
                  size={45}
                  className="text-green-500"
                />

                <div>

                  <p className="text-gray-400">
                    Matching Skills
                  </p>

                  <h2 className="text-4xl font-bold text-white">
                    {result.matching_skills.length}
                  </h2>

                </div>

              </div>

            </div>

          </div>

          {/* Skills */}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">

              <h2 className="text-2xl font-bold text-white mb-5">
                Matching Skills
              </h2>

              <div className="flex flex-wrap gap-3">

                {result.matching_skills.map((skill) => (
                  <span
                    key={skill}
                    className="flex items-center gap-2 bg-green-700 px-4 py-2 rounded-full text-white"
                  >
                    <CheckCircle size={16} />
                    {skill}
                  </span>
                ))}

              </div>

            </div>

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">

              <h2 className="text-2xl font-bold text-white mb-5">
                Missing Skills
              </h2>

              <div className="flex flex-wrap gap-3">

                {result.missing_skills.map((skill) => (
                  <span
                    key={skill}
                    className="flex items-center gap-2 bg-red-700 px-4 py-2 rounded-full text-white"
                  >
                    <XCircle size={16} />
                    {skill}
                  </span>
                ))}

              </div>

            </div>

          </div>

          {/* Recommendation */}

          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

            <div className="flex items-center gap-3 mb-5">

              <Sparkles
                size={28}
                className="text-yellow-400"
              />

              <h2 className="text-2xl font-bold text-white">
                AI Recommendation
              </h2>

            </div>

            <p className="text-gray-300 leading-8">
              {result.recommendation}
            </p>

          </div>

        </>
      )}

    </div>
  );
}

export default JobMatch;
