import { ref } from 'vue'

export function useChatEngine() {
  const chatHistory = ref([])
  const isThinking = ref(false)
  
  // A simple session ID so Frappe knows which database record to append to
  const sessionId = ref(null) 

  const sendMessage = async (userText) => {
    if (!userText.trim()) return

    // 1. Instantly push the user's message to the UI
    chatHistory.value.push({ role: 'user', text: userText })
    isThinking.value = true

    try {
      // 2. Call our Python Master Controller
      // Note: In Frappe, the window object usually has the `frappe.call` method globally available
      const response = await window.frappe.call({
        method: 'erpnext_gemini_integration.api.master_controller.process_user_message',
        args: {
          user_message: userText,
          session_id: sessionId.value 
        }
      })

      const data = response.message

      if (data.status === 'success') {
        // Save the session ID so follow-up questions stay in the same thread
        if (!sessionId.value) sessionId.value = data.session_id

        // 3. Push the AI's response and any dynamic data to the UI
        chatHistory.value.push({
          role: 'model',
          text: data.reply,
          render_type: data.render_type, 
          data: data.render_data, 
          raw_sql: data.raw_sql
        })
      } else {
        throw new Error(data.error || "Backend returned an unknown error.")
      }

    } catch (error) {
      console.error("AI Engine Error:", error)
      chatHistory.value.push({
        role: 'model',
        text: "I ran into a glitch trying to pull that data. Could this database *be* any more stubborn? Try rephrasing it."
      })
    } finally {
      isThinking.value = false
    }
  }

  return {
    chatHistory,
    isThinking,
    sendMessage
  }
}