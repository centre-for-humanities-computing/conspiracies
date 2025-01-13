import React, { useMemo, useState } from "react";
import HighlightWithinTextarea from "react-highlight-within-textarea";
import "./docinfo.css";
import { Doc, Triplet, TripletField } from "@shared/types/doc";

function subtractOffsetFromTripletField(
  tripletField: TripletField,
  offset: number,
): TripletField {
  return {
    ...tripletField,
    start: tripletField.start - offset,
    end: tripletField.end - offset,
  };
}

function subtractOffsetFromTriplet(triplet: Triplet, offset: number): Triplet {
  return {
    ...triplet,
    subject: subtractOffsetFromTripletField(triplet.subject, offset),
    predicate: subtractOffsetFromTripletField(triplet.predicate, offset),
    object: subtractOffsetFromTripletField(triplet.object, offset),
  };
}

function createExcerpt(
  document: Doc,
  subjectId?: string | number,
  predicateId?: string | number,
  objectId?: string | number,
  minCutText: number = 200,
): Doc {
  const triplets = document.triplets.filter(
    (t) =>
      t.subject.id === subjectId ||
      t.predicate.id === predicateId ||
      t.object.id === objectId,
  );
  let offset = Math.max(
    0,
    Math.min(...triplets.map((t) => t.subject.start)) - 100,
  );
  if (offset < minCutText) {
    offset = 0;
  }

  let tail = Math.min(
    document.text.length,
    Math.max(...triplets.map((t) => t.object.end)) + 100,
  );
  if (document.text.length - tail < minCutText) {
    tail = document.text.length;
  }

  return {
    ...document,
    text:
      (offset > 0 ? "... " : "") +
      document.text.slice(
        offset + (offset > 0 ? 4 : 0),
        tail - (tail < document.text.length ? 4 : 0),
      ) +
      (tail < document.text.length ? " ..." : ""),
    triplets: document.triplets.map((t) =>
      subtractOffsetFromTriplet(t, offset),
    ),
  };
}

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
  const [showExcerpt, setShowExcerpt] = useState<boolean>(
    [subjectId, predicateId, objectId].some((i) => i !== undefined),
  );

  const excerpt = useMemo<Doc>(
    () => createExcerpt(document, subjectId, predicateId, objectId),
    [document, objectId, predicateId, subjectId],
  );

  return (
    <div className={"panel__sub-panel"}>
      <h3>
        {document.id}{" "}
        <i style={{ color: "gray" }}>{document.timestamp?.toString()}</i>
      </h3>

      <HighlightedText
        text={showExcerpt ? excerpt.text : document.text}
        triplets={showExcerpt ? excerpt.triplets : document.triplets}
        subjectId={subjectId}
        predicateId={predicateId}
        objectId={objectId}
      />
      <br />
      {document.text !== excerpt.text && (
        <button onClick={() => setShowExcerpt((prevState) => !prevState)}>
          {showExcerpt ? "Show more" : "Show less"}
        </button>
      )}
    </div>
  );
};
