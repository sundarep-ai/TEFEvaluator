/**
 * Presentation helpers for TEF Canada expression écrite scores.
 *
 * ONE SCALE: 0–450. That is the "équivalence ancien score" column of the
 * attestation, and the only one IRCC accepts — the /699 headline the attestation
 * also carries is not entered anywhere in an Express Entry profile. The UI never
 * shows a second number, so there is nothing for a candidate to misread.
 *
 * The numbers come from the backend (`scoring.py`) so the two can never
 * disagree. Each submission carries a `scores` object:
 *   { rating, score, scoreMax, nclc, cefr, bandFloor, bandCeiling,
 *     pointsToNextLevel, expressEntryEligible, expressEntryThreshold,
 *     sectionA, sectionB }
 */

export const SCORE_MAX = 450;
/** NCLC 7 on the /450 scale — the Express Entry writing threshold. */
export const EXPRESS_ENTRY_THRESHOLD = 310;
export const EXPRESS_ENTRY_NCLC = 7;

/** Percentage of the full 0–450 scale, for gauges and progress bars. */
export function scorePct(score) {
  if (!score && score !== 0) return 0;
  return Math.max(0, Math.min(100, Math.round((score / SCORE_MAX) * 100)));
}

/**
 * Progress toward NCLC 7 rather than toward 450/450. Almost nobody needs a
 * perfect score; they need the Express Entry bar, so that is what the bar fills
 * to. Capped at 100% once the threshold is cleared.
 */
export function thresholdPct(score) {
  if (!score && score !== 0) return 0;
  return Math.max(0, Math.min(100, Math.round((score / EXPRESS_ENTRY_THRESHOLD) * 100)));
}

/** Short label + Tailwind classes for an NCLC level. */
export function nclcLabel(nclc) {
  if (nclc >= 10) return { text: `NCLC ${nclc}`, cls: 'bg-secondary/10 text-secondary' };
  if (nclc >= 8) return { text: `NCLC ${nclc}`, cls: 'bg-primary-fixed text-on-primary-fixed' };
  if (nclc === 7) return { text: 'NCLC 7', cls: 'bg-tertiary-fixed text-on-tertiary-fixed-variant' };
  if (nclc >= 4) return { text: `NCLC ${nclc}`, cls: 'bg-error-container text-on-error-container' };
  return { text: '< NCLC 4', cls: 'bg-error-container text-on-error-container' };
}

/** French status line shown next to the headline score. */
export function statusLabel(scores) {
  if (!scores || !scores.nclc) return 'En progression vers NCLC 4';
  if (scores.expressEntryEligible) {
    return `NCLC ${scores.nclc} — seuil Entrée express atteint`;
  }
  const missing = scores.pointsToNextLevel;
  return missing
    ? `NCLC ${scores.nclc} — ${missing} points pour le niveau suivant`
    : `NCLC ${scores.nclc} — en progression vers NCLC 7`;
}

/** "310–348" — the band the score sits in, so the number reads as a range. */
export function bandLabel(scores) {
  if (!scores || scores.bandFloor == null) return null;
  return `${scores.bandFloor}–${scores.bandCeiling}`;
}

/** Guards a missing `scores` object (e.g. a submission saved without ratings). */
export function safeScores(submission) {
  return (
    submission?.scores ?? {
      score: 0,
      scoreMax: SCORE_MAX,
      nclc: 0,
      cefr: '—',
      bandFloor: null,
      bandCeiling: null,
      pointsToNextLevel: null,
      expressEntryEligible: false,
      expressEntryThreshold: EXPRESS_ENTRY_THRESHOLD,
    }
  );
}
