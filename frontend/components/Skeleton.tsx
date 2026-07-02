import React from "react";

export const Skeleton: React.FC<{ rows?: number }> = ({ rows = 3 }) => {
  return (
    <div className="animate-pulse space-y-4 my-6">
      <div className="h-6 bg-slate-200 rounded w-1/3"></div>
      {Array.from({ length: rows }).map((_, idx) => (
        <div key={idx} className="p-4 bg-white rounded-lg border border-slate-200 space-y-3 shadow-xs">
          <div className="h-4 bg-slate-200 rounded w-2/3"></div>
          <div className="h-3 bg-slate-200 rounded w-full"></div>
          <div className="h-3 bg-slate-200 rounded w-4/5"></div>
        </div>
      ))}
    </div>
  );
};
