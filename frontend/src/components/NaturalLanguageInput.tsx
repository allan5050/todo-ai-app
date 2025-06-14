/**
 * NaturalLanguageInput Component
 *
 * A specialized form component for creating tasks using natural language.
 * It provides a text input for the user, handles loading states, and displays
 * the availability of the primary LLM parser. It also suggests examples to the user.
 */

import React, { useState } from 'react';

/**
 * Props for the NaturalLanguageInput component.
 */
interface NaturalLanguageInputProps {
  /** Callback function invoked when the user submits the form with text. */
  onSubmit: (text: string) => void;
  /** A boolean flag indicating if a submission is currently being processed. */
  isLoading?: boolean;
  /** A boolean flag indicating if the LLM service is available. */
  isLLMAvailable?: boolean;
}

const NaturalLanguageInput: React.FC<NaturalLanguageInputProps> = ({
  onSubmit,
  isLoading = false,
  isLLMAvailable = true,
}) => {
  /** The current text value of the input field. */
  const [text, setText] = useState('');

  /**
   * Handles the form submission event.
   * It prevents the default form action, trims the input text, calls the onSubmit prop,
   * and clears the input field.
   * @param e The React form event.
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSubmit(text.trim());
      setText('');
    }
  };

  /** A list of example prompts to help guide the user. */
  const examples = [
    'Remind me to submit taxes next Monday at noon',
    'Buy groceries tomorrow high priority',
    'Call mom this weekend',
  ];

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg shadow-inner border border-gray-200 mb-6">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-3" role="img" aria-label="sparkles">✨</span>
        <h3 className="text-xl font-semibold text-gray-800">
          Create Task with AI
        </h3>
        {/* Display a small badge if the fallback parser is active */}
        {!isLLMAvailable && (
          <span className="ml-auto text-sm font-medium text-yellow-800 bg-yellow-100 px-3 py-1 rounded-full">
            AI Offline (Using Basic Parser)
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g., 'Call mom this weekend'"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow disabled:bg-gray-100"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !text.trim()}
            className={`px-6 py-3 rounded-md font-semibold text-white transition-all duration-200 ease-in-out transform hover:scale-105 ${
              isLoading || !text.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
            }`}
          >
            {isLoading ? 'Processing...' : 'Add with AI'}
          </button>
        </div>
      </form>

      {/* Suggestion buttons to demonstrate functionality */}
      <div className="mt-4">
        <p className="text-sm text-gray-600 mb-2">Need ideas? Try one of these:</p>
        <div className="flex flex-wrap gap-2">
          {examples.map((example) => (
            <button
              key={example}
              onClick={() => setText(example)}
              disabled={isLoading}
              className="text-xs bg-white px-3 py-1.5 rounded-full border border-gray-300 hover:bg-gray-100 hover:border-gray-400 transition-all duration-150 disabled:opacity-50"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NaturalLanguageInput;