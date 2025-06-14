/**
 * Main App component
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import TaskList from './components/TaskList';
import AddTaskForm from './components/AddTaskForm';
import NaturalLanguageInput from './components/NaturalLanguageInput';
import api from './services/api';
import { Task, TaskCreate, TaskUpdate } from './types/task';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isProcessingNL, setIsProcessingNL] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [isLLMAvailable, setIsLLMAvailable] = useState(true);

  // Load tasks on component mount
  useEffect(() => {
    loadTasks();
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await api.checkHealth();
      setIsLLMAvailable(health.llm_available);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const loadedTasks = await api.getTasks();
      setTasks(loadedTasks);
    } catch (error) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error loading tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      const newTask = await api.createTask(taskData);
      setTasks([newTask, ...tasks]);
      setShowAddForm(false);
    } catch (error) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', error);
    }
  };

  const handleNaturalLanguageCreate = async (text: string) => {
    try {
      setIsProcessingNL(true);
      setError(null);
      const newTask = await api.createTaskFromNaturalLanguage({ text });
      setTasks([newTask, ...tasks]);
    } catch (error) {
      setError('Failed to process natural language. Please try again.');
      console.error('Error processing natural language:', error);
    } finally {
      setIsProcessingNL(false);
    }
  };

  const handleToggleTask = async (id: number) => {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    try {
      const updatedTask = await api.updateTask(id, { completed: !task.completed });
      setTasks(tasks.map(t => t.id === id ? updatedTask : t));
    } catch (error) {
      setError('Failed to update task. Please try again.');
      console.error('Error toggling task:', error);
    }
  };

  const handleDeleteTask = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;

    try {
      await api.deleteTask(id);
      setTasks(tasks.filter(t => t.id !== id));
    } catch (error) {
      setError('Failed to delete task. Please try again.');
      console.error('Error deleting task:', error);
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowAddForm(true);
  };

  const handleUpdateTask = async (taskData: TaskCreate) => {
    if (!editingTask) return;

    try {
      const updatedTask = await api.updateTask(editingTask.id, taskData);
      setTasks(tasks.map(t => t.id === editingTask.id ? updatedTask : t));
      setEditingTask(null);
      setShowAddForm(false);
    } catch (error) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', error);
    }
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
    setShowAddForm(false);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Todo AI App
          </h1>
          <p className="text-gray-600">
            Manage your tasks with natural language processing
          </p>
        </header>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
            <button
              onClick={() => setError(null)}
              className="float-right font-bold"
            >
              ×
            </button>
          </div>
        )}

        <NaturalLanguageInput
          onSubmit={handleNaturalLanguageCreate}
          isLoading={isProcessingNL}
          isLLMAvailable={isLLMAvailable}
        />

        <div className="mb-6">
          {showAddForm ? (
            <AddTaskForm
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              onCancel={handleCancelEdit}
              initialData={editingTask ? {
                title: editingTask.title,
                description: editingTask.description,
                due_date: editingTask.due_date,
                priority: editingTask.priority,
              } : undefined}
            />
          ) : (
            <button
              onClick={() => setShowAddForm(true)}
              className="w-full bg-white border-2 border-dashed border-gray-300 rounded-lg py-4 text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-colors"
            >
              + Add Task Manually
            </button>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            Your Tasks
          </h2>
          
          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading tasks...</p>
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
            {isLLMAvailable ? '✅ LLM Available' : '⚠️ Using Fallback Parser'} | 
            {' '}{tasks.filter(t => !t.completed).length} active, {tasks.filter(t => t.completed).length} completed
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;