// src/components/QuestionInput.js
import React, { useState } from 'react';
import axios from 'axios';

const QuestionInput = ({ documentId }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const askQuestion = async () => {
    const formData = new FormData();
    formData.append('document_id', documentId);
    formData.append('question', question);
    
    try {
      const response = await axios.post(`http://127.0.0.1:8000/answer/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Error asking question", error);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Ask your question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={askQuestion}>Ask</button>

      {answer && (
        <div>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default QuestionInput;
