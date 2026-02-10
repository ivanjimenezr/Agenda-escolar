import { describe, it, expect } from 'vitest';
import { validatePassword } from '../../../utils/passwordValidation';

describe('validatePassword', () => {
  it('should return all requirements unmet for empty password', () => {
    const result = validatePassword('');
    expect(result.isValid).toBe(false);
    expect(result.strength).toBe('weak');
    expect(result.requirements.every(r => !r.met)).toBe(true);
  });

  it('should detect minLength requirement', () => {
    const short = validatePassword('Ab1');
    expect(short.requirements.find(r => r.id === 'minLength')!.met).toBe(false);

    const long = validatePassword('Abcdefg1');
    expect(long.requirements.find(r => r.id === 'minLength')!.met).toBe(true);
  });

  it('should detect uppercase requirement', () => {
    const noUpper = validatePassword('abcdefg1');
    expect(noUpper.requirements.find(r => r.id === 'uppercase')!.met).toBe(false);

    const withUpper = validatePassword('Abcdefg1');
    expect(withUpper.requirements.find(r => r.id === 'uppercase')!.met).toBe(true);
  });

  it('should detect lowercase requirement', () => {
    const noLower = validatePassword('ABCDEFG1');
    expect(noLower.requirements.find(r => r.id === 'lowercase')!.met).toBe(false);

    const withLower = validatePassword('ABCDEFg1');
    expect(withLower.requirements.find(r => r.id === 'lowercase')!.met).toBe(true);
  });

  it('should detect number requirement', () => {
    const noNumber = validatePassword('Abcdefgh');
    expect(noNumber.requirements.find(r => r.id === 'number')!.met).toBe(false);

    const withNumber = validatePassword('Abcdefg1');
    expect(withNumber.requirements.find(r => r.id === 'number')!.met).toBe(true);
  });

  it('should return isValid=true when all requirements are met', () => {
    const result = validatePassword('Abcdefg1');
    expect(result.isValid).toBe(true);
  });

  it('should return isValid=false when any requirement is not met', () => {
    expect(validatePassword('abcdefg1').isValid).toBe(false); // no uppercase
    expect(validatePassword('ABCDEFG1').isValid).toBe(false); // no lowercase
    expect(validatePassword('Abcdefgh').isValid).toBe(false); // no number
    expect(validatePassword('Ab1').isValid).toBe(false);       // too short
  });

  it('should return strength=weak when 0-1 requirements met', () => {
    expect(validatePassword('').strength).toBe('weak');
    expect(validatePassword('a').strength).toBe('weak');
  });

  it('should return strength=medium when 2-3 requirements met', () => {
    // lowercase + number = 2
    expect(validatePassword('abc1').strength).toBe('medium');
    // lowercase + uppercase + number = 3 (but too short)
    expect(validatePassword('Ab1').strength).toBe('medium');
  });

  it('should return strength=strong when all 4 requirements met', () => {
    expect(validatePassword('Abcdefg1').strength).toBe('strong');
  });
});
