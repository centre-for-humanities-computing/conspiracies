import React from "react";

interface NdjsonFileUploadComponentProps {
  onFileLoaded: (data: Generator<any, void, unknown>) => void;
}

const NdjsonFileUploadComponent: React.FC<NdjsonFileUploadComponentProps> = ({
  onFileLoaded,
}: NdjsonFileUploadComponentProps) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result;
        if (typeof text === "string") {
          // Create a generator for NDJSON parsing
          const parseNDJSON = function* (
            input: string,
          ): Generator<any, void, unknown> {
            const lines = input.split("\n");
            for (const line of lines) {
              if (line.trim()) {
                try {
                  yield JSON.parse(line);
                } catch (error) {
                  console.error("Invalid JSON line:", line, error);
                }
              }
            }
          };

          try {
            // Test if the file is a single JSON object
            JSON.parse(text); // Throws if it's not a single JSON
            alert("This file is a standard JSON file. NDJSON is expected.");
          } catch {
            // If not, assume it's NDJSON and pass the generator
            onFileLoaded(parseNDJSON(text));
          }
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

export default NdjsonFileUploadComponent;
