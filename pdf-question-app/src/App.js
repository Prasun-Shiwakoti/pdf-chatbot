// src/App.js
import React, { useState } from 'react';
import FileUpload from './components/fileUpload';
import NavBar from './components/navbar';
import ChatScreen from './components/chatScreen';
import './App.css';

function App() {
  const [documentId, setDocumentId] = useState(null);
  const [documentName, setDocumentName] = useState(null);
  const [uploadDisplay, setUploadDisplay] = useState('none');


  const handleUploadSuccess = (data) => {
    setDocumentId(data.document_id); 
    setDocumentName(data.filename); 
    handleFileUpload()
  };

  const handleFileUpload = () => {
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
        <ChatScreen documentId={documentId} />
      )}
    </div>
  );
}

export default App;
