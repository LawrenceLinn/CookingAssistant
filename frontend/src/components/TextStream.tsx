import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import '../css/chat.css';
import send from '../icons/send.png';
import chatbot from '../icons/chatbot.png';
import user from '../icons/user.png';
import loading from '../icons/loading.gif';

function Chat() {
  const [ws, setWs] = useState(null)
  const [inputValue, setInputValue] = useState('')
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  const myParam = searchParams.get('item_id'); 

  let url = `wss://${import.meta.env.VITE_IP_ADDRESS}:443/ws/text`

  useEffect(() => {
    // Handle query parameters
    if (myParam) {
      url = `wss://${import.meta.env.VITE_IP_ADDRESS}:443/ws/text?item_id=${myParam}`
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

      var section = document.getElementById("messages-chat");

      if (typeof event.data === 'string') {
        // Handle text message
        if (section) {
          var message_div = document.createElement("div");
          message_div.className = 'message'

          var photo = document.createElement("img");
          photo.className = 'photo'
          photo.src = chatbot
          message_div.appendChild(photo);

          var text = document.createElement("p");
          text.className = 'text'
          text.innerText = event.data
          message_div.appendChild(text);

          section.appendChild(message_div);
          console.log('respond append')
          console.log(event.data)
        }
      } else if (event.data instanceof Blob) {
        // Read bytes
        const blob = event.data;
        // Create url
        const imageUrl = URL.createObjectURL(blob);
        // Create element for image
        const bot_img = document.getElementById('bot_img') as HTMLImageElement;
        if (bot_img) {
          bot_img.src = imageUrl;
        }
        // console.log(123)
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

      var section = document.getElementById("messages-chat");
      // Dynamically add elements
      if (section) {
        var message_div = document.createElement("div");
        message_div.className = 'message-text-only'

        var text = document.createElement("p");
        text.className = 'text-only'
        text.innerText = inputValue
        message_div.appendChild(text);

        var photo = document.createElement("img");
        photo.className = 'user_photo'
        photo.src = user
        message_div.appendChild(photo);

        section.appendChild(message_div);
        section.scrollTop = section.scrollHeight;
        console.log('append')
      }
    }
  }

  return (
    <div className="container">
      <section id='div' className='chat'>
        <section id='messages-chat' className='messages-chat'>
          <div className='message'>
            <img className='photo' src={chatbot}></img>
            <img className='bot_img' id='bot_img' src={loading} style={{ maxWidth: '30%', height: 'auto' }}></img>
          </div>
        </section>
      </section>

      <div className="footer-chat">
        <form className="write-message-form" onSubmit={sendMessage}>
          <input
            className="write-message"
            type='text'
            placeholder="Type your message here"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            autoComplete='off'
          />
          <button className='send' type='submit'>
            <img src={send}/>
          </button>
        </form>
      </div>
    </div>
  )
}


          // <i class="icon fa fa-smile-o clickable" style="font-size:25pt;" aria-hidden="true"></i>
          // <input type="text" class="write-message" placeholder="Type your message here"></input>
          // <i class="icon send fa fa-paper-plane-o clickable" aria-hidden="true"></i>
        


export default Chat
