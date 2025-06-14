/**
 * AddTaskForm Component
 *
 * A versatile form for both creating a new task and editing an existing one.
 * It adapts its behavior and appearance based on whether `initialData` is provided.
 */

import React, { useState, useEffect } from 'react';
import { Task, TaskCreate } from '../types/task';

/**
 * Props for the AddTaskForm component.
 */
interface AddTaskFormProps {
  /** Callback invoked when the form is submitted with valid data. */
  onSubmit: (task: TaskCreate) => void;
  /** Optional callback invoked when the user cancels the form (e.g., in edit mode). */
  onCancel?: () => void;
  /** Optional initial data to populate the form for editing an existing task. */
  initialData?: Task;
}

const AddTaskForm: React.FC<AddTaskFormProps> = ({ onSubmit, onCancel, initialData }) => {
  const isEditMode = !!initialData;

  /**
   * Formats a date string for a datetime-local input field.
   * The input requires the 'YYYY-MM-DDTHH:mm' format.
   * @param dateString An ISO date string from the backend (assumed to be UTC).
   * @returns A formatted string compatible with datetime-local input, adjusted for the user's timezone.
   */
  const formatForInput = (dateString?: string): string => {
    if (!dateString) return '';
    try {
      // If the date string from the backend does not include timezone information
      // (i.e., no 'Z' or +/- offset), append 'Z' to ensure it's parsed as UTC.
      // This handles both new, timezone-aware dates and legacy data that might
      // have been stored as naive datetimes intended to be UTC.
      const utcDateString = /Z|[+-]\d{2}(:?\d{2})?$/.test(dateString)
        ? dateString
        : `${dateString}Z`;

      const date = new Date(utcDateString);
      if (isNaN(date.getTime())) return '';

      // To display this time correctly in a `datetime-local` input, we need
      // to format it as "YYYY-MM-DDTHH:mm" IN THE USER'S LOCAL TIMEZONE.
      const tzOffset = date.getTimezoneOffset() * 60000; // Offset in milliseconds.
      const localDate = new Date(date.getTime() - tzOffset);
      
      // `toISOString()` on this adjusted date will produce the correct YYYY-MM-DDTHH:mm string.
      return localDate.toISOString().slice(0, 16);
    } catch (e) {
      console.error('Error formatting date for input:', e);
      return '';
    }
  };

  /** The state object holding the current values of the form fields. */
  const [task, setTask] = useState<TaskCreate>({
    title: '',
    description: '',
    due_date: '',
    priority: 'medium',
  });

  // Effect to populate the form when in edit mode or when the initialData changes.
  useEffect(() => {
    if (isEditMode) {
      setTask({
        title: initialData.title || '',
        description: initialData.description || '',
        due_date: formatForInput(initialData.due_date),
        priority: initialData.priority || 'medium',
      });
    }
  }, [initialData, isEditMode]);

  /**
   * Handles form input changes by updating the component's state.
   * @param e The change event from an input, textarea, or select element.
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setTask(prevTask => ({ ...prevTask, [name]: value }));
  };

  /**
   * Handles the form submission.
   * It performs validation, formats the data for the API, calls the onSubmit prop,
   * and resets the form if in "add" mode.
   * @param e The React form event.
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.title.trim()) {
      // Basic validation to prevent submission of empty titles.
      alert('Title is a required field.');
      return;
    }

    // When the user submits the form, the `task.due_date` is a timezone-naive
    // string from the <input type="datetime-local"> (e.g., "2024-06-15T19:07").
    // We must explicitly treat this as a local time and convert it to a full
    // UTC ISO 8601 string before sending it to the backend.
    const dueDateUTC = task.due_date ? new Date(task.due_date).toISOString() : undefined;

    onSubmit({
      ...task,
      title: task.title.trim(),
      description: task.description?.trim() || undefined,
      due_date: dueDateUTC,
      priority: task.priority || undefined,
    });

    // Reset the form only when creating a new task.
    if (!isEditMode) {
      setTask({
        title: '',
        description: '',
        due_date: '',
        priority: 'medium',
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        {isEditMode ? 'Edit Task' : 'Add a New Task'}
      </h3>
      
      <div className="space-y-4">
        {/* Title Field */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={task.title}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Read a book"
            required
          />
        </div>

        {/* Description Field */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={task.description}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add some details..."
            rows={3}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Due Date Field */}
          <div>
            <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <input
              type="datetime-local"
              id="due_date"
              name="due_date"
              value={task.due_date || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Priority Field */}
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              value={task.priority}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mt-6">
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2.5 px-4 rounded-md font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
        >
          {isEditMode ? 'Save Changes' : 'Add Task'}
        </button>
        {isEditMode && onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="w-full bg-gray-200 text-gray-800 py-2.5 px-4 rounded-md font-semibold hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 transition-all duration-200"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default AddTaskForm;