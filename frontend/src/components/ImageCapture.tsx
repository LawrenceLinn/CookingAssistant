import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function ImageCapture() {
  const [ws, setWs] = useState(null);
  const [wsData, setWsData] = useState(null);
  const [stream, setStream] = useState(null);
  const videoRef = useRef(null);
  const [messages, setMessages] = useState([])
  const canvasRef = useRef(null); // For capturing images from the video stream
  const navigateTo = useNavigate();

  useEffect(() => {
    const socket = new WebSocket('wss://localhost:443/ws/imageCapture'); // Make sure the address is correct

    socket.onopen = () => {
      console.log('WebSocket Connected');
      setWs(socket);

      // Access the camera
      if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            setStream(stream); // Store the stream for later use
            videoRef.current.srcObject = stream;
          })
          .catch(console.error);

        return () => {
          socket.close();
          stopCamera(); // Ensure the camera is stopped when the component unmounts
        };
      }
    };

    socket.onmessage = (event) => {
      console.log('redirect');
      // const message = event.data;
      const message = JSON.parse(event.data);
      if (message.redirect) {
          console.log(message.redirect);
          socket.close()
          setWsData(message.data);
          navigateTo(message.redirect);  // Using React Router for SPA internal redirect
      } else {
          console.log("Message from server:", message);
          setMessages((prevMessages) => [...prevMessages, event.data])
      }
    }

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  const captureImage = () => {
    const context = canvasRef.current.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
    // Convert the canvas to blob and send over WebSocket
    canvasRef.current.toBlob(blob => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(blob);
      }
    }, 'image/jpeg');
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop()); // Stop each track of the stream
      setStream(null); // Clear the stored stream
    }
  }

  return (
    <div>
      <h1>Image Capture and Upload</h1>
      <video ref={videoRef} autoPlay playsInline style={{ width: '300px' }}></video>
      
      <canvas ref={canvasRef} width="300" height="300" style={{ display: 'none' }}></canvas>
      <button onClick={() => { captureImage(); stopCamera(); }}>Capture and Upload</button>
      <ul>
        {messages.map((message, index) => (
          <li key={index}>{message}</li>
        ))}
      </ul>
    </div>
  );
}

export default ImageCapture;
