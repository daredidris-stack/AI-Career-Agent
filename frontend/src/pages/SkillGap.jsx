import { useState } from "react";
import MainLayout from "../components/layout/MainLayout";
import api from "../services/api";

function SkillGap() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const analyze = async () => {
    setLoading(true);

    try {
      const response = await api.post("/skills/analyze", {
        profile: {
          skills: ["AWS", "Linux", "Python"],
        },
        jobs: [
          {
            skills: [
              "AWS",
              "Linux",
              "Docker",
              "Kubernetes",
              "Terraform",
            ],
          },
        ],
      });

      setResult(response.data);
    } catch (err) {
      console.error(err);
      alert("Backend connection failed.");
    }

    setLoading(false);
  };

  return (
    <MainLayout>
      <h1 className="text-4xl font-bold">Skill Gap Analysis</h1>

      <button
        onClick={analyze}
        className="bg-blue-600 px-5 py-3 rounded-lg mt-6"
      >
        {loading ? "Analyzing..." : "Analyze Skills"}
      </button>

      {result && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold">Missing Skills</h2>

          <ul className="list-disc ml-6 mt-3">
            {result.missing_skills.map((skill) => (
              <li key={skill}>{skill}</li>
            ))}
          </ul>

          <h2 className="text-2xl font-bold mt-8">
            AI Recommendation
          </h2>

          <div className="bg-slate-800 p-5 rounded-lg mt-3 whitespace-pre-wrap">
            {result.recommendation}
          </div>
        </div>
      )}
    </MainLayout>
  );
}

export default SkillGap;