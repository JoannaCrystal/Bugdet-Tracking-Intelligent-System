import { useCallback, useState } from "react";
import { Upload, FileText, X } from "lucide-react";
import { cn } from "../../lib/utils";

interface FileUploadBoxProps {
  onFileSelect?: (file: File) => void;
  onUpload?: (file: File) => void;
  accept?: string;
  disabled?: boolean;
}

export function FileUploadBox({
  onFileSelect,
  onUpload,
  accept = ".csv",
  disabled = false,
}: FileUploadBoxProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      const f = e.dataTransfer.files[0];
      if (f?.name.toLowerCase().endsWith(".csv")) {
        setFile(f);
        (onUpload ?? onFileSelect)?.(f);
      }
    },
    [disabled, onUpload, onFileSelect]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled) setIsDragging(true);
    },
    [disabled]
  );

  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      (onUpload ?? onFileSelect)?.(f);
    }
  };

  const clear = () => {
    setFile(null);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={cn(
        "relative rounded-xl border-2 border-dashed p-8 text-center transition-colors",
        isDragging ? "border-teal-400 bg-teal-50/50" : "border-slate-200 bg-slate-50/50",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleChange}
        disabled={disabled}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      {file ? (
        <div className="flex items-center justify-center gap-2">
          <FileText className="h-5 w-5 text-teal-600" />
          <span className="font-medium text-slate-700">{file.name}</span>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              clear();
            }}
            className="p-1 rounded hover:bg-slate-200"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <>
          <Upload className="h-10 w-10 mx-auto mb-3 text-slate-400" />
          <p className="text-sm text-slate-600">Drag & drop CSV or click to browse</p>
        </>
      )}
    </div>
  );
}
