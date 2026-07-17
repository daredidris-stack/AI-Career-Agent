import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";


function CareerAnalytics({ progress }) {


  const formattedData = progress.map((item) => ({
    week: item.week.replace("Week3", "Week 3"),
    score: Number(item.score),
  }));


  return (

    <div className="bg-gray-900 rounded-2xl p-6 shadow-lg border border-gray-800">


      <h2 className="text-2xl font-bold text-white mb-4">
        Career Analytics
      </h2>


      <p className="text-gray-400 mb-6">
        Resume and ATS improvement progress over time.
      </p>


      <div className="w-full h-[300px]">


        <ResponsiveContainer
          width="100%"
          height="100%"
        >


          <LineChart
            data={formattedData}
            margin={{
              top:20,
              right:30,
              left:10,
              bottom:20
            }}
          >


            <CartesianGrid
              strokeDasharray="3 3"
            />


            <XAxis
              dataKey="week"
              stroke="#9CA3AF"
            />


            <YAxis
              domain={[0,100]}
              stroke="#9CA3AF"
            />


            <Tooltip />


            <Line
              type="monotone"
              dataKey="score"
              stroke="#3B82F6"
              strokeWidth={4}
              dot={{r:6}}
              activeDot={{r:8}}
            />


          </LineChart>


        </ResponsiveContainer>


      </div>


    </div>

  );

}


export default CareerAnalytics;