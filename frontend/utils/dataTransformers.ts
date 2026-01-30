/**
 * Data Transformers
 *
 * Utilities to transform backend API responses to frontend data structures
 */

import type { StudentProfile, MenuItem, ActiveModules } from '../types';
import type { StudentProfile as ApiStudent } from '../services/studentService';
import type { MenuItem as ApiMenu } from '../services/menuService';

const defaultActiveModules: ActiveModules = {
  subjects: true,
  exams: true,
  menu: true,
  events: true,
  dinner: true,
  contacts: true,
};

/**
 * Transform backend student to frontend StudentProfile
 */
export function transformStudent(apiStudent: ApiStudent): StudentProfile {
  return {
    id: apiStudent.id,
    name: apiStudent.name,
    school: apiStudent.school,
    grade: apiStudent.grade,
    avatarUrl: apiStudent.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${apiStudent.name}`,
    allergies: apiStudent.allergies || [],
    excludedFoods: apiStudent.excluded_foods || [],
    activeModules: defaultActiveModules, // TODO: Store in backend or localStorage per student
    // Keep backend fields for API calls
    user_id: apiStudent.user_id,
    avatar_url: apiStudent.avatar_url,
    excluded_foods: apiStudent.excluded_foods,
    created_at: apiStudent.created_at,
    updated_at: apiStudent.updated_at,
  };
}

/**
 * Transform frontend StudentProfile to backend update request
 */
export function transformStudentForUpdate(student: StudentProfile) {
  return {
    name: student.name,
    school: student.school,
    grade: student.grade,
    avatar_url: student.avatarUrl,
    allergies: student.allergies,
    excluded_foods: student.excludedFoods,
  };
}

/**
 * Transform backend menu to frontend MenuItem
 */
export function transformMenu(apiMenu: ApiMenu): MenuItem {
  return {
    id: apiMenu.id,
    date: apiMenu.date,
    mainCourse: apiMenu.first_course,
    sideDish: apiMenu.side_dish || '',
    dessert: apiMenu.dessert || '',
    // Keep backend fields
    student_id: apiMenu.student_id,
    studentId: apiMenu.student_id,
    first_course: apiMenu.first_course,
    second_course: apiMenu.second_course,
    side_dish: apiMenu.side_dish,
    allergens: apiMenu.allergens,
    created_at: apiMenu.created_at,
    updated_at: apiMenu.updated_at,
  };
}

/**
 * Transform frontend MenuItem to backend create request
 */
export function transformMenuForCreate(menu: Partial<MenuItem>, studentId: string) {
  return {
    student_id: studentId,
    date: menu.date!,
    first_course: menu.mainCourse || menu.first_course!,
    second_course: menu.second_course || '',
    side_dish: menu.sideDish || menu.side_dish || undefined,
    dessert: menu.dessert || undefined,
    allergens: menu.allergens || [],
  };
}

/**
 * Transform frontend MenuItem to backend update request
 */
export function transformMenuForUpdate(menu: Partial<MenuItem>) {
  return {
    date: menu.date,
    first_course: menu.mainCourse || menu.first_course,
    second_course: menu.second_course,
    side_dish: menu.sideDish || menu.side_dish,
    dessert: menu.dessert,
    allergens: menu.allergens,
  };
}
