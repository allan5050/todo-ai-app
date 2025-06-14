/**
 * TaskItem component for displaying individual tasks
 */

import React from 'react';
import { Task } from '../types/task';

interface TaskItemProps {
  task: Task;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
  onEdit: (task: Task) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggle, onDelete, onEdit }) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`border rounded-lg p-4 mb-3 ${task.completed ? 'bg-gray-50' : 'bg-white'} shadow-sm`}>
      <div className="flex items-start">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          className="mt-1 mr-3 h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
        />
        <div className="flex-1">
          <h3 className={`font-semibold ${task.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`text-sm mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
              {task.description}
            </p>
          )}
          <div className="flex flex-wrap gap-2 mt-2 text-sm">
            {task.due_date && (
              <span className="text-gray-500">
                📅 {formatDate(task.due_date)}
              </span>
            )}
            {task.priority && (
              <span className={`font-medium ${getPriorityColor(task.priority)}`}>
                {task.priority.toUpperCase()}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2 ml-3">
          <button
            onClick={() => onEdit(task)}
            className="text-blue-600 hover:text-blue-800 px-2 py-1 text-sm"
            title="Edit task"
          >
            ✏️
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="text-red-600 hover:text-red-800 px-2 py-1 text-sm"
            title="Delete task"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;