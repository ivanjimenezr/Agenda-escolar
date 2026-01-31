import { describe, it, expect } from 'vitest';
import { transformMenuForCreate, transformMenuForUpdate } from '../../../utils/dataTransformers';

describe('dataTransformers - menu', () => {
  it('uses sideDish as fallback for second_course on create', () => {
    const menu = { date: '2026-02-01', mainCourse: 'Arroz', sideDish: 'Patatas' } as any;
    const result = transformMenuForCreate(menu, 'student-1') as any;
    expect(result.second_course).toBe('Patatas');
    expect(result.second_course.length).toBeGreaterThan(0);
  });

  it('falls back to mainCourse if sideDish and second_course missing on create', () => {
    const menu = { date: '2026-02-01', mainCourse: 'Arroz' } as any;
    const result = transformMenuForCreate(menu, 'student-1') as any;
    expect(result.second_course).toBe('Arroz');
  });

  it('falls back to mainCourse when sideDish is blank/whitespace', () => {
    const menu = { date: '2026-02-01', mainCourse: 'Arroz', sideDish: '   ' } as any;
    const result = transformMenuForCreate(menu, 'student-1') as any;
    expect(result.second_course).toBe('Arroz');
  });

  it('preserves explicit second_course on update', () => {
    const menu = { second_course: 'Pescado' } as any;
    const result = transformMenuForUpdate(menu) as any;
    expect(result.second_course).toBe('Pescado');
  });

  it('uses sideDish as fallback for second_course on update when provided', () => {
    const menu = { sideDish: 'Patatas' } as any;
    const result = transformMenuForUpdate(menu) as any;
    expect(result.second_course).toBe('Patatas');
  });
});