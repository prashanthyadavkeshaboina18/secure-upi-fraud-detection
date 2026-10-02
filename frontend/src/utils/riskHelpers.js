import { RISK_LEVELS, DECISIONS } from './constants.js'

/**
 * Single source of truth for risk presentation.
 * The bands themselves are decided by the backend (they are configurable
 * server-side); this file only maps a level to how it looks and reads.
 */
const RISK_STYLES = {
  [RISK_LEVELS.LOW]: {
    label: 'Low risk',
    text: 'text-approved',
    bg: 'bg-approved-light',
    border: 'border-approved/25',
    stroke: '#0E7A4E',
  },
  [RISK_LEVELS.MEDIUM]: {
    label: 'Medium risk',
    text: 'text-review',
    bg: 'bg-review-light',
    border: 'border-review/25',
    stroke: '#B26A00',
  },
  [RISK_LEVELS.HIGH]: {
    label: 'High risk',
    text: 'text-blocked',
    bg: 'bg-blocked-light',
    border: 'border-blocked/25',
    stroke: '#B32B2B',
  },
}

const DECISION_STYLES = {
  [DECISIONS.APPROVED]: {
    label: 'Approved',
    text: 'text-approved',
    bg: 'bg-approved-light',
    border: 'border-approved/25',
  },
  [DECISIONS.REVIEW]: {
    label: 'Needs verification',
    text: 'text-review',
    bg: 'bg-review-light',
    border: 'border-review/25',
  },
  [DECISIONS.BLOCKED]: {
    label: 'Blocked',
    text: 'text-blocked',
    bg: 'bg-blocked-light',
    border: 'border-blocked/25',
  },
}

const FALLBACK = {
  label: 'Unknown',
  text: 'text-ink-muted',
  bg: 'bg-canvas',
  border: 'border-line',
  stroke: '#6B7789',
}

export const riskStyle = (level) => RISK_STYLES[level] || FALLBACK
export const decisionStyle = (decision) => DECISION_STYLES[decision] || FALLBACK

export function decisionHeadline(decision) {
  switch (decision) {
    case DECISIONS.APPROVED:
      return 'Payment sent'
    case DECISIONS.REVIEW:
      return 'Confirm this payment'
    case DECISIONS.BLOCKED:
      return 'Payment blocked'
    default:
      return 'Payment analysed'
  }
}

export function decisionSubline(decision) {
  switch (decision) {
    case DECISIONS.APPROVED:
      return 'Nothing unusual was found in this transaction.'
    case DECISIONS.REVIEW:
      return 'A few signals look unusual. Verify it was you before we continue.'
    case DECISIONS.BLOCKED:
      return 'We stopped this payment and raised an alert. No money left your account.'
    default:
      return ''
  }
}
