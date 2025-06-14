/**
 * NaturalLanguageInput component for AI-powered task creation
 */

import React, { useState } from 'react';

interface NaturalLanguageInputProps {
  onSubmit: (text: string) => void;
  isLoading?: boolean;
  isLLMAvailable?: boolean;
}

const NaturalLanguageInput: React.FC<NaturalLanguageInputProps> = ({ 
  onSubmit, 
  isLoading = false,
  isLLMAvailable = true 
}) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSubmit(text.trim());
      setText('');
    }
  };

  const examples = [
    "Remind me to submit taxes next Monday at noon",
    "Buy groceries tomorrow high priority",
    "Call mom this weekend",
    "Meeting with team next Friday at 3pm",
  ];

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg shadow-md mb-6">
      <div className="flex items-center mb-4">
        <span className="text-2xl mr-2">✨</span>
        <h3 className="text-lg font-semibold text-gray-800">
          Natural Language Task Creation
        </h3>
        {!isLLMAvailable && (
          <span className="ml-auto text-sm text-yellow-600 bg-yellow-100 px-2 py-1 rounded">
            Using fallback parser
          </span>
        )}
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g., 'Remind me to submit taxes next Monday at noon'"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !text.trim()}
            className={`px-6 py-3 rounded-md font-medium transition-colors ${
              isLoading || !text.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isLoading ? 'Processing...' : 'Create Task'}
          </button>
        </div>
      </form>

      <div className="mt-4">
        <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => setText(example)}
              className="text-xs bg-white px-3 py-1 rounded-full border border-gray-300 hover:bg-gray-50 transition-colors"
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