function DashboardCard({ title, value, icon, loading = false }) {
  if (loading) {
    return (
      <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-lg hover:border-blue-500 transition-all duration-300 animate-pulse">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-gray-400 uppercase text-sm">
              Loading...
            </p>
            <h2 className="text-4xl font-bold text-white mt-3">
              --
            </h2>
          </div>
          <div className="bg-blue-600/20 text-blue-400 p-4 rounded-xl">
            {/* Icon placeholder */}
            <div className="h-8 w-8 bg-blue-500 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-lg hover:border-blue-500 transition-all duration-300">

      <div className="flex justify-between items-center">

        <div>

          <p className="text-gray-400 uppercase text-sm">
            {title}
          </p>

          <h2 className="text-4xl font-bold text-white mt-3">
            {value}
          </h2>

        </div>

        <div className="bg-blue-600/20 text-blue-400 p-4 rounded-xl">
          {icon}
        </div>

      </div>

    </div>
  );
}

export default DashboardCard;
