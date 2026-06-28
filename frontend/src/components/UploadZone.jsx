import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload } from "lucide-react";

const UploadZone = ({ onUpload, isUploading, uploadProgress, onError }) => {
  const onDrop = useCallback(
    (acceptedFiles, fileRejections) => {
      if (fileRejections && fileRejections.length > 0) {
        const error = fileRejections[0].errors[0];
        let errorMsg;
        if (error.code === "file-too-large") {
          errorMsg = "File is too large. Max size is 5MB.";
        } else if (error.code === "file-invalid-type") {
          errorMsg = "Invalid file type. Only PDF, DOCX, TXT, JPG, and PNG files are allowed.";
        } else {
          errorMsg = error.message;
        }
        if (onError) onError(errorMsg);
        return;
      }
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload, onError]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"]
    },
    maxSize: 5 * 1024 * 1024,
    disabled: isUploading,
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[220px] ${
        isDragActive 
          ? "border-indigo-500 bg-indigo-950/10" 
          : isDragReject
            ? "border-rose-500 bg-rose-950/10"
            : "border-slate-800 hover:border-indigo-500/40 bg-slate-950/20"
      } ${isUploading ? "opacity-60 pointer-events-none" : ""}`}
    >
      <input {...getInputProps()} />
      
      {isUploading ? (
        <div className="w-full max-w-[200px] space-y-4 flex flex-col items-center">
          <div className="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center border border-slate-800">
            <LoadingCircle progress={uploadProgress} />
          </div>
          <div className="w-full space-y-1.5 text-center">
            <p className="text-xs font-semibold text-slate-300">
              {uploadProgress < 100 ? `Uploading: ${uploadProgress}%` : "Extracting text contents..."}
            </p>
            <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden w-full">
              <div 
                className="h-full bg-indigo-500 transition-all duration-200" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center mb-4 border border-slate-800">
            <Upload className="w-5 h-5 text-indigo-400" />
          </div>
          {isDragActive ? (
            <p className="text-sm font-semibold text-indigo-400">Drop your resume file here...</p>
          ) : (
            <>
              <p className="text-sm font-semibold text-slate-300">
                Drag & drop resume here
              </p>
              <p className="text-xs text-slate-500 mt-1">
                or click to browse from files
              </p>
            </>
          )}
          <div className="mt-4 flex flex-col items-center gap-1">
            <div className="flex gap-3 text-[10px] text-slate-500 font-semibold tracking-wider uppercase">
              <span>PDF / DOCX / TXT / JPG / PNG</span>
              <span>•</span>
              <span>Max 5MB</span>
            </div>
            <div className="mt-2 flex flex-col items-center text-[10px] text-slate-400">
              <span className="font-semibold text-slate-500">Note:</span>
              <span>• Text PDFs: first 10 pages analyzed</span>
              <span>• Scanned PDFs: first 5 pages analyzed</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Simple visual SVG circle loader representing upload percentage
const LoadingCircle = ({ progress }) => {
  const radius = 16;
  const stroke = 3;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
      <circle
        stroke="#1e293b"
        fill="transparent"
        strokeWidth={stroke}
        r={normalizedRadius}
        cx={radius}
        cy={radius}
      />
      <circle
        stroke="#6366f1"
        fill="transparent"
        strokeWidth={stroke}
        strokeDasharray={circumference + " " + circumference}
        style={{ strokeDashoffset }}
        strokeLinecap="round"
        r={normalizedRadius}
        cx={radius}
        cy={radius}
      />
    </svg>
  );
};

export default UploadZone;
