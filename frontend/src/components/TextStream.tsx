import React, { useState, useEffect } from 'react'

function Chat() {
  const [ws, setWs] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')

  useEffect(() => {
    const socket = new WebSocket('wss://localhost:443/ws/text') // 确保地址正确

    socket.onopen = () => {
      console.log('WebSocket Connected')
      setWs(socket)
    }

    socket.onmessage = (event) => {
      setMessages((prevMessages) => [...prevMessages, event.data])
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
    }
  }

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
        <button type='submit'>Send</button>
      </form>
      <ul>
        {messages.map((message, index) => (
          <li key={index}>{message}</li>
        ))}
      </ul>
    </div>
  )
}

export default Chat
