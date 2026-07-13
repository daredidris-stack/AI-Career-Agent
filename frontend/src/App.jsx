import { Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import SkillGap from "./pages/SkillGap";
import Resume from "./pages/Resume";
import Jobs from "./pages/Jobs";
import Interview from "./pages/Interview";
import Learning from "./pages/Learning";
import Settings from "./pages/Settings";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/skill-gap" element={<SkillGap />} />
      <Route path="/resume" element={<Resume />} />
      <Route path="/jobs" element={<Jobs />} />
      <Route path="/interview" element={<Interview />} />
      <Route path="/learning" element={<Learning />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  );
}

export default App;