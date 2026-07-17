import { useState } from "react";
import {
  Sparkles,
  FileText,
  Briefcase,
  Copy,
  CheckCircle,
} from "lucide-react";

import api from "../services/api";


function CoverLetter() {

  const [resume, setResume] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [letter, setLetter] = useState("");
  const [copied, setCopied] = useState(false);



  const generate = async () => {

    if (!resume || !jobDescription) {
      alert("Please enter your resume and job description.");
      return;
    }


    setLoading(true);


    try {

      const response = await api.post(
        "/cover-letter",
        {
          resume,
          job_description: jobDescription,
        }
      );


      setLetter(response.data.cover_letter);


    } catch(error){

      console.error(error);

      alert("Failed to generate cover letter.");

    }


    setLoading(false);

  };



  const copyLetter = async () => {

    await navigator.clipboard.writeText(letter);

    setCopied(true);


    setTimeout(() => {
      setCopied(false);
    },2000);

  };



  return (

    <div className="space-y-8">


      {/* Hero */}

      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 shadow-xl">

        <h1 className="text-4xl font-bold text-white">
          AI Cover Letter Generator
        </h1>


        <p className="text-blue-100 mt-3 text-lg">
          Create personalized cover letters tailored to your target job.
        </p>

      </div>




      {/* Inputs */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">


        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">


          <div className="flex items-center gap-3 mb-5">

            <FileText
              className="text-blue-500"
            />

            <h2 className="text-2xl font-bold text-white">
              Your Resume
            </h2>

          </div>


          <textarea

            rows="12"

            className="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white resize-none focus:outline-none focus:border-blue-500"

            placeholder="Paste your resume..."

            value={resume}

            onChange={(e)=>setResume(e.target.value)}

          />


        </div>





        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">


          <div className="flex items-center gap-3 mb-5">

            <Briefcase
              className="text-blue-500"
            />


            <h2 className="text-2xl font-bold text-white">
              Job Description
            </h2>


          </div>



          <textarea

            rows="12"

            className="w-full bg-gray-800 border border-gray-700 rounded-xl p-4 text-white resize-none focus:outline-none focus:border-blue-500"

            placeholder="Paste the job description..."

            value={jobDescription}

            onChange={(e)=>setJobDescription(e.target.value)}

          />



        </div>


      </div>





      {/* Button */}


      <button

        onClick={generate}

        className="bg-blue-600 hover:bg-blue-700 transition px-8 py-3 rounded-xl text-white font-semibold"

      >

        {loading
          ? "Generating..."
          : "Generate Cover Letter"
        }


      </button>





      {/* Result */}


      {letter && (

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-lg">


          <div className="flex justify-between items-center">


            <div className="flex items-center gap-3">


              <Sparkles
                className="text-yellow-400"
              />


              <h2 className="text-2xl font-bold text-white">

                AI Generated Cover Letter

              </h2>


            </div>





            <button

              onClick={copyLetter}

              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-white"

            >

              {
                copied
                ?
                <>
                  <CheckCircle size={18}/>
                  Copied
                </>
                :
                <>
                  <Copy size={18}/>
                  Copy
                </>
              }


            </button>


          </div>





          <div className="mt-6 bg-gray-800 rounded-xl p-6">


            <p className="text-gray-300 whitespace-pre-wrap leading-8">

              {letter}

            </p>


          </div>



        </div>


      )}



    </div>

  );

}


export default CoverLetter;