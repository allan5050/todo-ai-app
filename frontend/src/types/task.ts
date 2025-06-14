/**
 * Task type definitions
 */

export interface Task {
    id: number;
    title: string;
    description?: string;
    completed: boolean;
    due_date?: string;
    priority?: string;
    created_at: string;
    updated_at: string;
  }
  
  export interface TaskCreate {
    title: string;
    description?: string;
    due_date?: string;
    priority?: string;
  }
  
  export interface TaskUpdate {
    title?: string;
    description?: string;
    completed?: boolean;
    due_date?: string;
    priority?: string;
  }
  
  export interface NaturalLanguageRequest {
    text: string;
  }