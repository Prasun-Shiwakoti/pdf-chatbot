// src/App.js
import React, { useState, useEffect } from 'react';
import FileUpload from './components/fileUpload';
import NavBar from './components/navbar';
import ChatScreen from './components/chatScreen';
import './App.css';
import axios from 'axios';

function App() {
  const [documentId, setDocumentId] = useState(null);
  const [documentName, setDocumentName] = useState(null);
  const [uploadDisplay, setUploadDisplay] = useState('none');
  const [messages, setMessages] = useState([]);

  const updateMessages = (profile, message) => {
      // Update the messages state with a new message from either user or AI
      setMessages(prevMessages => [...prevMessages, { 'role': profile, 'content': message}]);
  }
  const fetchMessages = async (documentId) => {
    // Fetch messages from the server
    try {
      const response = await axios.get(`http://127.0.0.1:8000/chats/${documentId}/`);
      setMessages(response.data.messages);
    }
    catch (error) {
      console.error("Error fetching messages", error);
    }
  }
  useEffect(() => {
    // Fetch messages when the document ID changes
    if (documentId) {
      fetchMessages(documentId);
    }
  }, [documentId]);
  const handleUploadSuccess = (data) => {
    // Set the document ID and name when the file is uploaded
    setDocumentId(data.document_id); 
    setDocumentName(data.filename); 
    handleFileUpload();

  };

  const handleFileUpload = () => {
    // Toggle the display of the file upload component
    if (uploadDisplay === 'none'){
      setUploadDisplay('unset');
    }
    else{
      setUploadDisplay('none');
    }
  }


  return (
    <div className="App">
      <NavBar onUploadClick={handleFileUpload} documentName={documentName}/>
      <FileUpload onUploadSuccess={handleUploadSuccess} uploadDisplay={uploadDisplay} />

      {documentId && (
        <ChatScreen documentId={documentId} messages={messages} updateMessages={updateMessages}  />
      )}
    </div>
  );
}

export default App;
