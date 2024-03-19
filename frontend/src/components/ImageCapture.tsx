import React, { useState, useEffect, useRef } from 'react';

function ImageCapture() {
  const [ws, setWs] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null); // For capturing images from the video stream

  useEffect(() => {
    const socket = new WebSocket('wss://localhost:443/ws/imageCapture'); // Make sure the address is correct

    socket.onopen = () => {
      console.log('WebSocket Connected');
      setWs(socket);

      // Access the camera
      if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            if (videoRef.current) {
              videoRef.current.srcObject = stream;
            }
          })
          .catch(console.error);
      }
    };

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

  return (
    <div>
      <h1>Image Capture and Upload</h1>
      <video ref={videoRef} autoPlay playsInline style={{ width: '300px' }}></video>
      <button onClick={captureImage}>Capture and Upload</button>
      <canvas ref={canvasRef} width="300" height="300" style={{ display: 'none' }}></canvas>
    </div>
  );
}

export default ImageCapture;
