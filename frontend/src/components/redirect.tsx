let ws = new WebSocket("wss://192.168.2.22:443/ws/imageCapture");
console.log('redirect');

ws.onmessage = function(event) {
    const message = event.data;
    console.log('redirect');
    if (message.startsWith("redirect:")) {
        const newWsUrl = message.split("redirect:")[1];
        console.log("Redirecting to:", newWsUrl);
        ws.close(); // Close the current WebSocket connection
        // Connect to the new WebSocket as instructed
        ws = new WebSocket(newWsUrl);

        // Make sure to set up the necessary event listeners for the new WebSocket
        ws.onopen = () => console.log("Connected to the new WebSocket");
        ws.onmessage = (event) => console.log("New message:", event.data);
        // Add onerror and onclose handlers as needed
    } else {
        console.log("Message from server:", message);
    }
};

// Make sure to handle the onopen, onerror, and onclose events as needed