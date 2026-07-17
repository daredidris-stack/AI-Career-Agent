import { useState } from "react";
import {
  Upload,
  FileText,
  Award,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

import api from "../services/api";

function Resume() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!file) {
      alert("Please upload a resume.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post(
        "/resume/analyze",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
    } catch {
      alert("Resume analysis failed.");
    }

    setLoading(false);
  };

  return (
    <div className="space-y-8">

      {/* Header */}

      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 shadow-xl">

        <h1 className="text-4xl font-bold text-white">
          Resume Studio
        </h1>

        <p className="text-blue-100 mt-3 text-lg">
          Upload your resume and receive an AI-powered review,
          ATS score, strengths, and improvement suggestions.
        </p>

      </div>

      {/* Upload Card */}

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-lg">

        <div className="flex flex-col items-center justify-center">

          <Upload
            size={60}
            className="text-blue-500"
          />

          <h2 className="text-2xl font-bold text-white mt-4">
            Upload Resume
          </h2>

          <p className="text-gray-400 mt-2">
            PDF or DOCX files only
          </p>

          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files[0])}
            className="mt-6 text-white"
          />

          {file && (
            <p className="text-green-400 mt-4">
              Selected: {file.name}
            </p>
          )}

          <button
            onClick={analyze}
            className="mt-8 bg-blue-600 hover:bg-blue-700 transition px-8 py-3 rounded-xl text-white font-semibold"
          >
            {loading ? "Analyzing..." : "Analyze Resume"}
          </button>

        </div>

      </div>

      {/* Results */}

      {result && (

        <>

          {/* Score Cards */}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

              <div className="flex items-center gap-4">

                <Award
                  size={40}
                  className="text-yellow-400"
                />

                <div>

                  <p className="text-gray-400">
                    Resume Score
                  </p>

                  <h2 className="text-4xl font-bold text-white">
                    {result.resume_score}%
                  </h2>

                </div>

              </div>

            </div>

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

              <div className="flex items-center gap-4">

                <FileText
                  size={40}
                  className="text-blue-500"
                />

                <div>

                  <p className="text-gray-400">
                    ATS Score
                  </p>

                  <h2 className="text-4xl font-bold text-white">
                    {result.ats_score}%
                  </h2>

                </div>

              </div>

            </div>

          </div>

          {/* Strengths & Improvements */}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

              <h2 className="text-2xl font-bold text-white mb-6">
                Strengths
              </h2>

              <div className="space-y-4">

                {result.strengths?.map((item) => (

                  <div
                    key={item}
                    className="flex items-start gap-3"
                  >

                    <CheckCircle className="text-green-500 mt-1" />

                    <span className="text-gray-300">
                      {item}
                    </span>

                  </div>

                ))}

              </div>

            </div>

            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-lg">

              <h2 className="text-2xl font-bold text-white mb-6">
                Improvements
              </h2>

              <div className="space-y-4">

                {result.improvements?.map((item) => (

                  <div
                    key={item}
                    className="flex items-start gap-3"
                  >

                    <AlertCircle className="text-yellow-500 mt-1" />

                    <span className="text-gray-300">
                      {item}
                    </span>

                  </div>

                ))}

              </div>

            </div>

          </div>

        </>

      )}

    </div>
  );
}

export default Resume;
