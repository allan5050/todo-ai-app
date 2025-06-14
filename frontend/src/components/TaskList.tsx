/**
 * TaskList Component
 *
 * A component responsible for rendering a list of tasks. It handles the
 * display of an empty state and sorts the tasks before rendering them.
 */

import React from 'react';
import { Task } from '../types/task';
import TaskItem from './TaskItem';

/**
 * Props for the TaskList component.
 */
interface TaskListProps {
  /** An array of Task objects to display. */
  tasks: Task[];
  /** Callback function for toggling a task's completion status. */
  onToggle: (id: number) => void;
  /** Callback function for deleting a task. */
  onDelete: (id: number) => void;
  /** Callback function for initiating a task edit. */
  onEdit: (task: Task) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onToggle, onDelete, onEdit }) => {
  // Display a user-friendly message when there are no tasks.
  if (tasks.length === 0) {
    return (
      <div className="text-center py-10 px-4 bg-gray-50 rounded-lg">
        <h3 className="text-xl font-semibold text-gray-700">No Tasks Yet!</h3>
        <p className="text-gray-500 mt-2">Use the form above to add your first task.</p>
      </div>
    );
  }

  // --- Task Sorting ---
  // A new sorted array is created to avoid mutating the original props.
  // The sorting logic enhances usability by prioritizing active tasks.
  const sortedTasks = [...tasks].sort((a, b) => {
    // 1. Incomplete tasks always come before completed tasks.
    if (a.completed !== b.completed) {
      return a.completed ? 1 : -1;
    }
    // 2. For tasks with the same completion status, sort by creation date (newest first).
    // This keeps the most recently added tasks at the top of their respective groups.
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <div className="mt-4">
      {sortedTasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
          onEdit={onEdit}
        />
      ))}
    </div>
  );
};

export default TaskList;