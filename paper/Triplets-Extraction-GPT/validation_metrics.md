## Guideline for validating and comparing prompt outputs and comparing

### avg number of extraction errors pr. extraction
Extraction errors are
- if a generated triplet does not contain exactly three elements
- output is not consistent with the given format
- if the triplet extracted are not based on the target tweet, e.g. a completely different sentence

Extraction errors are not
- wrong subject/object/predicate
- extracting extra tweets (these should just be cut out)

### is the triplet an exact substring of the tweet
- each of the elements in the triplet has en exact match in the target tweet

### does predicate contain verb

### does predicate start with verb

### overlap with gold
- ?
