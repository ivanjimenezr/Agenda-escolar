import { describe, it, expect } from 'vitest';
import {
  transformMenuForCreate,
  transformMenuForUpdate,
  transformStudent,
  transformStudentForUpdate,
  transformMenu,
} from '../../../utils/dataTransformers';

describe('dataTransformers - menu create/update', () => {
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

  it('sets student_id and date on create', () => {
    const menu = { date: '2026-02-01', mainCourse: 'Arroz' } as any;
    const result = transformMenuForCreate(menu, 'student-1');
    expect(result.student_id).toBe('student-1');
    expect(result.date).toBe('2026-02-01');
  });

  it('defaults allergens to empty array on create', () => {
    const menu = { date: '2026-02-01', mainCourse: 'Arroz' } as any;
    const result = transformMenuForCreate(menu, 'student-1');
    expect(result.allergens).toEqual([]);
  });

  it('preserves provided allergens on create', () => {
    const menu = { date: '2026-02-01', mainCourse: 'Arroz', allergens: ['gluten'] } as any;
    const result = transformMenuForCreate(menu, 'student-1');
    expect(result.allergens).toEqual(['gluten']);
  });
});

describe('dataTransformers - transformStudent', () => {
  const apiStudent = {
    id: 'student-123',
    user_id: 'user-1',
    name: 'Alex García',
    school: 'Colegio Cervantes',
    grade: '5º Primaria',
    avatar_url: 'https://example.com/avatar.png',
    allergies: ['gluten'],
    excluded_foods: ['fish'],
    created_at: '2026-01-31T10:00:00Z',
    updated_at: '2026-01-31T10:00:00Z',
  };

  it('should transform basic student fields', () => {
    const result = transformStudent(apiStudent);
    expect(result.id).toBe('student-123');
    expect(result.name).toBe('Alex García');
    expect(result.school).toBe('Colegio Cervantes');
    expect(result.grade).toBe('5º Primaria');
  });

  it('should use avatar_url when provided', () => {
    const result = transformStudent(apiStudent);
    expect(result.avatarUrl).toBe('https://example.com/avatar.png');
  });

  it('should generate fallback avatar URL when avatar_url is null', () => {
    const studentNoAvatar = { ...apiStudent, avatar_url: null };
    const result = transformStudent(studentNoAvatar);
    expect(result.avatarUrl).toContain('dicebear.com');
    expect(result.avatarUrl).toContain('Alex');
  });

  it('should default allergies to empty array when null', () => {
    const studentNoAllergies = { ...apiStudent, allergies: null as any };
    const result = transformStudent(studentNoAllergies);
    expect(result.allergies).toEqual([]);
  });

  it('should default excluded_foods to empty array when null', () => {
    const studentNoFoods = { ...apiStudent, excluded_foods: null as any };
    const result = transformStudent(studentNoFoods);
    expect(result.excludedFoods).toEqual([]);
  });

  it('should use provided activeModules', () => {
    const modules = {
      subjects: false,
      exams: true,
      menu: false,
      events: true,
      dinner: false,
      contacts: true,
    };
    const result = transformStudent(apiStudent, modules);
    expect(result.activeModules).toEqual(modules);
  });

  it('should use default activeModules when not provided', () => {
    const result = transformStudent(apiStudent);
    expect(result.activeModules).toEqual({
      subjects: true,
      exams: true,
      menu: true,
      events: true,
      dinner: true,
      contacts: true,
    });
  });

  it('should preserve backend fields', () => {
    const result = transformStudent(apiStudent);
    expect(result.user_id).toBe('user-1');
    expect(result.created_at).toBe('2026-01-31T10:00:00Z');
    expect(result.updated_at).toBe('2026-01-31T10:00:00Z');
  });
});

describe('dataTransformers - transformStudentForUpdate', () => {
  it('should transform frontend profile to backend update format', () => {
    const profile = {
      id: 'student-123',
      name: 'Alex García',
      school: 'Colegio Cervantes',
      grade: '5º Primaria',
      avatarUrl: 'https://example.com/avatar.png',
      allergies: ['gluten'],
      excludedFoods: ['fish'],
      activeModules: {} as any,
    } as any;

    const result = transformStudentForUpdate(profile);
    expect(result).toEqual({
      name: 'Alex García',
      school: 'Colegio Cervantes',
      grade: '5º Primaria',
      avatar_url: 'https://example.com/avatar.png',
      allergies: ['gluten'],
      excluded_foods: ['fish'],
    });
  });

  it('should not include id or activeModules in update payload', () => {
    const profile = {
      id: 'student-123',
      name: 'Test',
      school: 'Test',
      grade: 'Test',
      avatarUrl: null,
      allergies: [],
      excludedFoods: [],
      activeModules: { subjects: true },
    } as any;

    const result = transformStudentForUpdate(profile);
    expect(result).not.toHaveProperty('id');
    expect(result).not.toHaveProperty('activeModules');
  });
});

describe('dataTransformers - transformMenu', () => {
  const apiMenu = {
    id: 'menu-1',
    student_id: 'student-123',
    date: '2026-02-01',
    first_course: 'Sopa',
    second_course: 'Pollo',
    side_dish: 'Ensalada',
    dessert: 'Fruta',
    allergens: ['gluten'],
    created_at: '2026-01-31T10:00:00Z',
    updated_at: '2026-01-31T10:00:00Z',
  };

  it('should transform basic menu fields', () => {
    const result = transformMenu(apiMenu);
    expect(result.id).toBe('menu-1');
    expect(result.date).toBe('2026-02-01');
    expect(result.mainCourse).toBe('Sopa');
  });

  it('should map first_course to mainCourse', () => {
    const result = transformMenu(apiMenu);
    expect(result.mainCourse).toBe(apiMenu.first_course);
  });

  it('should default sideDish to empty string when null', () => {
    const menuNoSide = { ...apiMenu, side_dish: null };
    const result = transformMenu(menuNoSide);
    expect(result.sideDish).toBe('');
  });

  it('should default dessert to empty string when null', () => {
    const menuNoDessert = { ...apiMenu, dessert: null };
    const result = transformMenu(menuNoDessert);
    expect(result.dessert).toBe('');
  });

  it('should preserve backend fields', () => {
    const result = transformMenu(apiMenu);
    expect(result.student_id).toBe('student-123');
    expect(result.studentId).toBe('student-123');
    expect(result.first_course).toBe('Sopa');
    expect(result.second_course).toBe('Pollo');
    expect(result.allergens).toEqual(['gluten']);
  });
});
