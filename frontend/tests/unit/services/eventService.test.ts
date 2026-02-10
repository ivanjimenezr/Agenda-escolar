import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createEvent,
  getEvents,
  getEventById,
  updateEvent,
  deleteEvent,
} from '../../../services/eventService';
import { apiClient } from '../../../services/apiClient';

const mockEvent = {
  id: 'event-1',
  user_id: 'user-123',
  date: '2026-03-19',
  name: 'Día del Padre',
  type: 'Festivo' as const,
  created_at: '2026-01-31T10:00:00Z',
  updated_at: '2026-01-31T10:00:00Z',
};

describe('eventService', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    const localStorageMock = {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    global.localStorage = localStorageMock as any;
  });

  describe('createEvent', () => {
    it('should create an event', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockEvent as any);

      const data = { date: '2026-03-19', name: 'Día del Padre', type: 'Festivo' as const };
      const result = await createEvent(data);

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/events', data);
      expect(result).toEqual(mockEvent);
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('Validation error'));

      await expect(
        createEvent({ date: '', name: '', type: 'Festivo' })
      ).rejects.toThrow('Validation error');
    });
  });

  describe('getEvents', () => {
    it('should fetch events without date filters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([mockEvent] as any);

      const result = await getEvents();

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/events');
      expect(result).toHaveLength(1);
    });

    it('should include from_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getEvents('2026-03-01');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/events?from_date=2026-03-01'
      );
    });

    it('should include to_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getEvents(undefined, '2026-03-31');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/events?to_date=2026-03-31'
      );
    });

    it('should include both date parameters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getEvents('2026-03-01', '2026-03-31');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/events?from_date=2026-03-01&to_date=2026-03-31'
      );
    });

    it('should return empty array when no events', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      const result = await getEvents();
      expect(result).toEqual([]);
    });
  });

  describe('getEventById', () => {
    it('should fetch a specific event', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockEvent as any);

      const result = await getEventById('event-1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/events/event-1');
      expect(result).toEqual(mockEvent);
    });

    it('should propagate not found errors', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new Error('Not found'));

      await expect(getEventById('nonexistent')).rejects.toThrow('Not found');
    });
  });

  describe('updateEvent', () => {
    it('should update an event', async () => {
      const updated = { ...mockEvent, name: 'Día de la Constitución' };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateEvent('event-1', { name: 'Día de la Constitución' });

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/events/event-1', {
        name: 'Día de la Constitución',
      });
      expect(result.name).toBe('Día de la Constitución');
    });
  });

  describe('deleteEvent', () => {
    it('should delete an event', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteEvent('event-1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/events/event-1');
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(new Error('Forbidden'));

      await expect(deleteEvent('event-1')).rejects.toThrow('Forbidden');
    });
  });
});
