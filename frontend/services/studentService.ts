/**
 * Student Service
 *
 * API client for student profile operations
 */

import { apiClient } from './apiClient';

export interface StudentProfile {
  id: string;
  user_id: string;
  name: string;
  school: string;
  grade: string;
  avatar_url: string | null;
  allergies: string[];
  excluded_foods: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateStudentRequest {
  name: string;
  school: string;
  grade: string;
  avatar_url?: string;
  allergies?: string[];
  excluded_foods?: string[];
}

export interface UpdateStudentRequest {
  name?: string;
  school?: string;
  grade?: string;
  avatar_url?: string;
  allergies?: string[];
  excluded_foods?: string[];
}

/**
 * Create a new student profile
 */
export const createStudent = async (data: CreateStudentRequest): Promise<StudentProfile> => {
  return apiClient.post<StudentProfile>('/api/v1/students', data);
};

/**
 * Get all student profiles for the current user
 */
export const getMyStudents = async (): Promise<StudentProfile[]> => {
  return apiClient.get<StudentProfile[]>('/api/v1/students');
};

/**
 * Get a specific student profile by ID
 */
export const getStudent = async (studentId: string): Promise<StudentProfile> => {
  return apiClient.get<StudentProfile>(`/api/v1/students/${studentId}`);
};

/**
 * Update a student profile
 */
export const updateStudent = async (
  studentId: string,
  data: UpdateStudentRequest
): Promise<StudentProfile> => {
  return apiClient.put<StudentProfile>(`/api/v1/students/${studentId}`, data);
};

/**
 * Delete a student profile
 */
export const deleteStudent = async (studentId: string): Promise<void> => {
  return apiClient.delete<void>(`/api/v1/students/${studentId}`);
};
