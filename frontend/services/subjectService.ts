/**
 * Subject Service
 *
 * API client for subject (asignatura) operations
 */

import { apiClient } from './apiClient';
import { Subject, CreateSubjectRequest, UpdateSubjectRequest } from '../types';

/**
 * Create a new subject for a student
 */
export const createSubject = async (studentId: string, data: CreateSubjectRequest): Promise<Subject> => {
  return apiClient.post<Subject>(`/api/v1/students/${studentId}/subjects`, data);
};

/**
 * Get all subjects for a specific student
 */
export const getSubjectsByStudent = async (studentId: string): Promise<Subject[]> => {
  return apiClient.get<Subject[]>(`/api/v1/students/${studentId}/subjects`);
};

/**
 * Get a specific subject by ID for a student
 */
export const getSubjectById = async (studentId: string, subjectId: string): Promise<Subject> => {
  return apiClient.get<Subject>(`/api/v1/students/${studentId}/subjects/${subjectId}`);
};

/**
 * Update a subject for a student
 */
export const updateSubject = async (
  studentId: string,
  subjectId: string,
  data: UpdateSubjectRequest
): Promise<Subject> => {
  return apiClient.put<Subject>(`/api/v1/students/${studentId}/subjects/${subjectId}`, data);
};

/**
 * Delete a subject for a student
 */
export const deleteSubject = async (studentId: string, subjectId: string): Promise<void> => {
  return apiClient.delete<void>(`/api/v1/students/${studentId}/subjects/${subjectId}`);
};
