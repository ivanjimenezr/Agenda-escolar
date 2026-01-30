/**
 * Brute Force Protection Utility
 * Protects login attempts against brute force attacks
 */

const STORAGE_KEY = 'login-attempts';
const MAX_ATTEMPTS = 5; // Maximum failed attempts before lockout
const LOCKOUT_DURATION_MS = 15 * 60 * 1000; // 15 minutes in milliseconds
const ATTEMPT_WINDOW_MS = 30 * 60 * 1000; // 30 minutes window for attempts

interface LoginAttempt {
  email: string;
  timestamp: number;
  success: boolean;
}

interface LockoutInfo {
  email: string;
  lockedUntil: number;
  failedAttempts: number;
}

/**
 * Get stored login attempts from localStorage
 */
function getStoredAttempts(): LoginAttempt[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

/**
 * Save login attempts to localStorage
 */
function saveAttempts(attempts: LoginAttempt[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(attempts));
  } catch (error) {
    console.error('Failed to save login attempts:', error);
  }
}

/**
 * Clean up old attempts (older than attempt window)
 */
function cleanupOldAttempts(attempts: LoginAttempt[]): LoginAttempt[] {
  const now = Date.now();
  return attempts.filter(
    attempt => now - attempt.timestamp < ATTEMPT_WINDOW_MS
  );
}

/**
 * Get failed attempts for a specific email within the time window
 */
function getFailedAttempts(email: string): LoginAttempt[] {
  const attempts = getStoredAttempts();
  const cleanAttempts = cleanupOldAttempts(attempts);

  return cleanAttempts.filter(
    attempt =>
      attempt.email.toLowerCase() === email.toLowerCase() &&
      !attempt.success
  );
}

/**
 * Check if an email is currently locked out
 */
export function isLockedOut(email: string): LockoutInfo | null {
  const failedAttempts = getFailedAttempts(email);

  if (failedAttempts.length < MAX_ATTEMPTS) {
    return null;
  }

  // Find the most recent failed attempt
  const mostRecentAttempt = failedAttempts.reduce((latest, current) =>
    current.timestamp > latest.timestamp ? current : latest
  );

  const lockedUntil = mostRecentAttempt.timestamp + LOCKOUT_DURATION_MS;
  const now = Date.now();

  if (now < lockedUntil) {
    return {
      email,
      lockedUntil,
      failedAttempts: failedAttempts.length
    };
  }

  // Lockout period has expired, clear old attempts
  clearAttemptsForEmail(email);
  return null;
}

/**
 * Get remaining time in lockout (in seconds)
 */
export function getRemainingLockoutTime(email: string): number {
  const lockoutInfo = isLockedOut(email);
  if (!lockoutInfo) return 0;

  const remaining = Math.ceil((lockoutInfo.lockedUntil - Date.now()) / 1000);
  return Math.max(0, remaining);
}

/**
 * Format remaining time as MM:SS
 */
export function formatLockoutTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Record a login attempt
 */
export function recordAttempt(email: string, success: boolean): void {
  let attempts = getStoredAttempts();
  attempts = cleanupOldAttempts(attempts);

  // If successful, clear all failed attempts for this email
  if (success) {
    attempts = attempts.filter(
      attempt => attempt.email.toLowerCase() !== email.toLowerCase()
    );
  }

  // Add new attempt
  attempts.push({
    email,
    timestamp: Date.now(),
    success
  });

  saveAttempts(attempts);
}

/**
 * Clear all attempts for a specific email
 */
function clearAttemptsForEmail(email: string): void {
  let attempts = getStoredAttempts();
  attempts = attempts.filter(
    attempt => attempt.email.toLowerCase() !== email.toLowerCase()
  );
  saveAttempts(attempts);
}

/**
 * Get remaining attempts before lockout
 */
export function getRemainingAttempts(email: string): number {
  const failedAttempts = getFailedAttempts(email);
  return Math.max(0, MAX_ATTEMPTS - failedAttempts.length);
}

/**
 * Calculate delay before allowing next attempt (progressive backoff)
 */
export function getAttemptDelay(email: string): number {
  const failedAttempts = getFailedAttempts(email);
  const attemptCount = failedAttempts.length;

  if (attemptCount === 0) return 0;

  // Progressive delays: 0s, 2s, 5s, 10s, 20s
  const delays = [0, 2000, 5000, 10000, 20000];
  const delayIndex = Math.min(attemptCount - 1, delays.length - 1);
  const baseDelay = delays[delayIndex];

  if (failedAttempts.length === 0) return 0;

  const lastAttempt = failedAttempts[failedAttempts.length - 1];
  const timeSinceLastAttempt = Date.now() - lastAttempt.timestamp;

  return Math.max(0, baseDelay - timeSinceLastAttempt);
}

/**
 * Check if user should wait before next attempt
 */
export function shouldWaitBeforeAttempt(email: string): boolean {
  return getAttemptDelay(email) > 0;
}

/**
 * Get security info for display
 */
export interface SecurityInfo {
  isLocked: boolean;
  lockoutTimeRemaining: number;
  lockoutTimeFormatted: string;
  remainingAttempts: number;
  attemptDelay: number;
  shouldWait: boolean;
}

export function getSecurityInfo(email: string): SecurityInfo {
  const isLocked = isLockedOut(email) !== null;
  const lockoutTimeRemaining = getRemainingLockoutTime(email);
  const remainingAttempts = getRemainingAttempts(email);
  const attemptDelay = getAttemptDelay(email);

  return {
    isLocked,
    lockoutTimeRemaining,
    lockoutTimeFormatted: formatLockoutTime(lockoutTimeRemaining),
    remainingAttempts,
    attemptDelay,
    shouldWait: shouldWaitBeforeAttempt(email)
  };
}

/**
 * Clear all login attempts (for testing or admin purposes)
 */
export function clearAllAttempts(): void {
  localStorage.removeItem(STORAGE_KEY);
}
