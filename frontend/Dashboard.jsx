import MainLayout from "../components/layout/MainLayout";
import DashboardCard from "../components/cards/DashboardCard";

function Dashboard() {
  return (
    <MainLayout>
      <h1 className="text-4xl font-bold">Dashboard</h1>

      <p className="text-gray-400 mt-2">
        Welcome back! Here's your AI career overview.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
        <DashboardCard title="Skill Gap" value="3 Skills" />
        <DashboardCard title="Resume Score" value="82%" />
        <DashboardCard title="Job Matches" value="15" />
      </div>
    </MainLayout>
  );
}

export default Dashboard;