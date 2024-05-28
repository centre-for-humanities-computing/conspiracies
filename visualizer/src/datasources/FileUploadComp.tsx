import React from "react";

interface FileUploadComponentProps {
  onFileLoaded: (data: any ) => void;
}

const FileUploadComponent: React.FC<FileUploadComponentProps> = ({
  onFileLoaded,
}: FileUploadComponentProps) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result;
        if (typeof text === "string") {
          const data = JSON.parse(text);
          onFileLoaded(data);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
    </div>
  );
};

export default FileUploadComponent;
