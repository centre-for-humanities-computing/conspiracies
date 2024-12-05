import React from "react";
import { Doc } from "../docs/DocService";

export interface DocInfoProps {
  document: Doc;
}

export const DocInfo: React.FC<DocInfoProps> = ({ document }) => {
  return (
    <div
      style={{ border: "1px solid gray", padding: "2px", marginBottom: "1px" }}
    >
      <h3>{document.id}</h3>
      <i>{document.timestamp}</i>
      <p>{document.text}</p>
    </div>
  );
};
