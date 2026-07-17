import { useEffect, useState } from "react";

import {
  Briefcase,
  FileText,
  Target,
  TrendingUp,
  Award,
  CheckCircle,
} from "lucide-react";

import DashboardCard from "../components/cards/DashboardCard";
import CareerAnalytics from "../components/charts/CareerAnalytics";
import api from "../services/api";


function Dashboard() {

  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);


  useEffect(() => {

    async function fetchDashboard() {

      try {

        setError("");

        const response = await api.get("/dashboard");

        setData(response.data);


      } catch {

        setError(
          "Dashboard could not be loaded. Please try again.",
        );

      }

    }


    fetchDashboard();


  }, [reloadKey]);



  if (!data) {

    if (error) {

      return (

        <div className="flex h-screen flex-col items-center justify-center gap-4 text-white">

          <p className="text-xl font-semibold">
            {error}
          </p>

          <button
            type="button"
            onClick={() => setReloadKey((value) => value + 1)}
            className="rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-700"
          >
            Retry
          </button>

        </div>

      );

    }

    return (

      <div className="flex items-center justify-center h-screen">

        <h1 className="text-3xl font-bold text-white">
          Loading Dashboard...
        </h1>

      </div>

    );

  }



  return (

    <div className="space-y-8">


      {/* Hero */}

      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 shadow-xl">

        <h1 className="text-4xl font-bold text-white">

          Welcome to NextHire AI  👋

        </h1>


        <p className="text-blue-100 mt-3 text-lg">

          Your AI-powered career platform for job matching, resume optimization, and professional growth.

        </p>


      </div>





      {/* Cards */}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">


        <DashboardCard

          title="Missing Skills"

          value={data.skill_gap}

          icon={<Briefcase size={28}/>}

        />



        <DashboardCard

          title="Resume Score"

          value={
            data.resume_score == null
              ? "Not scored"
              : `${data.resume_score}%`
          }

          icon={<FileText size={28}/>}

        />



        <DashboardCard

          title="Jobs Available"

          value={data.jobs_available}

          icon={<Target size={28}/>}

        />



        <DashboardCard

          title="Career Progress"

          value={`${data.career_progress}%`}

          icon={<TrendingUp size={28}/>}

        />

        <DashboardCard

          title="ATS Score"

          value={
            data.ats_score == null
              ? "Not scored"
              : `${data.ats_score}%`
          }

          icon={<Award size={28}/>}

        />


        <DashboardCard

          title="Skills Completed"

          value={data.skills_completed}

          icon={<CheckCircle size={28}/>}

        />


      </div>






      {/* Progress + Skill */}


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">



        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">


          <h2 className="text-2xl font-bold text-white">

            Career Progress

          </h2>



          <p className="text-gray-400 mt-2">

            Progress toward becoming a {data.profile.target_role || "stronger candidate"}.

          </p>




          <div className="mt-8 w-full bg-gray-700 rounded-full h-5">


            <div

              className="bg-blue-500 h-5 rounded-full"

              style={{
                width:`${data.career_progress}%`
              }}

            ></div>


          </div>



          <p className="mt-3 text-right text-blue-400 font-bold">

            {data.career_progress}%

          </p>


        </div>







        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">


          <h2 className="text-2xl font-bold text-white">

            Recommended Next Skill

          </h2>



          <div className="flex items-center gap-4 mt-8">


            <Award

              size={50}

              className="text-yellow-400"

            />



            <div>


              <h3 className="text-xl font-bold text-white">

                {data.recommended_skill.name}

              </h3>



              <p className="text-gray-400">

                {data.recommended_skill.description}

              </p>


            </div>


          </div>


        </div>


      </div>







      {/* Activity */}


      {data.recent_activity.length > 0 && (
        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">


        <h2 className="text-2xl font-bold text-white mb-6">

          Recent AI Activity

        </h2>



        <div className="space-y-4">


          {data.recent_activity.map((item,index)=>(


            <div

              key={index}

              className="flex items-center gap-3"

            >


              <CheckCircle

                className="text-green-500"

              />


              <span className="text-white">

                {item}

              </span>


            </div>


          ))}



        </div>


        </div>
      )}






      {/* Analytics */}


      {data.weekly_progress.length > 0 && (
        <CareerAnalytics progress={data.weekly_progress} />
      )}





    </div>

  );

}



export default Dashboard;
