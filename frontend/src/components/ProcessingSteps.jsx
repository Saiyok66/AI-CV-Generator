const STEP_NAMES = [
  "Understanding input",
  "Structuring data",
  "Optimizing for ATS",
  "Formatting CV",
  "Generating PDF",
];

export default function ProcessingSteps({ steps, generating }) {
  return (
    <div className="flex justify-center my-4">
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6 w-full max-w-md">
        <h3 className="text-white font-semibold mb-4 text-center">
          Processing Your CV
        </h3>
        <div className="space-y-3">
          {STEP_NAMES.map((name, i) => {
            const completed = steps.some((s) => s.index >= i);
            const active = generating && steps.length === i;

            return (
              <div key={i} className="flex items-center gap-3">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-500 ${
                    completed
                      ? "bg-green-500"
                      : active
                        ? "bg-blue-500 animate-pulse"
                        : "bg-white/10"
                  }`}
                >
                  {completed ? (
                    <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : active ? (
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  ) : (
                    <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                  )}
                </div>
                <span
                  className={`text-sm transition-all duration-500 ${
                    completed
                      ? "text-green-400"
                      : active
                        ? "text-blue-400 font-medium"
                        : "text-gray-500"
                  }`}
                >
                  {name}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
