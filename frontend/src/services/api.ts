/**
 * API Service for Backend Communication.
 *
 * This module provides a singleton service class for all communications with the backend API.
 * It uses Axios for HTTP requests and includes interceptors for global logging and error handling.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { Task, TaskCreate, TaskUpdate, NaturalLanguageRequest } from '../types/task';

/**
 * Defines the structure for a health check response.
 */
export interface HealthStatus {
  status: string;
  llm_service: string;
}

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // Initialize the Axios instance with a base URL from environment variables,
    // falling back to a default for local development.
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 second timeout
    });

    // --- Axios Interceptors ---

    // Request interceptor for logging outgoing requests.
    this.api.interceptors.request.use(
      (config) => {
        console.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, config);
        return config;
      },
      (error: AxiosError) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for logging responses and centralizing error handling.
    this.api.interceptors.response.use(
      (response) => {
        console.debug(`API Response: ${response.status} ${response.config.url}`, response);
        return response;
      },
      (error: AxiosError) => {
        // Log a more user-friendly error message.
        const errorMessage = error.response
          ? `Error ${error.response.status}: ${JSON.stringify(error.response.data)}`
          : error.message;
        console.error('API Response Error:', errorMessage);
        
        // We re-throw the error so that the calling component can handle it
        // (e.g., show a notification to the user).
        return Promise.reject(error);
      }
    );
  }

  // --- API Methods ---

  /**
   * Fetches all tasks from the backend.
   * @returns A promise that resolves to an array of Task objects.
   */
  async getTasks(): Promise<Task[]> {
    const response = await this.api.get<Task[]>('/tasks/');
    return response.data;
  }

  /**
   * Fetches a single task by its unique ID.
   * @param id The ID of the task to fetch.
   * @returns A promise that resolves to a single Task object.
   */
  async getTask(id: number): Promise<Task> {
    const response = await this.api.get<Task>(`/tasks/${id}`);
    return response.data;
  }

  /**
   * Creates a new task with the given data.
   * @param taskData The data for the task to create.
   * @returns A promise that resolves to the newly created Task object.
   */
  async createTask(taskData: TaskCreate): Promise<Task> {
    const response = await this.api.post<Task>('/tasks', taskData);
    return response.data;
  }

  /**
   * Creates a new task by sending a natural language string to be parsed by the backend.
   * @param request The object containing the natural language text.
   * @returns A promise that resolves to the newly created Task object.
   */
  async createTaskFromNaturalLanguage(request: NaturalLanguageRequest): Promise<Task> {
    const response = await this.api.post<Task>('/tasks/parse', request);
    return response.data;
  }

  /**
   * Updates an existing task with new data.
   * @param id The ID of the task to update.
   * @param taskData The data to update the task with.
   * @returns A promise that resolves to the updated Task object.
   */
  async updateTask(id: number, taskData: TaskUpdate): Promise<Task> {
    const response = await this.api.put<Task>(`/tasks/${id}`, taskData);
    return response.data;
  }

  /**
   * Deletes a task by its unique ID.
   * @param id The ID of the task to delete.
   * @returns A promise that resolves when the deletion is complete.
   */
  async deleteTask(id: number): Promise<void> {
    await this.api.delete(`/tasks/${id}`);
  }

  /**
   * Checks the health status of the backend API.
   * This can be used to verify connectivity and see if the LLM service is active.
   * @returns A promise that resolves to a HealthStatus object.
   */
  async checkHealth(): Promise<HealthStatus> {
    // Gracefully handle errors in the health check itself, returning a "down" status.
    try {
      const response = await this.api.get<HealthStatus>('/health');
      return response.data;
    } catch (error) {
      console.error('API health check failed:', error);
      return { status: 'error', llm_service: 'unavailable' };
    }
  }
}

// Export a singleton instance of the ApiService.
// This ensures that all parts of the application use the same instance
// and share the same configuration and interceptors.
const apiService = new ApiService();
export default apiService;