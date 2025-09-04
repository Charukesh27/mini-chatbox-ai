const chatWindow = document.getElementById("chatWindow");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const userIdInput = document.getElementById("userId");
const loadHistoryBtn = document.getElementById("loadHistory");

function addBubble(text, sender="bot"){
  const div = document.createElement("div");
  div.className = `bubble ${sender === "user" ? "user-msg" : "bot-msg"}`;
  div.innerText = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(){
  const text = input.value.trim();
  const user_id = (userIdInput.value || "guest").trim() || "guest";
  if(!text){ return; }
  addBubble(text, "user");
  input.value = "";

  try{
    const res = await fetch("/api/message", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message: text, user_id})
    });
    const data = await res.json();
    if(data.ok){
      addBubble(data.reply, "bot");
    }else{
      addBubble("Error: " + (data.error || "Unknown"), "bot");
    }
  }catch(err){
    addBubble("Network error. Please try again.", "bot");
  }
}

async function loadHistory(){
  const user_id = (userIdInput.value || "guest").trim() || "guest";
  chatWindow.innerHTML = "";
  try{
    const res = await fetch(`/api/history?user_id=${encodeURIComponent(user_id)}`);
    const data = await res.json();
    if(data.ok){
      data.history.forEach(item => addBubble(item.text, item.sender));
      if(data.history.length === 0){
        addBubble("No history yet. Say hi! 👋", "bot");
      }
    }
  }catch(e){
    addBubble("Could not load history.", "bot");
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e)=>{
  if(e.key === "Enter"){ sendMessage(); }
});
loadHistoryBtn.addEventListener("click", loadHistory);

// Initial greeting
addBubble("Hello! I’m Mini Chatbox AI. Type something to get started ✨", "bot");
