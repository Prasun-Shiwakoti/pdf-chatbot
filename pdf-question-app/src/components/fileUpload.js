// src/components/FileUpload.js
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const FileUpload = ({ onUploadSuccess, uploadDisplay }) => {
    const [file, setFile] = useState(null); // State to hold the selected file
  
    // Configure the dropzone for file uploads
    const { getRootProps, getInputProps } = useDropzone({
      accept: '.pdf', // Accept only PDF files
      onDrop: (acceptedFiles) => {
        setFile(acceptedFiles[0]); // Set the first accepted file to state
      }
    });
  
    const uploadFile = async () => {
      const formData = new FormData(); // Create a FormData object for the file upload
      formData.append('doc', file); 
      
      try {
        // Send POST request to upload the file
        const response = await axios.post('http://127.0.0.1:8000/upload/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        onUploadSuccess(response.data); // Changes the sate of the documentId and documentName
      } catch (error) {
        console.error("Error uploading the file", error); 
      }
    };
  
    return (
      <div style={{ display: uploadDisplay }}> {/* Control visibility based on uploadDisplay prop */}
        <div {...getRootProps()} style={{ border: '2px dashed #ccc', padding: '20px' }}>
          <input {...getInputProps()} /> {/* Input for file selection */}
          <p>Drag 'n' drop a PDF file here, or click to select one</p>
        </div>
        {file && ( // Show file name and upload button if a file is selected
          <div>
            <p>{file.name}</p>
            <button onClick={uploadFile}>Upload</button>
          </div>
        )}
      </div>
    );
  };
  
  export default FileUpload;
