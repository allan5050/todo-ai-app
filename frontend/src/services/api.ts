/**
 * API service for backend communication
 */

import axios, { AxiosInstance } from 'axios';
import { Task, TaskCreate, TaskUpdate, NaturalLanguageRequest } from '../types/task';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get all tasks
   */
  async getTasks(): Promise<Task[]> {
    try {
      const response = await this.api.get<Task[]>('/tasks');
      return response.data;
    } catch (error) {
      console.error('Error fetching tasks:', error);
      throw error;
    }
  }

  /**
   * Get a single task by ID
   */
  async getTask(id: number): Promise<Task> {
    try {
      const response = await this.api.get<Task>(`/tasks/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching task ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create a new task
   */
  async createTask(task: TaskCreate): Promise<Task> {
    try {
      const response = await this.api.post<Task>('/tasks', task);
      return response.data;
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  }

  /**
   * Create a task from natural language
   */
  async createTaskFromNaturalLanguage(request: NaturalLanguageRequest): Promise<Task> {
    try {
      const response = await this.api.post<Task>('/tasks/parse', request);
      return response.data;
    } catch (error) {
      console.error('Error parsing natural language:', error);
      throw error;
    }
  }

  /**
   * Update a task
   */
  async updateTask(id: number, task: TaskUpdate): Promise<Task> {
    try {
      const response = await this.api.put<Task>(`/tasks/${id}`, task);
      return response.data;
    } catch (error) {
      console.error(`Error updating task ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete a task
   */
  async deleteTask(id: number): Promise<void> {
    try {
      await this.api.delete(`/tasks/${id}`);
    } catch (error) {
      console.error(`Error deleting task ${id}:`, error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<{ status: string; llm_available: boolean }> {
    try {
      const response = await this.api.get<{ status: string; llm_available: boolean }>('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      return { status: 'error', llm_available: false };
    }
  }
}

export default new ApiService();