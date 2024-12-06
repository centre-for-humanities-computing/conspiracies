import React, { PropsWithChildren } from "react";
import { Doc, Triplet } from "../docs/DocService";
import HighlightWithinTextarea from "react-highlight-within-textarea";
import "./docinfo.css";

const BlueHighlight: React.FC<PropsWithChildren> = (props) => {
  return (
    <mark style={{ background: "lightblue", opacity: 0.5 }}>
      {props.children}
    </mark>
  );
};

const GreenHighlight: React.FC<PropsWithChildren> = (props) => {
  return (
    <mark style={{ background: "lightgreen", opacity: 0.5 }}>
      {props.children}
    </mark>
  );
};

const RedHighlight: React.FC<PropsWithChildren> = (props) => {
  return (
    <mark style={{ background: "pink", opacity: 0.5 }}>{props.children}</mark>
  );
};

interface HighlightedTextProps {
  text: string;
  triplets: Triplet[];
  highlightLabels: string[];
}

const HighlightedText: React.FC<HighlightedTextProps> = ({
  text,
  triplets,
  highlightLabels,
}) => {
  const subjects = [];
  const highlightSubjects = [];
  const predicates = [];
  const highlightPredicates = [];
  const objects = [];
  const highlightObjects = [];

  for (let triplet of triplets) {
    const subject = triplet.subject;
    const subjectSpan = [subject.start_char, subject.end_char];
    if (highlightLabels.indexOf(subject.text) > -1) {
      highlightSubjects.push(subjectSpan);
    } else {
      subjects.push(subjectSpan);
    }
    const predicate = triplet.predicate;
    const predicateSpan = [predicate.start_char, predicate.end_char];
    if (highlightLabels.indexOf(predicate.text) > -1) {
      highlightPredicates.push(predicateSpan);
    } else {
      predicates.push(predicateSpan);
    }
    const object = triplet.object;
    const objectSpan = [object.start_char, object.end_char];
    if (highlightLabels.indexOf(object.text) > -1) {
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
  highlightLabels: string[];
}

export const DocInfo: React.FC<DocInfoProps> = ({
  document,
  highlightLabels,
}) => {
  return (
    <div
      style={{ border: "1px solid gray", padding: "2px", marginBottom: "1px" }}
    >
      <h3>
        {document.id} <i style={{ color: "gray" }}>{document.timestamp}</i>
      </h3>
      <HighlightedText
        text={document.text}
        triplets={document.semantic_triplets}
        highlightLabels={highlightLabels}
      />
    </div>
  );
};
