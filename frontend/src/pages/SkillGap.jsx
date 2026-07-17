import { useState } from "react";
import { CheckCircle, AlertTriangle, Sparkles } from "lucide-react";
import api from "../services/api";

function SkillGap() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const analyze = async () => {
    setLoading(true);

    try {
      const response = await api.post("/skills/analyze");

      setResult(response.data);
    } catch {
      alert("Unable to analyze skills.");
    }

    setLoading(false);
  };

  return (
    <div className="space-y-8 p-8 text-white">

      <div>
        <h1 className="text-4xl font-bold">
          Skill Gap Analysis
        </h1>

        <p className="text-gray-400 mt-2">
          Discover missing skills and receive AI-powered recommendations.
        </p>
      </div>

      <button
        onClick={analyze}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 transition px-6 py-3 rounded-xl text-white font-semibold"
      >
        {loading ? "Analyzing..." : "Analyze Skills"}
      </button>

      {result && (
        <div className="grid lg:grid-cols-3 gap-6">

          {/* Current Skills */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg">

            <div className="flex items-center gap-3 mb-5">
              <CheckCircle className="text-green-500" size={28} />
              <h2 className="text-xl font-bold">
                Current Skills
              </h2>
            </div>

            <div className="flex flex-wrap gap-3">
              {result.current_skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-green-600 px-4 py-2 rounded-full text-white font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>

          </div>

          {/* Missing Skills */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-lg">

            <div className="flex items-center gap-3 mb-5">
              <AlertTriangle className="text-yellow-400" size={28} />
              <h2 className="text-xl font-bold">
                Missing Skills
              </h2>
            </div>

            <div className="flex flex-wrap gap-3">
              {result.missing_skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-red-600 px-4 py-2 rounded-full text-white font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>

          </div>

          {/* AI Recommendation */}
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 shadow-xl">

            <div className="flex items-center gap-3 mb-5">
              <Sparkles className="text-yellow-300" size={28} />
              <h2 className="text-xl font-bold">
                AI Recommendation
              </h2>
            </div>

            <p className="text-blue-100 leading-8">
              {result.recommendation}
            </p>

          </div>

        </div>
      )}

    </div>
  );
}

export default SkillGap;
