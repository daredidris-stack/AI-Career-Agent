import MainLayout from "../components/layout/MainLayout";

function Resume() {
  return (
    <MainLayout>
      <h1 className="text-4xl font-bold">Resume Analyzer</h1>

      <p className="text-gray-400 mt-2">
        Upload and analyze your resume.
      </p>
    </MainLayout>
  );
}

export default Resume;