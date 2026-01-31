/**
 * Active Modules Service
 *
 * API client for active modules operations
 */

import { apiClient } from './apiClient';

export interface ActiveModules {
  id: string;
  student_id: string;
  subjects: boolean;
  exams: boolean;
  menu: boolean;
  events: boolean;
  dinner: boolean;
  contacts: boolean;
}

export interface UpdateActiveModulesRequest {
  subjects?: boolean;
  exams?: boolean;
  menu?: boolean;
  events?: boolean;
  dinner?: boolean;
  contacts?: boolean;
}

/**
 * Get active modules configuration for a student
 */
export const getActiveModules = async (studentId: string): Promise<ActiveModules> => {
  return apiClient.get<ActiveModules>(`/api/v1/students/${studentId}/active-modules`);
};

/**
 * Update active modules configuration for a student
 */
export const updateActiveModules = async (
  studentId: string,
  data: UpdateActiveModulesRequest
): Promise<ActiveModules> => {
  return apiClient.put<ActiveModules>(`/api/v1/students/${studentId}/active-modules`, data);
};
