/**
 * The main application component.
 *
 * This component serves as the root of the application, managing the overall state,
 * orchestrating data flow, and assembling the various UI components.
 */

import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import TaskList from './components/TaskList';
import AddTaskForm from './components/AddTaskForm';
import NaturalLanguageInput from './components/NaturalLanguageInput';
import api, { HealthStatus } from './services/api';
import { Task, TaskCreate, TaskUpdate } from './types/task';

function App() {
  // --- State Management ---
  /** The list of all tasks. */
  const [tasks, setTasks] = useState<Task[]>([]);
  /** Represents the loading state for the initial task fetch. */
  const [isLoading, setIsLoading] = useState(true);
  /** Holds any global error message to be displayed to the user. */
  const [error, setError] = useState<string | null>(null);
  /** Holds the task object that is currently being edited, or null if not in edit mode. */
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  /** Represents the processing state for the natural language input. */
  const [isProcessingNL, setIsProcessingNL] = useState(false);
  /** Controls the visibility of the manual "Add/Edit Task" form. */
  const [showAddForm, setShowAddForm] = useState(false);
  /** Tracks the availability of the primary LLM service. */
  const [isLLMAvailable, setIsLLMAvailable] = useState(true);

  // --- Data Fetching and Initialization ---

  /**
   * Checks the health of the backend API, including the LLM service status.
   * Updates the `isLLMAvailable` state based on the response.
   */
  const checkHealth = useCallback(async () => {
    try {
      const health: HealthStatus = await api.checkHealth();
      setIsLLMAvailable(health.llm_service === 'available');
    } catch (error) {
      console.error('Health check failed:', error);
      setIsLLMAvailable(false); // Assume unavailable on error
    }
  }, []);

  /**
   * Fetches all tasks from the API and updates the component's state.
   * Manages loading and error states for the fetch operation.
   */
  const loadTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const loadedTasks = await api.getTasks();
      setTasks(loadedTasks);
    } catch (err) {
      setError('Failed to load tasks. Please check your connection and try again.');
      console.error('Error loading tasks:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Effect to load initial data when the component mounts.
  useEffect(() => {
    loadTasks();
    checkHealth();
  }, [loadTasks, checkHealth]);


  // --- Event Handlers for CRUD Operations ---

  /**
   * Handles the creation of a new task from the manual form.
   * @param taskData The data for the new task.
   */
  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      setError(null);
      const newTask = await api.createTask(taskData);
      setTasks(prevTasks => [newTask, ...prevTasks]);
      setShowAddForm(false); // Hide form on successful creation
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    }
  };

  /**
   * Handles the creation of a new task from the natural language input.
   * Manages the specific loading state for this operation.
   * @param text The natural language text from the user.
   */
  const handleNaturalLanguageCreate = async (text: string) => {
    setIsProcessingNL(true);
    setError(null);
    try {
      const newTask = await api.createTaskFromNaturalLanguage({ text });
      setTasks(prevTasks => [newTask, ...prevTasks]);
    } catch (err) {
      setError('The AI failed to understand. Please try rephrasing or add the task manually.');
      console.error('Error processing natural language:', err);
    } finally {
      setIsProcessingNL(false);
    }
  };

  /**
   * Toggles the completion status of a task.
   * @param id The ID of the task to toggle.
   */
  const handleToggleTask = async (id: number) => {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    try {
      setError(null);
      const updatedTask = await api.updateTask(id, { completed: !task.completed });
      setTasks(tasks.map(t => (t.id === id ? updatedTask : t)));
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error toggling task:', err);
      // Note: In a real-world scenario, you might want to revert the optimistic UI update here.
    }
  };

  /**
   * Deletes a task after user confirmation.
   * @param id The ID of the task to delete.
   */
  const handleDeleteTask = async (id: number) => {
    // User confirmation to prevent accidental deletion.
    if (!window.confirm('Are you sure you want to permanently delete this task?')) {
      return;
    }

    try {
      setError(null);
      await api.deleteTask(id);
      setTasks(tasks.filter(t => t.id !== id));
    } catch (err) {
      setError('Failed to delete task. Please try again.');
      console.error('Error deleting task:', err);
    }
  };

  /**
   * Initiates the editing process for a task.
   * @param task The task object to be edited.
   */
  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowAddForm(true); // Show the form, which will now be in "edit" mode.
  };

  /**
   * Handles the submission of an updated task.
   * @param taskData The updated task data from the form.
   */
  const handleUpdateTask = async (taskData: TaskUpdate) => {
    if (!editingTask) return;

    try {
      setError(null);
      const updatedTask = await api.updateTask(editingTask.id, taskData);
      setTasks(tasks.map(t => (t.id === editingTask.id ? updatedTask : t)));
      // Reset editing state and hide the form.
      setEditingTask(null);
      setShowAddForm(false);
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  /**
   * Cancels the editing process and hides the form.
   */
  const handleCancelEdit = () => {
    setEditingTask(null);
    setShowAddForm(false);
  };

  // --- Render Method ---
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-2">
            AI-Powered Tasks
          </h1>
          <p className="text-lg text-gray-600">
            The intelligent to-do list that understands you.
          </p>
        </header>

        {/* Global Error Display */}
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6 rounded-md shadow" role="alert">
            <div className="flex">
              <div className="py-1"><svg className="fill-current h-6 w-6 text-red-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zM10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-1-5a1 1 0 0 1 1-1h2a1 1 0 0 1 0 2h-2a1 1 0 0 1-1-1zm0-4a1 1 0 0 1 1-1h2a1 1 0 1 1 0 2h-2a1 1 0 0 1-1-1z"/></svg></div>
              <div>
                <p className="font-bold">An error occurred</p>
                <p className="text-sm">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-500 hover:text-red-700"
                aria-label="Close error message"
              >
                <span className="text-2xl font-bold">&times;</span>
              </button>
            </div>
          </div>
        )}

        {/* AI Input Component */}
        <NaturalLanguageInput
          onSubmit={handleNaturalLanguageCreate}
          isLoading={isProcessingNL}
          isLLMAvailable={isLLMAvailable}
        />
        
        {/* Manual Add/Edit Form Area */}
        <div className="mb-6">
          {showAddForm ? (
            <AddTaskForm
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              onCancel={handleCancelEdit}
              initialData={editingTask ?? undefined}
            />
          ) : (
            <button
              onClick={() => { setEditingTask(null); setShowAddForm(true); }}
              className="w-full bg-white border-2 border-dashed border-gray-300 rounded-lg py-4 text-gray-500 font-semibold hover:border-blue-500 hover:text-blue-600 transition-all duration-200"
            >
              + Add a Task Manually
            </button>
          )}
        </div>

        {/* Task List Display */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800 border-b pb-3">
            Your Tasks
          </h2>
          
          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600"></div>
              <p className="mt-3 text-gray-600">Loading tasks...</p>
            </div>
          ) : (
            <TaskList
              tasks={tasks}
              onToggle={handleToggleTask}
              onDelete={handleDeleteTask}
              onEdit={handleEditTask}
            />
          )}
        </div>

        <footer className="mt-8 text-center text-sm text-gray-500">
          <p>
            LLM Status: <span className={isLLMAvailable ? 'text-green-600' : 'text-yellow-600'}>{isLLMAvailable ? 'Available' : 'Using Fallback'}</span> | 
            {' '}{tasks.filter(t => !t.completed).length} active tasks
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;