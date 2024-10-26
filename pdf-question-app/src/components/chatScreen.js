
import React, { useState } from 'react';
import axios from 'axios';



const ChatScreen = ({ documentId }) => {
    const [messages, setMessages] = useState([]); // State to hold chat messages

    const updateMessages = (profile, message) => {
        // Update the messages state with a new message from either user or AI
        setMessages(prevMessages => [...prevMessages, { 'profile': profile, 'message': message, 'key': Math.random() }]);
    }

    const askQuestion = async () => {
        let question = document.getElementById('user-prompt').value; 
        document.getElementById('user-prompt').value = ''; 
        updateMessages('user', question); // Update messages with user's question

        const formData = new FormData(); // Create FormData object to send data
        formData.append('document_id', documentId); 
        formData.append('question', question); 
        
        try {
            // Send POST request to the server with the question and document ID
            const response = await axios.post(`http://127.0.0.1:8000/answer/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            updateMessages('ai', response.data.answer); // Update messages with AI's response

        } catch (error) {
            console.error("Error asking question", error); // Log any errors that occur during the request
        }
    };
    
    return (
        <div className="chatScreen">
            <div className="messageContainer">
                {messages.map((message) => (
                    <div className="messageBox" key={message.key}>
                        <div className={`profilePic ${message.profile}-profile`} />
                        <div className="message">{message.message}</div>
                    </div>
                ))}
            </div>

            <div className="inputContainer">
                <input id='user-prompt' type="text" placeholder="Send a message..." />
                <button className='send-icon' onClick={askQuestion}></button>
            </div>
        </div>
    );
}

export default ChatScreen;