import ScrollStack, { ScrollStackItem } from "./ScrollStack";

export default function ContinueLearning() {
  const tasks = [
    {
      label: "Today",
      subject: "Computer Science",
      topic: "Data Structures: Trees & Graphs",
      status: "In Progress",
      highlight: true,
    },
    {
      label: "Yesterday",
      subject: "Mathematics",
      topic: "Linear Algebra: Eigenvalues",
      status: "Not Started",
    },
    {
      label: "2 days ago",
      subject: "Physics",
      topic: "Quantum Mechanics Basics",
      status: "Completed",
    },
    {
      label: "3 days ago",
      subject: "Chemistry",
      topic: "Organic Synthesis: Alkenes",
      status: "Not Started",
    },
    {
      label: "Last week",
      subject: "Biology",
      topic: "Cellular Respiration",
      status: "Completed",
    },
  ];

  const getStatusStyle = (status: string) => {
    if (status === "In Progress")
      return "bg-blue-500/20 text-blue-400";
    if (status === "Completed")
      return "bg-green-500/20 text-green-400";
    return "bg-neutral-600/20 text-neutral-300";
  };

  return (
    <div className="h-full w-full bg-neutral-900 rounded-2xl p-4 flex flex-col">
      
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-white text-lg font-semibold">
          Continue Learning
        </h2>
        <p className="text-neutral-400 text-sm">
          Timeline of your study tasks
        </p>
      </div>

      {/* Stack */}
      <div className="flex-1 overflow-hidden">
        <ScrollStack
          className="h-full"
          itemScale={0}
          rotationAmount={0}
          blurAmount={0}
          baseScale={1}
          itemStackDistance={20}
          itemDistance={80}
        >
          {tasks.map((task, index) => (
            <ScrollStackItem
              key={index}
              itemClassName={`
                bg-neutral-800 text-white rounded-2xl p-5
                border ${task.highlight ? "border-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.3)]" : "border-neutral-700"}
                shadow-lg
              `}
            >
              <p
                className={`text-xs ${
                  task.highlight ? "text-blue-400" : "text-neutral-400"
                }`}
              >
                {task.label} • {task.subject}
              </p>

              <h3 className="text-lg font-semibold mt-1">
                {task.topic}
              </h3>

              <span
                className={`inline-block mt-3 text-xs px-2 py-1 rounded-full ${getStatusStyle(
                  task.status
                )}`}
              >
                {task.status}
              </span>
            </ScrollStackItem>
          ))}
        </ScrollStack>
      </div>
    </div>
  );
}
