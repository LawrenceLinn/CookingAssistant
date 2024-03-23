import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

function Chat() {
  const [ws, setWs] = useState(null)
  const [messages, setMessages] = useState([])
  const [imageSrc, setImageSrc] = useState([])
  const [inputValue, setInputValue] = useState('')
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  const myParam = searchParams.get('item_id'); 

  let url = `wss://192.168.2.22:443/ws/text`

  useEffect(() => {
    // Handle query parameters
    if (myParam) {
      // url = 'wss://:443/ws/text' + '?item_id=' + myParam
      url = `wss://192.168.2.22:443/ws/text?item_id=${myParam}`
    }
    //  else {
    //   url = 'wss://localhost:443/ws/text'
    // }

    var socket = new WebSocket(url) // 确保地址正确
    
    socket.onopen = () => {
      console.log('WebSocket Connected')
      setWs(socket)
    }

    socket.onmessage = (event) => {
      // setMessages((prevMessages) => [...prevMessages, event.data])
      // console.log(event.data)
      if (typeof event.data === 'string') {
        // Handle text message
        setMessages((prevMessages) => [...prevMessages, event.data])
      } else if (event.data instanceof Blob) {
        // Read bytes
        const blob = event.data;
        // Create url
        const imageUrl = URL.createObjectURL(blob);
        // Create element for image
        const targetImg = document.getElementById('img');
        targetImg.src = imageUrl
      };
    }

    // 只有在组件卸载时关闭 WebSocket 连接
    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close()
      }
    }
  }, []) // 空依赖数组意味着这个 effect 只在组件挂载时运行

  const sendMessage = (event) => {
    event.preventDefault()
    if (ws) {
      ws.send(inputValue)
      setInputValue('')
      // Display user input message
      var ul = document.getElementById("list");
      // Dynamically add elements
      if (ul) {
        var li = document.createElement("li");
        li.appendChild(document.createTextNode('User: '+inputValue));
        ul.appendChild(li);
        console.log('append')
      }
    }
  }

  return (
    <div id='div'>
      <img id='img' src='' style={{ maxWidth: '30%', height: 'auto' }}></img>
      <h1>WebSocket Chat</h1>
      <form onSubmit={sendMessage}>
        <input
          type='text'
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          autoComplete='off'
        />
        <button type='submit'>Send</button>
      </form>
      <ul id='list'>
        {messages.map((message, index) => (
          <li key={index}>{message}</li>
        ))}
      </ul>
    </div>
  )
}

export default Chat
