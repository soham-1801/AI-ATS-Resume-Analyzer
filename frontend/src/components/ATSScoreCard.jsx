

const ATSScoreCard = ({ score, title, subtitle, color = "indigo" }) => {
  const getColorClasses = () => {
    switch (color) {
      case "emerald":
        return "text-emerald-400 border-emerald-500/20 bg-emerald-950/20";
      case "rose":
        return "text-rose-400 border-rose-500/20 bg-rose-950/20";
      case "blue":
        return "text-blue-400 border-blue-500/20 bg-blue-950/20";
      default:
        return "text-indigo-400 border-indigo-500/20 bg-indigo-950/20";
    }
  };

  return (
    <div className={`border p-6 rounded-xl flex flex-col justify-center items-center text-center transition-all ${getColorClasses()}`}>
      <p className="text-xs font-semibold uppercase tracking-wider opacity-80">{title}</p>
      <h3 className="text-4xl font-extrabold mt-3">{score}%</h3>
      {subtitle && <p className="text-[10px] mt-1.5 opacity-60 leading-relaxed">{subtitle}</p>}
    </div>
  );
};

export default ATSScoreCard;
