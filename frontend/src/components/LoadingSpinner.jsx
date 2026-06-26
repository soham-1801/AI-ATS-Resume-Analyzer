

const LoadingSpinner = ({ size = "md", color = "indigo" }) => {
  const getSizeClass = () => {
    switch (size) {
      case "sm":
        return "w-4 h-4 border-2";
      case "lg":
        return "w-12 h-12 border-4";
      default:
        return "w-8 h-8 border-3";
    }
  };

  const getColorClass = () => {
    switch (color) {
      case "emerald":
        return "border-emerald-500";
      case "rose":
        return "border-rose-500";
      default:
        return "border-indigo-500";
    }
  };

  return (
    <div className="flex items-center justify-center p-4">
      <div 
        className={`border-t-transparent rounded-full animate-spin ${getSizeClass()} ${getColorClass()}`} 
      />
    </div>
  );
};

export default LoadingSpinner;
