/**
 * Exam Service
 *
 * API client for exam operations
 */

import { apiClient } from './apiClient';
import { Exam } from '../types';

/**
 * Request type for creating an exam
 */
export interface CreateExamRequest {
  subject: string;
  date: string; // YYYY-MM-DD format
  topic: string;
  notes?: string;
}

/**
 * Request type for updating an exam
 */
export interface UpdateExamRequest {
  subject?: string;
  date?: string; // YYYY-MM-DD format
  topic?: string;
  notes?: string;
}

/**
 * Create a new exam for a student
 */
export const createExam = async (studentId: string, data: CreateExamRequest): Promise<Exam> => {
  console.log('[examService] createExam called:', { studentId, data });
  const result = await apiClient.post<Exam>(`/api/v1/students/${studentId}/exams`, data);
  console.log('[examService] createExam result:', result);
  return result;
};

/**
 * Get all exams for a specific student
 */
export const getExamsByStudent = async (
  studentId: string,
  fromDate?: string,
  toDate?: string
): Promise<Exam[]> => {
  let url = `/api/v1/students/${studentId}/exams`;
  const params = new URLSearchParams();

  if (fromDate) params.append('from_date', fromDate);
  if (toDate) params.append('to_date', toDate);

  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  return apiClient.get<Exam[]>(url);
};

/**
 * Get a specific exam by ID for a student
 */
export const getExamById = async (studentId: string, examId: string): Promise<Exam> => {
  return apiClient.get<Exam>(`/api/v1/students/${studentId}/exams/${examId}`);
};

/**
 * Update an exam for a student
 */
export const updateExam = async (
  studentId: string,
  examId: string,
  data: UpdateExamRequest
): Promise<Exam> => {
  console.log('[examService] updateExam called:', { studentId, examId, data });
  const result = await apiClient.put<Exam>(`/api/v1/students/${studentId}/exams/${examId}`, data);
  console.log('[examService] updateExam result:', result);
  return result;
};

/**
 * Delete an exam for a student (hard delete - permanent)
 */
export const deleteExam = async (studentId: string, examId: string): Promise<void> => {
  return apiClient.delete<void>(`/api/v1/students/${studentId}/exams/${examId}`);
};
