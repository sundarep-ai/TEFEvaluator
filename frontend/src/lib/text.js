/**
 * Word counting for French text.
 *
 * The previous implementation used /\b\w+\b/g. In JavaScript `\w` is
 * [A-Za-z0-9_] unless the `u` flag is set, so every accented character acted as
 * a word boundary: "élève" matched "l" and "ve" and counted as TWO words.
 * Real French prose was over-counted substantially, so the 80/200-word minimum
 * gates unlocked long before the candidate had actually written enough.
 *
 * The Unicode-aware pattern below counts letters (any script), digits, and
 * words joined by an apostrophe or hyphen, matching how the backend's
 * str.split() behaves closely enough for the counters to agree.
 */
const WORD_RE = /[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu;

export function countWords(text) {
  if (!text) return 0;
  return (text.match(WORD_RE) || []).length;
}
