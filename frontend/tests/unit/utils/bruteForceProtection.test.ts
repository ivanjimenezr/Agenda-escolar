import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  isLockedOut,
  getRemainingLockoutTime,
  formatLockoutTime,
  recordAttempt,
  getRemainingAttempts,
  getAttemptDelay,
  shouldWaitBeforeAttempt,
  getSecurityInfo,
  clearAllAttempts,
} from '../../../utils/bruteForceProtection';

const STORAGE_KEY = 'login-attempts';
const NOW = new Date('2026-02-10T10:00:00Z').getTime();

function setStoredAttempts(attempts: Array<{ email: string; timestamp: number; success: boolean }>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(attempts));
}

function makeFailedAttempts(email: string, count: number, baseTime = NOW) {
  return Array.from({ length: count }, (_, i) => ({
    email,
    timestamp: baseTime - (count - 1 - i) * 1000,
    success: false,
  }));
}

describe('bruteForceProtection', () => {
  let localStorageData: Record<string, string>;

  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-02-10T10:00:00Z'));

    localStorageData = {};
    const localStorageMock = {
      getItem: vi.fn((key: string) => localStorageData[key] ?? null),
      setItem: vi.fn((key: string, value: string) => { localStorageData[key] = value; }),
      removeItem: vi.fn((key: string) => { delete localStorageData[key]; }),
      clear: vi.fn(() => { localStorageData = {}; }),
    };
    global.localStorage = localStorageMock as any;
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('isLockedOut', () => {
    it('should return null when no attempts exist', () => {
      expect(isLockedOut('test@example.com')).toBeNull();
    });

    it('should return null when fewer than 5 failed attempts', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 4));
      expect(isLockedOut('test@example.com')).toBeNull();
    });

    it('should return lockout info when 5 or more failed attempts', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 5));
      const result = isLockedOut('test@example.com');
      expect(result).not.toBeNull();
      expect(result!.email).toBe('test@example.com');
      expect(result!.failedAttempts).toBe(5);
      expect(result!.lockedUntil).toBeGreaterThan(NOW);
    });

    it('should return null when lockout period has expired', () => {
      const oldTime = NOW - 20 * 60 * 1000; // 20 min ago
      setStoredAttempts(makeFailedAttempts('test@example.com', 5, oldTime));
      expect(isLockedOut('test@example.com')).toBeNull();
    });

    it('should be case-insensitive for email matching', () => {
      setStoredAttempts(makeFailedAttempts('Test@Example.COM', 5));
      const result = isLockedOut('test@example.com');
      expect(result).not.toBeNull();
    });

    it('should not count attempts from other emails', () => {
      setStoredAttempts([
        ...makeFailedAttempts('other@example.com', 5),
        ...makeFailedAttempts('test@example.com', 2),
      ]);
      expect(isLockedOut('test@example.com')).toBeNull();
    });
  });

  describe('recordAttempt', () => {
    it('should record a failed attempt', () => {
      recordAttempt('test@example.com', false);
      const stored = JSON.parse(localStorageData[STORAGE_KEY]);
      expect(stored).toHaveLength(1);
      expect(stored[0].success).toBe(false);
    });

    it('should clear all failed attempts on successful login', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 3));
      recordAttempt('test@example.com', true);
      const stored = JSON.parse(localStorageData[STORAGE_KEY]);
      // Only the successful attempt should remain
      expect(stored).toHaveLength(1);
      expect(stored[0].success).toBe(true);
    });

    it('should clean up old attempts beyond 30-minute window', () => {
      const oldTime = NOW - 35 * 60 * 1000; // 35 min ago
      setStoredAttempts(makeFailedAttempts('test@example.com', 3, oldTime));
      recordAttempt('test@example.com', false);
      const stored = JSON.parse(localStorageData[STORAGE_KEY]);
      // Old attempts should be cleaned, only new one remains
      expect(stored).toHaveLength(1);
    });
  });

  describe('getRemainingAttempts', () => {
    it('should return 5 when no failed attempts', () => {
      expect(getRemainingAttempts('test@example.com')).toBe(5);
    });

    it('should decrease with each failed attempt', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 3));
      expect(getRemainingAttempts('test@example.com')).toBe(2);
    });

    it('should return 0 when at max attempts', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 5));
      expect(getRemainingAttempts('test@example.com')).toBe(0);
    });

    it('should return 0 when over max attempts', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 7));
      expect(getRemainingAttempts('test@example.com')).toBe(0);
    });
  });

  describe('getAttemptDelay', () => {
    it('should return 0 when no failed attempts', () => {
      expect(getAttemptDelay('test@example.com')).toBe(0);
    });

    it('should return progressive delays based on attempt count', () => {
      // 1 failed attempt -> delay[0] = 0ms
      const oneAttempt = makeFailedAttempts('test@example.com', 1);
      setStoredAttempts(oneAttempt);
      expect(getAttemptDelay('test@example.com')).toBe(0);

      // 2 failed attempts -> delay[1] = 2000ms
      const twoAttempts = makeFailedAttempts('test@example.com', 2);
      setStoredAttempts(twoAttempts);
      expect(getAttemptDelay('test@example.com')).toBe(2000);

      // 3 failed attempts -> delay[2] = 5000ms
      const threeAttempts = makeFailedAttempts('test@example.com', 3);
      setStoredAttempts(threeAttempts);
      expect(getAttemptDelay('test@example.com')).toBe(5000);

      // 4 failed attempts -> delay[3] = 10000ms
      const fourAttempts = makeFailedAttempts('test@example.com', 4);
      setStoredAttempts(fourAttempts);
      expect(getAttemptDelay('test@example.com')).toBe(10000);

      // 5 failed attempts -> delay[4] = 20000ms
      const fiveAttempts = makeFailedAttempts('test@example.com', 5);
      setStoredAttempts(fiveAttempts);
      expect(getAttemptDelay('test@example.com')).toBe(20000);
    });

    it('should reduce delay by time already elapsed since last attempt', () => {
      // 2 failed attempts, last one 1 second ago -> delay = 2000 - 1000 = 1000
      const attempts = [
        { email: 'test@example.com', timestamp: NOW - 5000, success: false },
        { email: 'test@example.com', timestamp: NOW - 1000, success: false },
      ];
      setStoredAttempts(attempts);
      expect(getAttemptDelay('test@example.com')).toBe(1000);
    });

    it('should return 0 when enough time has passed', () => {
      // 2 failed attempts, last one 3 seconds ago -> delay = max(0, 2000-3000) = 0
      const attempts = [
        { email: 'test@example.com', timestamp: NOW - 5000, success: false },
        { email: 'test@example.com', timestamp: NOW - 3000, success: false },
      ];
      setStoredAttempts(attempts);
      expect(getAttemptDelay('test@example.com')).toBe(0);
    });
  });

  describe('shouldWaitBeforeAttempt', () => {
    it('should return false when no delay needed', () => {
      expect(shouldWaitBeforeAttempt('test@example.com')).toBe(false);
    });

    it('should return true when delay is needed', () => {
      // 2 attempts, last one just now
      const attempts = [
        { email: 'test@example.com', timestamp: NOW - 1000, success: false },
        { email: 'test@example.com', timestamp: NOW, success: false },
      ];
      setStoredAttempts(attempts);
      expect(shouldWaitBeforeAttempt('test@example.com')).toBe(true);
    });
  });

  describe('formatLockoutTime', () => {
    it('should format seconds as MM:SS', () => {
      expect(formatLockoutTime(0)).toBe('0:00');
      expect(formatLockoutTime(5)).toBe('0:05');
      expect(formatLockoutTime(60)).toBe('1:00');
      expect(formatLockoutTime(90)).toBe('1:30');
      expect(formatLockoutTime(600)).toBe('10:00');
      expect(formatLockoutTime(900)).toBe('15:00');
    });
  });

  describe('getRemainingLockoutTime', () => {
    it('should return 0 when not locked out', () => {
      expect(getRemainingLockoutTime('test@example.com')).toBe(0);
    });

    it('should return remaining seconds when locked out', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 5));
      const remaining = getRemainingLockoutTime('test@example.com');
      // Lockout is 15 min = 900 seconds. Last attempt is at NOW, so remaining ~900
      expect(remaining).toBeGreaterThan(0);
      expect(remaining).toBeLessThanOrEqual(900);
    });
  });

  describe('getSecurityInfo', () => {
    it('should return full security info for unlocked email', () => {
      const info = getSecurityInfo('test@example.com');
      expect(info.isLocked).toBe(false);
      expect(info.lockoutTimeRemaining).toBe(0);
      expect(info.lockoutTimeFormatted).toBe('0:00');
      expect(info.remainingAttempts).toBe(5);
      expect(info.attemptDelay).toBe(0);
      expect(info.shouldWait).toBe(false);
    });

    it('should return locked security info when locked out', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 5));
      const info = getSecurityInfo('test@example.com');
      expect(info.isLocked).toBe(true);
      expect(info.lockoutTimeRemaining).toBeGreaterThan(0);
      expect(info.remainingAttempts).toBe(0);
    });
  });

  describe('clearAllAttempts', () => {
    it('should remove all stored attempts', () => {
      setStoredAttempts(makeFailedAttempts('test@example.com', 5));
      clearAllAttempts();
      expect(localStorage.removeItem).toHaveBeenCalledWith(STORAGE_KEY);
    });
  });

  describe('localStorage error handling', () => {
    it('should handle corrupted localStorage data gracefully', () => {
      localStorageData[STORAGE_KEY] = 'not-valid-json';
      expect(isLockedOut('test@example.com')).toBeNull();
      expect(getRemainingAttempts('test@example.com')).toBe(5);
    });
  });
});
