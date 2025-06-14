/**
 * TaskItem Component
 *
 * A presentational component responsible for rendering a single task item.
 * It displays the task's details and provides controls for toggling completion,
 * editing, and deleting the task.
 */

import React from 'react';
import { Task } from '../types/task';

/**
 * Props for the TaskItem component.
 */
interface TaskItemProps {
  /** The task object to display. */
  task: Task;
  /** Callback function to be invoked when the task's completion status is toggled. */
  onToggle: (id: number) => void;
  /** Callback function to be invoked when the task is deleted. */
  onDelete: (id: number) => void;
  /** Callback function to be invoked when the user initiates an edit of the task. */
  onEdit: (task: Task) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggle, onDelete, onEdit }) => {
  /**
   * Formats an ISO date string into a more readable local date and time string.
   * @param dateString The ISO date string to format.
   * @returns A formatted string or null if the input is invalid.
   */
  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      // Create a new Date object directly from the ISO string.
      // The backend now consistently provides timezone-aware strings (e.g., ending in 'Z' or with a +-offset),
      // which new Date() parses correctly into the user's local timezone.
      return new Date(dateString).toLocaleString();
    } catch (error) {
      console.error("Error formatting date:", error);
      return "Invalid Date";
    }
  };

  /**
   * Determines the Tailwind CSS text color class based on the task's priority.
   * @param priority The priority string (e.g., 'high', 'medium', 'low').
   * @returns A string containing the appropriate CSS color class.
   */
  const getPriorityColor = (priority?: string): string => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div
      className={`border rounded-lg p-4 mb-3 transition-colors duration-200 ${
        task.completed ? 'bg-gray-50 opacity-60' : 'bg-white'
      } shadow-sm hover:shadow-md`}
    >
      <div className="flex items-start">
        {/* Checkbox for toggling task completion */}
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          className="mt-1 mr-4 h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
        />
        <div className="flex-1">
          {/* Task Title */}
          <h3
            className={`font-semibold text-lg ${
              task.completed ? 'line-through text-gray-500' : 'text-gray-800'
            }`}
          >
            {task.title}
          </h3>
          {/* Task Description */}
          {task.description && (
            <p className={`text-sm mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
              {task.description}
            </p>
          )}
          {/* Task Metadata: Due Date and Priority */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm">
            {task.due_date && (
              <span className="flex items-center text-gray-500">
                <span className="mr-1">📅</span>
                {formatDate(task.due_date)}
              </span>
            )}
            {task.priority && (
              <span
                className={`font-medium rounded-full px-2 py-0.5 text-xs ${getPriorityColor(
                  task.priority
                )} bg-opacity-20`}
              >
                {task.priority.toUpperCase()}
              </span>
            )}
          </div>
        </div>
        {/* Action Buttons: Edit and Delete */}
        <div className="flex gap-2 ml-3">
          <button
            onClick={() => onEdit(task)}
            className="text-gray-500 hover:text-blue-600 transition-colors p-2 rounded-full hover:bg-gray-100"
            title="Edit task"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
              <path fillRule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="text-gray-500 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-gray-100"
            title="Delete task"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;