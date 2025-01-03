import React from "react";

interface JsonFileUploadComponentProps {
  onFileLoaded: (data: any) => void;
}

const JsonFileUploadComponent: React.FC<JsonFileUploadComponentProps> = ({
  onFileLoaded,
}: JsonFileUploadComponentProps) => {
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

export default JsonFileUploadComponent;
