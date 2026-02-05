/**
 * Event Service
 *
 * API client for school event operations
 */

import { apiClient } from './apiClient';
import { SchoolEvent } from '../types';

/**
 * Request type for creating an event
 */
export interface CreateEventRequest {
  date: string; // YYYY-MM-DD format
  name: string;
  type: 'Festivo' | 'Lectivo' | 'Vacaciones';
}

/**
 * Request type for updating an event
 */
export interface UpdateEventRequest {
  date?: string; // YYYY-MM-DD format
  name?: string;
  type?: 'Festivo' | 'Lectivo' | 'Vacaciones';
}

/**
 * Create a new event
 */
export const createEvent = async (data: CreateEventRequest): Promise<SchoolEvent> => {
  console.log('[eventService] createEvent called:', data);
  const result = await apiClient.post<SchoolEvent>('/api/v1/events', data);
  console.log('[eventService] createEvent result:', result);
  return result;
};

/**
 * Get all events for current user
 */
export const getEvents = async (
  fromDate?: string,
  toDate?: string
): Promise<SchoolEvent[]> => {
  console.log('[eventService] getEvents called with:', { fromDate, toDate });
  let url = '/api/v1/events';
  const params = new URLSearchParams();

  if (fromDate) params.append('from_date', fromDate);
  if (toDate) params.append('to_date', toDate);

  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  console.log('[eventService] Fetching events from:', url);
  const result = await apiClient.get<SchoolEvent[]>(url);
  console.log('[eventService] getEvents result:', result);
  return result;
};

/**
 * Get a specific event by ID
 */
export const getEventById = async (eventId: string): Promise<SchoolEvent> => {
  return apiClient.get<SchoolEvent>(`/api/v1/events/${eventId}`);
};

/**
 * Update an event
 */
export const updateEvent = async (
  eventId: string,
  data: UpdateEventRequest
): Promise<SchoolEvent> => {
  console.log('[eventService] updateEvent called:', { eventId, data });
  const result = await apiClient.put<SchoolEvent>(`/api/v1/events/${eventId}`, data);
  console.log('[eventService] updateEvent result:', result);
  return result;
};

/**
 * Delete an event (hard delete - permanent)
 */
export const deleteEvent = async (eventId: string): Promise<void> => {
  console.log('[eventService] deleteEvent called:', eventId);
  return apiClient.delete<void>(`/api/v1/events/${eventId}`);
};
