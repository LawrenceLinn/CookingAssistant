import React, { useState, useEffect } from 'react';

function Image() {
  const [ws, setWs] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState(null); // For storing the selected image file
  const [imagePreview, setImagePreview] = useState(''); // For storing the image preview URL
  const [imageSize, setImageSize] = useState(''); // For storing image size

  useEffect(() => {
    const socket = new WebSocket('wss://localhost:443/ws/image'); // Make sure the address is correct

    socket.onopen = () => {
      console.log('WebSocket Connected');
      setWs(socket);
    };

    socket.onmessage = (event) => {
      setMessages((prevMessages) => [...prevMessages, event.data]);
    };

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  const sendMessage = (event) => {
    event.preventDefault();
    if (ws && selectedImage) {
      const reader = new FileReader();
      reader.onload = function (e) {
        ws.send(e.target.result); // Send image as binary
      };
      reader.readAsArrayBuffer(selectedImage); // Read the file as an ArrayBuffer
    } else if (ws) {
      ws.send(inputValue); // Send text message
      setInputValue('');
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file)); // Generate and set image preview URL
      // No need to read the file here for size, URL.createObjectURL doesn't load the file into memory
      const img = new Image();
      img.onload = () => {
        setImageSize(`${img.width} x ${img.height}px`); // Set image size after loading it
      };
      img.src = URL.createObjectURL(file);
    }
  };

  return (
    <div>
      <h1>WebSocket Chat</h1>
      <form onSubmit={sendMessage}>
        <input
          type='text'
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          autoComplete='off'
        />
        <input
          type='file'
          onChange={handleFileChange}
          accept='image/*'
        />
        <button type='submit'>Send</button>
      </form>
      {imagePreview && (
        <div>
          <img src={imagePreview} alt='Preview' style={{ maxWidth: '100%', height: 'auto' }} />
          <p>Image size: {imageSize}</p>
        </div>
      )}
      <ul>
        {messages.map((message, index) => (
          <li key={index}>{message}</li>
        ))}
      </ul>
    </div>
  );
}

export default Image;
