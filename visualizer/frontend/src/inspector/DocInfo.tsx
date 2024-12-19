import React from "react";
import HighlightWithinTextarea from "react-highlight-within-textarea";
import "./docinfo.css";
import { Doc, Triplet } from "@shared/types/doc";

interface HighlightedTextProps {
  text: string;
  triplets: Triplet[];
  subjectId?: string | number;
  predicateId?: string | number;
  objectId?: string | number;
}

const HighlightedText: React.FC<HighlightedTextProps> = ({
  text,
  triplets,
  subjectId,
  predicateId,
  objectId,
}) => {
  const subjects = [];
  const highlightSubjects = [];
  const predicates = [];
  const highlightPredicates = [];
  const objects = [];
  const highlightObjects = [];

  for (let triplet of triplets) {
    const subject = triplet.subject;
    const subjectSpan = [subject.start, subject.end];
    if (subject.id === subjectId) {
      highlightSubjects.push(subjectSpan);
    } else {
      subjects.push(subjectSpan);
    }
    const predicate = triplet.predicate;
    const predicateSpan = [predicate.start, predicate.end];
    if (predicate.id === predicateId) {
      highlightPredicates.push(predicateSpan);
    } else {
      predicates.push(predicateSpan);
    }
    const object = triplet.object;
    const objectSpan = [object.start, object.end];
    if (object.id === objectId) {
      highlightObjects.push(objectSpan);
    } else {
      objects.push(objectSpan);
    }
  }

  return (
    <HighlightWithinTextarea
      value={text}
      highlight={[
        {
          highlight: subjects,
          className: "subject",
        },
        {
          highlight: highlightSubjects,
          className: "highlight-subject",
        },

        {
          highlight: predicates,
          className: "predicate",
        },
        {
          highlight: highlightPredicates,
          className: "highlight-predicate",
        },
        {
          highlight: objects,
          className: "object",
        },
        {
          highlight: highlightObjects,
          className: "highlight-object",
        },
      ]}
    />
  );
};

export interface DocInfoProps {
  document: Doc;
  subjectId?: string | number;
  predicateId?: string | number;
  objectId?: string | number;
}

export const DocInfo: React.FC<DocInfoProps> = ({
  document,
  subjectId,
  predicateId,
  objectId,
}) => {
  return (
    <div
      style={{ border: "1px solid gray", padding: "2px", marginBottom: "1px" }}
    >
      <h3>
        {document.id}{" "}
        <i style={{ color: "gray" }}>{document.timestamp?.toString()}</i>
      </h3>
      <HighlightedText
        text={document.text}
        triplets={document.triplets}
        subjectId={subjectId}
        predicateId={predicateId}
        objectId={objectId}
      />
    </div>
  );
};
